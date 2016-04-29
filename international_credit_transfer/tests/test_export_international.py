# -*- encoding: utf-8 -*-
##############################################################################
#
#    International Credit Transfer module for OpenERP
#    Copyright (C) 2016 Savoir-faire Linux
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.addons.account_banking_tests.tests import (
    test_payment_roundtrip)


class TestExportInternational(test_payment_roundtrip.TestPaymentRoundtrip):
    def setup_payment_config(self, reg, cr, uid):
        """
        Configure an additional account and journal for payments
        in transit and configure a payment mode with them.
        """
        account_parent_id = reg('account.account').search(
            cr, uid,
            [
                ('company_id', '=', self.company_id),
                ('parent_id', '=', False)
            ])[0]
        user_type = reg('ir.model.data').get_object_reference(
            cr, uid, 'account', 'data_account_type_liability')[1]
        transfer_account_id = reg('account.account').create(
            cr, uid,
            {
                'company_id': self.company_id,
                'parent_id': account_parent_id,
                'code': 'TRANS',
                'name': 'Transfer account',
                'type': 'other',
                'user_type': user_type,
                'reconcile': True,
            })
        transfer_journal_id = reg('account.journal').search(
            cr, uid, [
                ('company_id', '=', self.company_id),
                ('code', '=', 'MISC')
            ])[0]
        self.bank_journal_id = reg('account.journal').search(
            cr, uid, [
                ('company_id', '=', self.company_id),
                ('type', '=', 'bank')
            ])[0]

        payment_mode_type_id = self.ref(
            'international_credit_transfer.'
            'export_international_pain_001_001_03')

        self.payment_mode_id = reg('payment.mode').create(
            cr, uid,
            {
                'name': 'International Payment Mode',
                'bank_id': self.partner_bank_id,
                'journal': self.bank_journal_id,
                'company_id': self.company_id,
                'transfer_account_id': transfer_account_id,
                'transfer_journal_id': transfer_journal_id,
                'type': payment_mode_type_id,
            })

    def export_payment(self, reg, cr, uid):
        export_model = reg('banking.export.international.wizard')
        export_id = export_model.create(
            cr, uid, {}, context={'active_ids': [self.payment_order_id]})

        export_model.process_payment(
            cr, uid, [export_id])
        export_model.save_payment(
            cr, uid, [export_id])
        self.assert_payment_order_state('sent')
        self.assert_invoices_state('paid')

    def test_payment_roundtrip(self):
        reg, cr, uid, = self.registry, self.cr, self.uid
        # Tests fail if admin does not have the English language
        reg('res.users').write(cr, uid, uid, {'lang': 'en_US'})
        self.setup_company(reg, cr, uid)
        self.setup_chart(reg, cr, uid)
        self.setup_payables(reg, cr, uid)
        self.setup_payment_config(reg, cr, uid)
        self.setup_payment(reg, cr, uid)
        self.export_payment(reg, cr, uid)
        self.setup_bank_statement(reg, cr, uid)
        self.check_reconciliations(reg, cr, uid)
