# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)





class SaleOrder(models.Model):
    
    _inherit = 'sale.order'
    
    
    partner_contact_id = fields.Many2one(
        'res.partner', string='Kapcsolattartó',
        readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'sale': [('readonly', False)]},
        domain="[('parent_id', '=', partner_id)]",)
    quotation_str1 = fields.Html(u'Ajánlat szöveg 1', default="""
        <strong>Tisztelt Hölgyem/Uram!</strong><br/>
        <br/>
        A megkeresésükre hivatkozva, amelyet ezúttal is köszönünk, az alábbiakban ajánlatot adunk AERMEC gyártmányú berendezésekre.<br/>
        <br/>
        <strong>
            1. Szállítási áraink<br/>
            Az ajánlott berendezések árai az alább részletezett szállítási terjedelemmel és műszaki tartalommal:<br/>
        </strong>
        <br/>
    """)
    quotation_str2 = fields.Html(u'Ajánlat szöveg 2', default="""
        <strong>Az ajánlott berendezések részletezését lásd a melléklet adatlapokon.</strong><br/>
        <br/>
        <ul>
            <li>Szállítás és az árú átvétele alapesetben a központi raktárunkban történik. Amennyiben az áraink nettó 3 000 000 Ft vásárlási értéket meghaladják, akkor tartalmazzák a szállítást a Megrendelő telephelyére, az alábbi 4. pontban részletezettek szerint. Raktárunkból való helyszínre szállítás átfutási ideje további 2-3 nap.</li> 
            <li>Az ajánlatunk az üzembe helyezési díjakat az alábbi 5. pontban részletezettek szerint tartalmazza</li>
        </ul>
        <br/>
        <strong>2. Garnciális ajánlat</strong><br/>
        A berendezésekre, az átvételtől számított 24 hónapra kiterjedő garanciát vállalunk,  amennyiben a beüzemelés általunk felhatalmazott márkaszerviz végzi és az üzemeltetés a műszaki leírásnak és a kezelési utasításnak megfelelően történik.<br/>
        <br/>
        Garanciális kötelezettségünk megszűnik, ha az átadott berendezésen, vagy annak beállításán illetéktelen személy, előzetes írásbeli engedélyünk nélkül, változtatásokat hajt végre, illetve engedély nélkül beüzemeli, feszültség alá helyezi, hűtőközeg oldali bármilyen szerelést, beavatkozást végez, beleértve a nem megfelelő csővezetékek szerelését osztott rendszerű berendezéseknél. A vízzel működő berendezések elfagyása esetén történő károsodás nem tartozik a garanciális vállalásunk alá, ugyanis a berendezés rendeltetés szerinti használatához hozzátartozik a fagyvédelem biztosítása a felhasználó részéről.<br/>
        <br/>
        A 24 hónapos garancia feltétele, hogy minden hűtési, hőszivattyúknál fűtési, időszak megkezdése előtt a leszállított berendezéseket AERMEC márkaszerviz a rendes karbantartás keretében átvizsgálja, megtisztítsa, a szükséges karbantartási munkálatokat elvégezze, és tevékenységét jegyzőkönyvbe foglalja. Ezen munkálatok nem tartoznak a garanciális vállalás alá, elmaradása esetén a garanciális időszak 12 hónapra módosul. A garancia nem vonatkozik a rendeltetés szerinti használat során szükségszerűen elhasználódó berendezésekre és alkatrészekre.<br/>
        <br/>
        Garanciális feltételként, és a biztonságos üzemeltetés végett beüzemelés szükséges minden folyadékhűtő, légkezelő, hőszivattyú, hűtőközeget tartalmazó egyéb berendezés, párásító, ipari párátlanító esetében.<br/>
        <br/>
        <strong>3. Szállítási határidő</strong><br/>
        <ul>
            <li>folyadékhűtőre kb. 6-7 hét a megrendelés érvénybelépésétől számítva,</li>
            <li>fan coilok kb. 3-5 hét a megrendelés érvénybelépésétől számítva,</li>
            <li>légkezelők kb. 6-8 hét a megrendelés érvénybelépésétől számítva,</li>
        </ul>
        A szállítási határidőket standard időszakra adtuk meg, rátartással, a projekt tervezhetősége miatt. A szállítási határidő előzetes pontos termékegyeztetés esetén lényegesen rövidebb lehet. Az előszállítás jogát fenntartjuk. A gyár augusztusi és decemberi zárva tartása miatt ezeket az időszakokat a határidőbe nem tudjuk beszámítani, kérjük ezt figyelembe venni.<br/>
        <br/>
        <strong>4. Házhoz szállítás az ajánlatunk szerint a következőket tartalmazza</strong><br/>
        <ul>
            <li>a díjmentes házhoz szállítás nettó 3 000 000 Ft vásárlási értékhatár fölött érvényes</li>
            <li>a házhoz szállítás előtt szükséges kitölteni a „Szállítási megrendelőt”, amely letölthető honlapunkról (www.oktoklima.hu Letöltések menüpont alól, legalább egy héttel korábban a kiszállítás időpontját megelőzően</li>
            <li>a házhoz szállítást logisztikai partnerünkkel szervezzük, 1-3 napos határidővel, munkanapokon</li>
            <li>a szállítmány fogadása, és a lerakodás a megrendelő feladata, és saját felelősségére történik</li>
            <li>a daruzandó nagyobb készülékeket, folyadékhűtőket stb. az import szállító gépkocsi helyszínre irányításával biztosítjuk, előzetes egyeztetéssel</li>
            <li>részszállításokat kizárólag minimum 3 000 000 Ft- os értékű bontásokban vállaljuk</li>
            <li>amennyiben az átvétel/átadás a Megrendelő hibájából meghiúsul, az árut raktárunkba visszaszállítjuk, és a további kiszállítások a Megrendelő költségére, és felelősségére történik</li>
            <li>amennyiben behajtási engedély, útvonalterv, vagy bármilyen helyszíni a szállítással összefüggő díjfizetés szükséges, azt a Megrendelő intézi, és fizeti</li>
            <li>nettó 3 000 000 Ft vásárlási értékhatár alatt kedvezményes házhoz szállítást tudunk biztosítani akár raklapon, akár futárszolgálattal, egyedi egyeztetés alapján</li>
        </ul>
        <br/>
        <strong>5. Beüzemelés részletezése</strong><br/>
        Beüzemelést csak a garancia feltételeknél részletezett berendezéseknél szükséges elvégezni. A beüzemelés nem tartalmazza a kiszállást, amelyet külön felszámítunk, a helyszíntől függően.<br/>
        <br/>
        Folyadékhűtők esetén:<br/>
        A beüzemelés során a szakszerviz elvégzi a következő műveleteket:<br/>
        <ul>
            <li>az elektromos bekötéseket elvégzik a helyi elektromos szerelő közreműködésével</li>
            <li>a folyadékhűtő üzemelési paramétereinek a beállítását</li>
            <li>a berendezés elindítását</li>
            <li>ellenőrzik a működést, védelmi elemeket, áramfelvételeket, gázoldali nyomásviszonyokat stb.</li>
            <li>beüzemelési jegyzőkönyvet készítenek</li>
            <li>érvényesítik a garanciajegyet</li>
        </ul>
        <br/>
        Építőelemes légkezelők esetén továbbá::<br/>
        <ul>
            <li>ventilátor motor áramfelvételek ellenőrzése</li>
            <li>ventilátor forgási irány ellenőrzése</li>
            <li>légszállítások ellenőrzése</li>
            <li>ékszíjak ellenőrzése</li>
        </ul>
        <br/>
        AZ ÜZEMBE HELYEZÉS MEGKEZDÉSE ELŐTT A MEGRENDELŐNEK KÖVETKEZŐ FELTÉTELEKET KELL BIZTOSÍTANI:<br/>
        <ul>
            <li>visszaküldi számunkra, vagy szervizpartnerünknek, a beüzemelés megrendelése lapot kitöltve (amelyet a berendezés garancialevele mellett a készülékhez biztosítunk, vagy letölthető honlapunkról a www.oktoklima.hu Letöltések menüpont alól)</li>
            <li>gépészetileg a berendezés teljesen készre szerelt, a hűtési (fűtési) teljesítmény felvétele biztosított</li>
            <li>a folyadékhűtő vagy légkezelő kiszolgáló berendezései elektromosan készre szereltek</li>
            <li>a berendezés műszaki adatsorában szereplőek szerinti elektromos betáp-kábel a helyszínen biztosított (nincs bekötve!)</li>
            <li>épületfelügyeleti rendszerhez való csatlakozás beüzemelése nem része az ajánlatunknak</li>
            <li>a berendezés eredeti dokumentációja a helyszínen biztosítva van (Pl. a berendezéssel szállított elektromos rajzok)</li>
        </ul>
        Osztott rendszerű folyadékhűtők hűtőközeg vezetékeinek tervezése, szerelése és splitek szerelése nem része ajánlatunknak.<br/>
        <br/>
        A beüzemelési díjunk továbbá nem tartalmazza a 310/2008 (XII:20.) Korm. rendelet szerinti kötelező szivárgásvizsgálat elvégzését. Amennyiben a kötelező szivárgásvizsgálatot nem a beüzemelőtől kívánja megrendelni, akkor ezt írásban kérjük jelezze felénk.<br/>
        <br/>
        Amennyiben az üzembe-helyezés a megrendelő hibájából nem valósul meg, vagy a berendezés nincs olyan állapotban, hogy biztonságosan, a berendezés állagát nem veszélyeztetve beüzemelhető legyen, akkor a meghiúsult beüzemelési kiszállás díját érvényesítjük, és kiszámlázzuk.<br/>
        <br/>
        <strong>6. Minőség</strong><br/>
        Minden AERMEC berendezés, a végellenőrzést megelőzően, már az alkatrészeinek a részgyártása különösen gondos ellenőrzésen esik át. Ezáltal garantálható, hogy már az alkatrészek is megfelelnek a magas minőségi követelményeknek, és nem kell attól tartani, hogy a már összeszerelt végtermék ellenőrzéskor kiderül, valamelyik komponens nem megfelelő.<br/>
        <br/>
        Fan coilokat magasan automatizált gyártósorokon illetve robotok gyártják, szerelik össze, és csomagolják. Ennek megfelelően nagyon kicsi a valószínűsége a hibás készülék gyártásának. Az Európában egyedülálló robotizált gyártósor, állandó jó minőségű végterméket, gyors szállítási határidőt és nagyobb gyártási kapacitást jelent.<br/>
        <br/>
        A folyadékhűtők és hőszivattyúk  az összeszerelést követően próbaüzemen is átesnek.<br/>
        A 30 kW- nál kisebb teljesítményűeket 1 órán keresztül üzemeltetik névleges körülmények közt, vízzel feltöltött állapotban.<br/>
        A közepes teljesítményű berendezéseket a 30-150 kW köztieket 8 órát üzemeltetik, míg az ennél nagyobb berendezéseket 24 órát!<br/>
        Természetesen a hőszivattyús változatokat ugyanennyi ideig fűtő üzemmódban is tesztelik.<br/>
        Addig egyetlen folyadékhűtő berendezés sem hagyhatja el a gyárat, amíg a próbaüzemen át nem esett.<br/>
        Ezáltal teljességgel megbizonyosodik, hogy a berendezés nem csak hogy működőképes, hanem a névleges adatok szerinti zaj, elektromos, kalorikus tulajdonságokkal rendelkeznek.<br/>
        A klímatechnikai gyártók közt a legaprólékosabb minőség ellenőrzésével rendelkező AERMEC gyár minősége ezáltal a legmagasabb kategóriába sorolja a termékeket.<br/>
        <br/>
        <strong>7. Tervezés</strong><br/>
        Az ajánlatunk nem tartalmazza a berendezések telepítéséhez szükséges semmilyen tervdokumentáció elkészítését, és a tervezést nem helyettesíti. Az ajánlatunkat a rendelkezésünkre bocsátott műszaki adatok figyelembevételével állítottuk össze. Amennyiben változások történnek, kérjük, értesítsenek, hogy az ajánlatunkat aktualizálhassuk. A berendezések hibás alkalmazásából, ill. rendszerbe építéséből adódó károkért nem vállalunk felelősséget.<br/>
        <br/>
        <strong>8. Vállalási feltételek</strong><br/>
        <ul>
            <li>Az ajánlatban nem szabályzott kondíciók az "Oktoklima Kft. Általános Szerződési Feltételei"- ben rögzítettek szerint érvényesek</li>
            <li>Az ajánlatunk szerinti Megrendelést az ajánlatban szereplő kondíciók és az Általános Szerződési Feltételek elfogadásának tekintjük, és a továbbiakban Szállítási Szerződésként kezeljük.</li>
            <li>A Megrendelés amennyiben külön megállapodás nem született, az előleg megérkezésének dátumától érvényes (megrendelés érvénybe lépése).</li>
            <li>amennyiben a Megrendelő a szállítást az ajánlatunkban foglaltaktól eltérő kondíciókkal rendeli meg, az eltéréseket csak írásos visszaigazolás esetében tekintjük elfogadottnak</li>
            <li>Az áru megérkezésének írásos kiértesítésétől számított 15. nap után az át nem vett berendezésekre vonatkozó kárveszély a Megrendelőre száll, továbbá raktározási költséget számolunk fel, amelynek mértéke minimum az áru nettó értékének 1 %- a vagy 100 FT/m2/nap+Áfa, a nagyobbik érték szerint. A díj kiszabásánál az áru tárolási alapterülete a mértékadó, vagy legalább 1 m2, amennyiben az alapterülete kevesebb mint 1 m2. A raktározási költség az előszállítási időszakra nem vonatkozik.</li>
            <li>Amennyiben a berendezéseket a szállítási határidő lejárta után, és a kiértesítést követő 30 napon belül a Megrendelő nem vette át, úgy tekintjük, hogy elállt a szerződéstől, és kiszámlázzuk a bánatpénzt.</li>
            <li>Az árú minőségi és mennyiségi írásos átvétele Budapesten az Oktoklíma Kft. telephelyén ill. raktárából.</li>
            <li>A Ptk. 368.§-ában foglaltaknak megfelelően szerződés szerinti vételár teljes kiegyenlítéséig a leszállított berendezések az Oktoklíma Kft. tulajdonában maradnak, azokat a Megrendelő nem adhatja el, nem rendelkezhet róluk, nem üzemeltetheti be, és nem üzemeltetheti. A Megrendelő ezennel feljogosítja Oktoklíma Kft.-t, hogy a fizetési határidő leteltét követően a tulajdonjog fenntartás alapján a Megrendelő által ki nem fizetett árut a Megrendelő telephelyéről, raktárából, stb. elszállítsa. Ha a késedelmes fizetés miatt Szállítónak költségei keletkeznek például behajtás, bírósági eljárás vagy egyéb költségek, ezt a Megrendelő köteles viselni.</li>
            <li>Az átvétel után a berendezések őrzése és szakszerű tárolása a Megrendelő feladata, az ebből eredő károkra és meghibásodásokra felelősséget nem vállalunk.</li>
        </ul>
        <br/>
        <strong>9. Szerződésszegés esetén alkalmazandó szabályok</strong><br/>
        <ul>
            <li>Aki a szerződést megszegi, kártérítési felelősséggel tartozik, kivéve, ha bizonyítja, hogy a szerződés teljesítése érdekében úgy járt el, ahogy a gazdálkodó szervezettől az adott helyzetben általában elvárható.</li>
            <li>A szerződésszegés következményei alól nem mentesít az a körülmény, hogy a szerződésszegést a gazdálkodó szervezet irányítására, felügyeletére jogosult szerv intézkedése okozta.</li>
            <li>A Szállító a berendezés gyártójának bármely akadály közlését jogosult és köteles a Megrendelő tudomására hozni a gyártó által közölt szállítási határidő megjelölésével, amely a szerződést módosítja.</li>
            <li>A szerződésben nem érintett kérdésekben a PTK rendelkezéseit kell alkalmazni.</li>
            <li>Felek a szerződéssel kapcsolatos esetleges vitáikat törekednek békés egyeztetés útján rendezni, amennyiben ez sikertelen, úgy a hatáskörrel és illetékességgel rendelkező rendes bírósághoz fordulnak.</li>
            <li>Ha a Szerződés bármely olyan oknál fogva, amely nem a Szállító magatartására vezethető vissza, meghiúsul, vagy Megrendelő a megvalósítástól eláll, illetve csökkentett értékű megvalósítást határoz el, akkor Szállító jogosult az elállással (meghiúsulással) érintett szerződési összegre vetített 20 % bánatpénz érvényesítésére, valamint az előleg vissza nem térítésére.</li>
            <li>Fizetési késedelem esetén a 2013.V. törvény, vagyis a  TK. 6:155. § szerint járunk el:<br/>
                (1) Vállalkozások közötti szerződés, valamint pénztartozás fizetésére kötelezett szerződő vállalkozással kötött szerződése esetén a késedelmi kamat mértéke a késedelemmel érintett naptári félév első napján érvényes jegybanki alapkamat - idegen pénznemben meghatározott pénztartozás esetén az adott pénznemre a kibocsátó jegybank által meghatározott alapkamat, ennek hiányában a pénzpiaci kamat - nyolc százalékponttal növelt értéke. A kamat számításakor a késedelemmel érintett naptári félév első napján érvényes jegybanki alapkamat irányadó az adott naptári félév teljes idejére.<br/>
                (2) Ha vállalkozások közötti szerződés esetén a kötelezett, vállalkozással kötött szerződése esetén a szerződő fizetési késedelembe esik, köteles a jogosultnak a követelése behajtásával kapcsolatos költségei fedezésére negyven eurónak a Magyar Nemzeti Bank késedelmi kamatfizetési kötelezettség kezdőnapján érvényes hivatalos deviza-középárfolyama alapján meghatározott forintösszeget megfizetni. E kötelezettség teljesítése nem mentesít a késedelem egyéb jogkövetkezményei alól; a kártérítésbe azonban a behajtási költségátalány összege beszámít. A behajtási költségátalányt kizáró, vagy azt negyven eurónál alacsonyabb összegben meghatározó szerződési kikötés semmis.<br/>
                (4) Vállalkozások közötti szerződés esetén a késedelmi kamatot kizáró szerződési feltétel, szerződő hatóságnak szerződő hatóságnak nem minősülő vállalkozással kötött szerződése esetén a késedelmi kamatot kizáró vagy azt az (1) bekezdésben meghatározott mértékhez képest alacsonyabb értékben meghatározó szerződési feltétel semmis, kivéve, ha a kötelezett késedelme esetére kötbér fizetésére köteles.</li>
            <li>Tartós nemfizetés esetén az Oktoklíma Kft. a követelést átadja követeléskezelő partnereinek. Ha a kérdéses kötelezettség az Oktoklima Kft.-től a követelésbehajtó partnereihez kerül át a PTK szerinti behajtásra, a követelésbehajtás költségei a nem fizető ügyfelet terhelik, amely a követelésbehajtó partner által kibocsátott számlán jelennek meg terhelésként.</li>
            <li>A Megrendelő hozzájárul ahhoz, hogy a számla lejáratától számított 90 napon túli nem fizetés esetén a Szállító inkasszó igényt nyújtson be a fent jelölt banknál vezetett bankszámlájára. Ezzel Megrendelő felhatalmazza a számlavezető bankját, hogy Oktoklíma Kft.-val szembeni tartozás erejéig számláját inkasszóval terheljék.</li>
        </ul>
        <br/>
        Az ajánlatunkkal kapcsolatban felmerülő kérdések esetén készséggel rendelkezésükre állunk. Az ajánlatunkat a rendelkezésünkre bocsátott műszaki adatok szerint, a terv és helyszín ismerete nélkül, állítottuk össze, amennyiben változások történnek, kérjük, jelezzék felénk!<br/>
        <br/>
    """)


    def wizard_merge_into_product(self):
        
        context = {}
        context['default_order_id'] = self.id
        
        return {
            'name'      : u'Új termék létrehozása termékekből',
            'type'      : 'ir.actions.act_window',
            'res_model' : 'sale.order.product.wizard',
            'view_id'   : self.env.ref('oktoklima.sale_order_product_wizard_view_form').id,
            'view_type' : 'form',
            'view_mode' : 'form',
            'target'    : 'new',
            'context'   : context,
        }



