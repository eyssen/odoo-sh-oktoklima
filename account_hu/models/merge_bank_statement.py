# -*- coding: utf-8 -*-
from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)





class MergeBankStatement(models.TransientModel):

    _name = 'account.merge.bank.statement'
    _description = 'Merge Bank Statements'


    name = fields.Char(u'Reference', required=True)
    statement_ids = fields.Many2many('account.bank.statement', 'merge_bank_statement_rel', 'merge_id', 'statement_id', string='Statements', domain="[('state', '=', 'open')]")


    @api.model
    def default_get(self, fields):
        record_ids = self._context.get('active_ids')
        result = super(MergeBankStatement, self).default_get(fields)
 
        if record_ids:
            if 'statement_ids' in fields:
                stmt_ids = self.env['account.bank.statement'].browse(record_ids).filtered(lambda stmt: stmt.state == 'open').ids
                result['statement_ids'] = stmt_ids
 
        return result


    @api.multi
    def action_merge(self):
        self.ensure_one()

        if len(self.statement_ids) > 1:
            stmt_id = None
            for stmt in self.statement_ids.sorted(key=lambda s: s.id):
                if not stmt_id:
                    stmt.name = self.name
                    stmt_id = stmt.id
                else:
                    lines = self.env['account.bank.statement.line'].search([('statement_id', '=', stmt.id)])
                    for line in lines:
                        line.statement_id = stmt_id
                    stmt.unlink()