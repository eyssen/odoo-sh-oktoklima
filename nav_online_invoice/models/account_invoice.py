# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _, tools
from lxml import etree
from lxml.etree import fromstring
import logging
import time
import math
import random
import re
import datetime
import hashlib
import requests
import io
from base64 import b64decode
from base64 import b64encode
from Crypto.Cipher import AES
import binascii

_logger = logging.getLogger(__name__)





class AccountMove(models.Model):
    
    _inherit = "account.move"


    nav_no = fields.Boolean(u'Nem kell átadni a NAV-nak!', help=u'Pl. ha a számla másik programban lett kiállítva és már korábban átadásra került a NAV-nak, stb.', copy=False)
    nav_no_reason = fields.Char(u'Az alábbiak miatt nem kellett átadni a NAV-nak: ', readonly=True, copy=False)
    nav_transaction_id = fields.Char(u'Nav tranzakciós azonosító', readonly=True, copy=False)
    nav_send_date = fields.Datetime(u'Nav beküldés ideje', readonly=True, copy=False)
    nav_send_result = fields.Char(u'Nav beküldés állapota', readonly=True, copy=False)
    nav_check_result = fields.Char(u'Nav feldolgozás állapota', readonly=True, copy=False)
    nav_message = fields.Char(u'Nav válasz', readonly=True, copy=False)
    nav_xml = fields.Text(u'Nav beküldött xml', readonly=True, copy=False)


    def action_post(self):
        ret = super(AccountMove, self).action_post()
        self.nav_send()
        return ret


    def nav_send(self):
        self.ensure_one()
        if self.state != 'posted':
            self.nav_no_reason = "Csak open vagy paid szamla kuldheto be"
            _logger.error("===== NAV: Csak open vagy paid szamla kuldheto be")
            return

        if not self.company_id.partner_id or not self.company_id.partner_id.vat_hu:
            self.nav_no_reason = "Partner adószáma kötelező"
            _logger.error("===== NAV: Partner adószáma kötelező")
            return

        if self.type not in ['out_invoice','out_refund']:
            self.nav_no_reason = "Csak kimenő számlákat küldünk a nav-nak"
            _logger.error("===== NAV: Csak kimenő számlákat küldünk a nav-nak")
            return

        if self.partner_id.company_type == 'person':
            self.nav_no_reason = "Magánszemélyt nem kell átadni"
            _logger.info("===== NAV: Magánszemélyt nem kell átadni")
            return
        
        if self.partner_id.company_type == 'company' and self.partner_id.country_id != self.company_id.partner_id.country_id:
            self.nav_no_reason = "Csak magyar cégek felé kiállított számlát kell átadni"
            _logger.info("===== NAV: Csak magyar cégek felé kiállított számlát kell átadni")
            return

        if self.nav_no == True:
            self.nav_no_reason = "Manuálisan beállítva: Nem kell átadni a NAV-nak!"
            _logger.error("===== NAV: Manuálisan beállítva: Nem kell átadni a NAV-nak!")
            return
        
        if not self.nav_check_result or self.nav_check_result == '' or self.nav_check_result == 'ABORTED':
            self.nav_message = ""
            token = self.requestExchangeToken()
            if token[0] == "Ok":
                decodedToken = self.decryptToken(token[1])
                invoice_xml = self.prepareInvoiceXml()

                if self.type=='out_invoice':
                    operation = "CREATE"
                if self.type=='out_refund':
                    operation = "STORNO"

                result = self.manageInvoice(decodedToken, invoice_xml, operation = operation)
                if result[0] == "Ok":
                    self.nav_transaction_id = result[1]
                    self.nav_send_date = datetime.datetime.now()
                    self.nav_send_result = "Beküldve"
                    self.nav_check()

                else:
                    _logger.error("NAV INVOICE SEND ERROR: " + result[1])
                    self.nav_send_result= "Beküldés hiba! " + result[1]
            else:
                _logger.error("NAV ERROR: " + token[1])
                self.nav_send_result= "Token kérés hiba! " + token[1]
        else:
            _logger.error("Mar be van kuldve")


    def nav_check(self):
        self.ensure_one()
        ret = ("", "")

        if not self.nav_transaction_id:
            ret = ("Err","No transaction id")
            #self.nav_check_result="Státusz ellenőrzés hiba!"
            self.nav_message = ret[1]
            return ret

        nav_api_url = self.company_id.nav_api_url

        request = self.baseXml('QueryTransactionStatusRequest')
        etree.SubElement(request, "transactionId").text = self.nav_transaction_id

        xml = self.getXmlString(request)
        
        response = self.makeRequest(nav_api_url + "/queryTransactionStatus", xml)
        if response.status_code == requests.codes.ok:
            root = self.parseXml(response.text)

            funcCode = root.find(".//funcCode")
            if funcCode.text.upper() == "OK":
                invoiceStatus  = root.find('.//invoiceStatus')
                message = root.find('.//message')
                self.nav_check_result = invoiceStatus.text
                if message != None:
                    self.nav_message = message.text
                ret = ("Ok", "")
            else:
                errorCode = root.find(".//errorCode")
                message = root.find(".//message")
                ret = ("Err", "ErrorCode: " + errorCode.text + " Message: " + message.text)
        else:
            ret = self.response(response)

        if ret[0] == "Err":
            #self.nav_check_result="Státusz ellenőrzés hiba!"
            self.nav_message = ret[1]

        return ret


    def nav_get(self):
        self.ensure_one()
        ret = ("","")
        if not self.nav_transaction_id:
            _logger.error("Nincs beküldve")
            self.nav_message = "nincs beküldve"
            return
        
        nav_api_url = self.company_id.nav_api_url

        request = self.baseXml('QueryInvoiceDataRequest')
        #etree.SubElement(request, "page").text = '1'
        invoiceQuery = etree.SubElement(request, "invoiceNumberQuery")
        etree.SubElement(invoiceQuery, "invoiceNumber").text = self.name
        etree.SubElement(invoiceQuery, "invoiceDirection").text = 'OUTBOUND'

        xml = self.getXmlString(request)
        
        response = self.makeRequest(nav_api_url + "/queryInvoiceData", xml)

        if response.status_code == requests.codes.ok:
            root = self.parseXml(response.text)
            invoice = root.find('.//invoiceData')
            self.nav_xml = b64decode(invoice.text)
        else:
            ret = self.response(response)

        if ret[0] == "Err":
            _logger.error(response.text)
            _logger.error(ret[1])
        

    def manageInvoice(self, token, invoice_xml, operation="CREATE"):
        ret = ("", "")
        nav_api_url = self.company_id.nav_api_url
        base64_invoice = b64encode(invoice_xml)

        request = self.baseXml('ManageInvoiceRequest', base64_invoice)
        etree.SubElement(request, "exchangeToken").text = token

        invoiceOperations = etree.SubElement(request, "invoiceOperations")
        etree.SubElement(invoiceOperations, "compressedContent").text = "false"

        invoiceOperation = etree.SubElement(invoiceOperations, "invoiceOperation")
        etree.SubElement(invoiceOperation, "index").text = "1"
        etree.SubElement(invoiceOperation, "invoiceOperation").text = operation
        etree.SubElement(invoiceOperation, "invoiceData").text = base64_invoice

        xml = self.getXmlString(request)