class SaleOrderLine(models.Model):
    
    _inherit = 'sale.order.line'
    
    
    supplierinfo_popover = fields.Text(u'Supplierinfo PopOver', compute='_supplierinfo_popover', readonly=True)
    
    
    @api.depends('product_id')
    def _supplierinfo_popover(self):
        for line in self:
            supplierinfo_popover = ''
            for s in line.product_id.seller_ids:
                supplierinfo_popover += str(s.price) + ' ' + str(s.currency_id.name) + ' (' + str(s.name.name) + ')\n'
            line.supplierinfo_popover = supplierinfo_popover





class SaleOrderProductWizard(models.TransientModel):
    
    _name = 'sale.order.product.wizard'
    
    
    name = fields.Char(u'Új termék neve', required=True)
    default_code = fields.Char(u'Új termék cikkszáma', required=True)
    order_id = fields.Many2one('sale.order', u'Árajánlat', required=True)
    list_price = fields.Float(u'Eladási ár', compute='_compute')
    standard_price = fields.Float(u'Beszerzési ár', compute='_compute')
    line_ids = fields.Many2many('sale.order.line', 'merge_product_rel', 'wizard_id', 'line_id', string='Sorok' , domain="[('order_id', '=', order_id),('product_id.product_tmpl_id.configured_product', '=', False)]")
    
    
    @api.model
    def default_get(self, fields):
        
        vals = super(SaleOrderProductWizard, self).default_get(fields)
        vals['line_ids'] = self.env['sale.order.line'].search([('order_id', '=', self._context.get('active_ids')[0]),('product_id.product_tmpl_id.configured_product', '=', False)]).ids
        return vals


    @api.depends('line_ids')
    @api.onchange('line_ids')
    def _compute(self):
        list_price = 0
        standard_price = 0
        for line in self.line_ids:
            list_price += line.product_id.list_price
            standard_price += line.product_id.standard_price
        self.list_price = list_price
        self.standard_price = standard_price


    def action_create_product(self):
        
        ProductTemplate = self.env['product.template'].create({
            'name': self.name,
            'default_code': self.default_code,
            'list_price': self.list_price,
            'standard_price': self.standard_price,
            'configured_product': True
        })
        ProductProduct = self.env['product.product'].search([('product_tmpl_id', '=', ProductTemplate.id)], limit=1)
        for line in self.line_ids:
            self.env['product.template.configured.component'].create({
                'product_tmpl_id': ProductTemplate.id,
                'product_comp_id': line.product_id.product_tmpl_id.id,
                'qty': line.product_uom_qty
            })
            line.unlink();
        
        self.env['sale.order.line'].create({
            'order_id': self.order_id.id,
            'product_id': ProductProduct.id,
        })