#         _logger.info("******************")
#         _logger.info(invoice_xml)
#         _logger.info("******************")

        response = self.makeRequest(nav_api_url + "/manageInvoice", xml)
        if response.status_code == requests.codes.ok:
            root = self.parseXml(response.text)

            funcCode = root.find(".//funcCode")
            if funcCode.text.upper() == "OK":
                transactionId  = root.find('.//transactionId')
                ret = ("Ok", transactionId.text)
            else:
                errorCode = root.find(".//errorCode")
                message = root.find(".//message")
                ret = ("Err", "ErrorCode: " + errorCode.text + " Message: " + message.text)
        else:
            ret = self.response(response)
        return ret


    def requestExchangeToken(self):
        ret = ("","")
        nav_api_url = self.company_id.nav_api_url

        request = self.baseXml('TokenExchangeRequest')
        xml = self.getXmlString(request)

        response = self.makeRequest(nav_api_url + "/tokenExchange", xml)
        if response.status_code == requests.codes.ok:
            root = self.parseXml(response.text)

            funcCode = root.find(".//funcCode")
            if funcCode.text.upper() == "OK":
                encodedExchangeToken = root.find('.//encodedExchangeToken')
                ret = ("Ok", encodedExchangeToken.text)
            else:
                errorCode = root.find(".//errorCode")
                message = root.find(".//message")
                ret = ("Err", "ErrorCode: " + errorCode.text + " Message: " + message.text)

        else:
            ret = self.response(response)
        return ret


    def decryptToken(self, token):
        exchangeKey = self.company_id.nav_exchange_key

        unpad = lambda s: s[:-ord(s[len(s) - 1:])]

        enc = b64decode(token)
        cipher = AES.new(exchangeKey, AES.MODE_ECB)
        return unpad(cipher.decrypt(enc)).decode('utf8')


    def makeRequest(self, url, xml):
        headers = {
            'Content-Type': 'application/xml;charset="UTF-8"',
            'Accept': 'application/xml'
        }
        r = requests.post(url, headers=headers, data=xml, timeout=5000)
#         _logger.info("******** Nav request header ********")
#         _logger.info(headers)
#         _logger.info("******** Nav request data ********")
#         _logger.info(xml)
        _logger.info("******** Nav response ********")
        _logger.info(r.content.decode('utf8'))
        return r


    def getXmlString(self, root):
        return etree.tostring(root, xml_declaration=True, encoding='utf-8')


    def baseXml(self, rootTag, base64_invoice = None):
        signKey = self.company_id.nav_sign_key

        root = etree.Element(rootTag, xmlns='http://schemas.nav.gov.hu/OSA/2.0/api')
        requestId = self.generateRequestId()
        timestamp = self.generateTimestamp()

        header = etree.SubElement(root, "header")
        etree.SubElement(header, "requestId" ).text = requestId
        etree.SubElement(header, "timestamp" ).text = timestamp
        etree.SubElement(header, "requestVersion").text = "2.0"
        etree.SubElement(header, "headerVersion").text = "1.0"

        user = etree.SubElement(root, "user")
        etree.SubElement(user, "login").text = self.company_id.nav_user
        etree.SubElement(user, "passwordHash").text = self.sha512(self.company_id.nav_pass)
        etree.SubElement(user, "taxNumber").text = str(self.company_id.partner_id.vat_hu.split('-')[0])
        etree.SubElement(user, "requestSignature").text = self.generateSignatureHash(requestId, timestamp, signKey, rootTag, base64_invoice)

        software = etree.SubElement(root, "software")
        etree.SubElement(software, "softwareId").text = "EYSSENODOO13-00001"
        etree.SubElement(software, "softwareName").text = "eYssen Odoo"
        etree.SubElement(software, "softwareOperation").text = "ONLINE_SERVICE"
        etree.SubElement(software, "softwareMainVersion").text = "13.0.2.0"
        etree.SubElement(software, "softwareDevName").text = "eYssen IT Services"
        etree.SubElement(software, "softwareDevContact").text = "info@eyssen.hu"
        etree.SubElement(software, "softwareDevCountryCode").text = "HU"
        etree.SubElement(software, "softwareDevTaxNumber").text = "14225433-2-41"

        return root


    def generateRequestId(self):
        id = "RID" + '%f %d' % math.modf(time.time()) + str(random.randint (10000, 99999))
        id = re.sub(r'[^A-Z0-9]', r'', id)
        return id[0:30]
    
    
    def generateTimestamp(self):
        dt = datetime.datetime.now();
        return dt.isoformat()[0:-3] + "Z"


    def generateSignatureHash(self, requestId, timestamp, signKey, rootTag, base64_invoice = None):
        signature = requestId
        signature = signature + re.sub(r'\.\d{3}|\D+', r'', timestamp)
        signature = signature + signKey

        if rootTag == "ManageInvoiceRequest":
                if self.type=='out_invoice':
                    signature = signature + self.sha3512('CREATE' + base64_invoice.decode('UTF-8'))
                if self.type=='out_refund':
                    signature = signature + self.sha3512('STORNO' + base64_invoice.decode('UTF-8'))

        return self.sha3512(signature)
    
    
    def sha512(self, string):
        return hashlib.sha512(string.encode('utf-8')).hexdigest().upper()


    def sha3512(self, string):
        return hashlib.sha3_512(string.encode('utf-8')).hexdigest().upper()


    def parseXml(self, xml):
        xml = re.sub(r"""\s(xmlns="[^"]+"|xmlns='[^']+')""", '', xml, count=1)
        xml = xml.encode('utf-8')
        parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
        tree = etree.parse(io.BytesIO(xml), parser=parser)
        return tree.getroot()


    def prepareInvoiceXml(self):
        report_object = self.env['ir.actions.report']
        report_name = 'nav_online_invoice.nav_online_invoice_report_xml_view'
        report = report_object._get_report_from_name(report_name)
        docs = [self.id]

        if self.type=='out_refund' and self.refund_invoice_id:
            docs = docs + [self.refund_invoice_id.id]

        rep = report.render(docs, {})
        invoice = etree.fromstring(rep[0])
        xml = self.getXmlString(invoice)

        xml = re.sub(r'data-oe-id="[^\"]*"', '', xml.decode('utf-8'))
        xml = re.sub(r'data-oe-xpath="[^\"]*"', '', xml)
        xml = re.sub(r'data-oe-model="[^\"]*"', '', xml)
        xml = re.sub(r'data-oe-field="[^\"]*"', '', xml)

#         _logger.info("INVOICE XML ******************")
#         _logger.info(xml)
#         _logger.info("/INVOICE XML ******************")

        return xml.encode()


    def response(self, response):
        msg = "Http Error, NAV server is down?" + str(response.status_code)
        root = self.parseXml(response.text)
        if root:
            message = root.find(".//message")  or root.find(".//{http://schemas.nav.gov.hu/OSA/2.0/api}message")
            if message != None:
                msg = msg + message.text
        ret = ("Err", msg)
        return ret


    def nav_check_processing(self):
        for Invoice in self.env['account.move'].search([('nav_check_result', '!=', 'DONE')]):
            _logger.info('Check not DONE Invoice: ' + str(Invoice.name))
            Invoice.nav_check()
