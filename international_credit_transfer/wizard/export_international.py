# -*- encoding: utf-8 -*-
##############################################################################
#
#    SEPA Credit Transfer module for OpenERP
#    Copyright (C) 2010-2013 Akretion (http://www.akretion.com)
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
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

import base64
import logging

from collections import defaultdict
from datetime import datetime
from lxml import etree

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp import netsvc, tools


logger = logging.getLogger(__name__)


class XmlGeneratorInternational(object):
    """
    Xml generator for international credit transfers under the
    standard pain.001.001.03
    """

    def __init__(self, cr, uid, wizard, context=None):
        if context is None:
            context = {}

        self.cr = cr
        self.uid = uid
        self.context = context

        self.pain_flavor = 'pain.001.001.03'

        self.file_obj = wizard.pool['banking.export.international']
        self.pain_xsd_file = (
            'international_credit_transfer/data/%s.xsd' %
            self.pain_flavor)

        self.wizard = wizard
        self.root_xml_tag = 'CstmrCdtTrfInitn'

        self.payment_order = self.wizard.payment_order_ids[0]
        self.company = self.payment_order.company_id
        self.reference = self.payment_order.reference

        self.debtor_bank = self.payment_order.mode.bank_id

        self.debtor_bank_name = self.debtor_bank.partner_id.name[0:70]
        self.debtor_account_number = self.wizard.validate_iban(
            self.debtor_bank.acc_number)

        self.debtor_bic = self.debtor_bank.bank.bic

        self.initiating_party_country_code = self.debtor_account_number[0:2]

        self.total_amount = sum(
            order.total for order in wizard.payment_order_ids)

    def generate(self):
        pain_ns = {
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            None: 'urn:iso:std:iso:20022:tech:xsd:%s' % self.pain_flavor,
        }

        self.xml_root = etree.Element('Document', nsmap=pain_ns)
        pain_root = etree.SubElement(self.xml_root, self.root_xml_tag)

        self.generate_group_header_block(pain_root)

        lines_per_group = self.group_payment_lines()

        for (requested_date, priority), lines in lines_per_group.items():
            self.generate_start_payment_info_block(
                pain_root, requested_date, priority, lines)

        self.xml_string = etree.tostring(
            self.xml_root, pretty_print=True, encoding='UTF-8',
            xml_declaration=True)

    def generate_group_header_block(self, parent_node):
        header_node = etree.SubElement(parent_node, 'GrpHdr')

        message_identification_1_1 = etree.SubElement(header_node, 'MsgId')
        message_identification_1_1.text = self.payment_order.reference[0:35]

        creation_date_time_1_2 = etree.SubElement(header_node, 'CreDtTm')
        creation_date_time_1_2.text = datetime.strftime(
            datetime.today(), '%Y-%m-%dT%H:%M:%S')

        transactions_count_1_6 = 0
        amount_control_sum_1_7 = 0

        for payment_order in self.wizard.payment_order_ids:
            for line in payment_order.line_ids:
                transactions_count_1_6 += 1
                amount_control_sum_1_7 += line.amount_currency

        nb_of_transactions_1_6 = etree.SubElement(header_node, 'NbOfTxs')
        nb_of_transactions_1_6.text = str(transactions_count_1_6)
        self.transactions_count = transactions_count_1_6

        control_sum_1_7 = etree.SubElement(header_node, 'CtrlSum')
        control_sum_1_7.text = '%.2f' % amount_control_sum_1_7

        self.generate_initiating_party_block(header_node)

    def generate_initiating_party_block(self, parent_node):
        """
        Difference with SEPA credit transfers:

            - Identification is not expected
        """
        initiating_party_1_8 = etree.SubElement(parent_node, 'InitgPty')

        initiating_party_name = etree.SubElement(initiating_party_1_8, 'Nm')
        initiating_party_name.text = self.debtor_bank_name

    def generate_start_payment_info_block(
        self, parent_node, requested_date, priority, lines
    ):
        """
        For now, 2.23 UltimateDebtor is not implemented. This would be used
        in the case where the payment is made on behalf of a third party.
        """
        payment_info_ident = "%s-%s-%s" % (
            self.reference, requested_date.replace('-', ''), priority
        )

        payment_info_2_0 = etree.SubElement(parent_node, 'PmtInf')

        payment_info_identification_2_1 = etree.SubElement(
            payment_info_2_0, 'PmtInfId')
        payment_info_identification_2_1.text = payment_info_ident[0:35]

        payment_method_2_2 = etree.SubElement(payment_info_2_0, 'PmtMtd')
        payment_method_2_2.text = 'TRF'

        batch_booking_2_3 = etree.SubElement(payment_info_2_0, 'BtchBookg')
        batch_booking_2_3.text = str(self.wizard.batch_booking).lower()

        nb_of_transactions_2_4 = etree.SubElement(payment_info_2_0, 'NbOfTxs')
        nb_of_transactions_2_4.text = str(len(lines))

        control_sum_2_5 = etree.SubElement(payment_info_2_0, 'CtrlSum')
        amount_control_sum_2_5 = sum(l.amount_currency for l in lines)
        control_sum_2_5.text = '%.2f' % amount_control_sum_2_5

        self.generate_payment_type_info_block(
            payment_info_2_0, requested_date, priority)

        requested_date_2_17 = etree.SubElement(
            payment_info_2_0, 'ReqdExctnDt')
        requested_date_2_17.text = requested_date

        self.generate_party_block_dbtr(payment_info_2_0)

        charge_bearer_2_24 = etree.SubElement(payment_info_2_0, 'ChrgBr')
        charge_bearer_2_24.text = self.wizard.charge_bearer

        for line in lines:
            self.generate_transaction(payment_info_2_0, line)

    def generate_payment_type_info_block(
        self, parent_node, requested_date, priority
    ):
        """
        Difference with SEPA credit transfers:

            - 2.8 ServiceLevel is not expected
            - 2.9 Code is not expected

            - 2.11 LocalInstrument is optional
            - 2.12 Code is mandatory
            - 2.14 CategoryPurpose (composed) is optional
        """
        payment_type_info_2_6 = etree.SubElement(parent_node, 'PmtTpInf')

        if priority:
            instruction_priority_2_7 = etree.SubElement(
                payment_type_info_2_6, 'InstrPrty')
            instruction_priority_2_7.text = priority

    def generate_transaction(self, parent_node, line):
        """
        Difference with SEPA credit transfers:

            - Choice between 2.43 InstructedAmount and 2.44 EquivalentAmount
            - 2.47 ExchangeRateInformation is optional
            - 2.51 ChargeBearer is optional for now, it is not implemented at
              the transaction level.

            - 2.89 RegulatoryReporting is required in some cases
            - 2.91 RelatedRemittanceInformation is optional
            - 2.98 RemittanceInformation is always unstructured

        """
        credit_transfer_transaction_info_2_27 = etree.SubElement(
            parent_node, 'CdtTrfTxInf')

        payment_identification_2_28 = etree.SubElement(
            credit_transfer_transaction_info_2_27, 'PmtId')

        end2end_identification_2_30 = etree.SubElement(
            payment_identification_2_28, 'EndToEndId')

        end2end_identification_2_30.text = line.name[0:35]
        currency_name = line.currency.name[0:3]

        amount_2_42 = etree.SubElement(
            credit_transfer_transaction_info_2_27, 'Amt')

        instructed_amount_2_43 = etree.SubElement(
            amount_2_42, 'InstdAmt', Ccy=currency_name)
        instructed_amount_2_43.text = '%.2f' % line.amount_currency

        if not line.bank_id:
            raise orm.except_orm(
                _('Error:'),
                _("Missing Bank Account on invoice '%s' (payment "
                    "order line reference '%s').")
                % (line.ml_inv_ref.number, line.name))

        self.generate_party_block_cdtr(
            credit_transfer_transaction_info_2_27, line)

        self.generate_remittance_info_block(
            credit_transfer_transaction_info_2_27, line)

    def generate_party_block_dbtr(self, parent_node):
        """
        Debtor -> Currency is optional

        2.22 DebtorAgentAccount
            - ignored because it is meant for very rare cases

        Difference with SEPA credit transfers:

            - Dbtr -> Id may be used to specify a contract number
        """
        debtor = etree.SubElement(parent_node, 'Dbtr')

        debtor_nm = etree.SubElement(debtor, 'Nm')
        debtor_nm.text = self.debtor_bank_name

        debtor_acct = etree.SubElement(parent_node, 'DbtrAcct')

        debtor_acct_id = etree.SubElement(debtor_acct, 'Id')

        debtor_acct_iban = etree.SubElement(debtor_acct_id, 'IBAN')
        debtor_acct_iban.text = self.debtor_account_number

        debtor_agent = etree.SubElement(parent_node, 'DbtrAgt')
        debtor_agent_institution = etree.SubElement(debtor_agent, 'FinInstnId')

        debtor_agent_bic = etree.SubElement(debtor_agent_institution, 'BIC')
        debtor_agent_bic.text = self.debtor_bic

    def generate_party_block_cdtr(self, parent_node, line):
        """
        Difference with SEPA credit transfers:

            - 2.71 IntermediaryAgent1 is optional
            - 2.72 IntermediaryAgent1Account is optional
            - 2.79 Requires the address of the creditor
            - 2.82 InstructionForCreditorAgent is optional

        For now, UltimateCreditor is not implemented.
        Also 2.79 -> Identification is not implemented either.
        """
        creditor_agent_2_77 = etree.SubElement(parent_node, 'CdtrAgt')

        creditor_institution_2_77 = etree.SubElement(
            creditor_agent_2_77, 'FinInstnId')

        creditor_bic_2_77 = etree.SubElement(creditor_institution_2_77, 'BIC')
        creditor_bic_2_77.text = line.bank_id.bank.bic

        creditor_2_79 = etree.SubElement(parent_node, 'Cdtr')
        creditor_2_79_nm = etree.SubElement(creditor_2_79, 'Nm')
        creditor_2_79_nm.text = line.partner_id.name[0:70]

        creditor_acct_2_80 = etree.SubElement(parent_node, 'CdtrAcct')
        creditor_acct_2_80_id = etree.SubElement(creditor_acct_2_80, 'Id')

        iban = self.wizard.validate_iban(line.bank_id.acc_number)
        creditor_iban_2_80 = etree.SubElement(creditor_acct_2_80_id, 'IBAN')
        creditor_iban_2_80.text = iban

    def generate_remittance_info_block(self, parent_node, line):
        remittance_info_2_91 = etree.SubElement(parent_node, 'RmtInf')

        if line.state == 'normal':
            remittance_info_unstructured_2_99 = etree.SubElement(
                remittance_info_2_91, 'Ustrd')
            remittance_info_unstructured_2_99.text = line.communication[0:140]

        else:
            if not line.struct_communication_type:
                raise orm.except_orm(
                    _('Error:'),
                    _("Missing 'Structured Communication Type' on payment "
                        "line with reference '%s'.")
                    % (line.name))

            remittance_info_structured_2_100 = etree.SubElement(
                remittance_info_2_91, 'Strd')
            creditor_ref_information_2_120 = etree.SubElement(
                remittance_info_structured_2_100, 'CdtrRefInf')

            creditor_ref_info_type_2_121 = etree.SubElement(
                creditor_ref_information_2_120, 'Tp')

            creditor_ref_info_type_or_2_122 = etree.SubElement(
                creditor_ref_info_type_2_121, 'CdOrPrtry')

            creditor_ref_info_type_code_2_123 = etree.SubElement(
                creditor_ref_info_type_or_2_122, 'Cd')
            creditor_ref_info_type_code_2_123.text = 'SCOR'

            creditor_ref_info_type_issuer_2_125 = etree.SubElement(
                creditor_ref_info_type_2_121, 'Issr')
            creditor_ref_info_type_issuer_2_125.text = (
                line.struct_communication_type)

            creditor_reference_2_126 = etree.SubElement(
                creditor_ref_information_2_120, 'Ref')
            creditor_reference_2_126.text = line.communication[0:35]

    def group_payment_lines(self):
        today = fields.date.context_today(
            self.wizard, self.cr, self.uid, context=self.context)

        lines_per_group = defaultdict(list)

        for payment_order in self.wizard.payment_order_ids:
            for line in payment_order.line_ids:
                priority = line.priority

                if payment_order.date_prefered == 'due':
                    requested_date = line.ml_maturity_date or today

                elif payment_order.date_prefered == 'fixed':
                    requested_date = payment_order.date_scheduled or today

                else:
                    requested_date = today

                key = (requested_date, priority)
                lines_per_group[key].append(line)

                if requested_date != line.date:
                    line.write({'date': requested_date})

        return lines_per_group

    def validate_xml(self):
        xsd_etree_obj = etree.parse(
            tools.file_open(self.pain_xsd_file))

        official_pain_schema = etree.XMLSchema(xsd_etree_obj)

        try:
            root_to_validate = etree.fromstring(self.xml_string)
            official_pain_schema.assertValid(root_to_validate)
        except Exception, e:
            logger.warning(
                "The XML file is invalid against the XML Schema Definition")
            logger.warning(self.xml_string)
            logger.warning(e)
            raise orm.except_orm(
                _('Error:'),
                _("The generated XML file is not valid against the official "
                    "XML Schema Definition. The generated XML file and the "
                    "full error have been written in the server logs. Here "
                    "is the error, which may give you an idea on the cause "
                    "of the problem : %s")
                % str(e))


class banking_export_international_wizard(orm.TransientModel):
    _name = 'banking.export.international.wizard'
    _description = 'Export International Credit Transfer File'

    _columns = {
        'state': fields.selection(
            [
                ('create', 'Create'),
                ('finish', 'Finish'),
            ],
            'State', readonly=True),
        'batch_booking': fields.boolean(
            'Batch Booking',
            help="If true, the bank statement will display only one debit "
            "line for all the wire transfers of the SEPA XML file ; if "
            "false, the bank statement will display one debit line per wire "
            "transfer of the SEPA XML file."),
        'charge_bearer': fields.selection(
            [
                ('SLEV', 'Following Service Level'),
                ('SHAR', 'Shared'),
                ('CRED', 'Borne by Creditor'),
                ('DEBT', 'Borne by Debtor'),
            ],
            'Charge Bearer', required=True,
            help="Following service level : transaction charges are to be "
            "applied following the rules agreed in the service level and/or "
            "scheme (SEPA Core messages must use this). Shared : transaction "
            "charges on the debtor side are to be borne by the debtor, "
            "transaction charges on the creditor side are to be borne by "
            "the creditor. Borne by creditor : all transaction charges are "
            "to be borne by the creditor. Borne by debtor : all transaction "
            "charges are to be borne by the debtor."),
        'nb_transactions': fields.related(
            'file_id', 'nb_transactions', type='integer',
            string='Number of Transactions', readonly=True),
        'total_amount': fields.related(
            'file_id', 'total_amount', type='float', string='Total Amount',
            readonly=True),
        'file_id': fields.many2one(
            'banking.export.international', 'SEPA XML File', readonly=True),
        'file': fields.related(
            'file_id', 'file', string="File", type='binary', readonly=True),
        'filename': fields.related(
            'file_id', 'filename', string="Filename", type='char',
            size=256, readonly=True),
        'payment_order_ids': fields.many2many(
            'payment.order', 'wiz_international_payorders_rel', 'wizard_id',
            'payment_order_id', 'Payment Orders', readonly=True),
    }

    _defaults = {
        'charge_bearer': 'SLEV',
        'state': 'create',
    }

    def create(self, cr, uid, vals, context=None):
        payment_order_ids = context.get('active_ids', [])
        vals.update({
            'payment_order_ids': [[6, 0, payment_order_ids]],
        })
        return super(banking_export_international_wizard, self).create(
            cr, uid, vals, context=context)

    def get_wizard(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        assert len(ids) == 1, 'Expected singleton'
        return self.browse(cr, uid, ids[0], context=context)

    def validate_iban(self, cr, uid, ids, iban, context=None):
        partner_bank_obj = self.pool.get('res.partner.bank')
        if partner_bank_obj.is_iban_valid(cr, uid, iban, context=context):
            return iban.replace(' ', '')
        else:
            raise orm.except_orm(
                _('Error:'), _("This IBAN is not valid : %s") % iban)

    def process_payment(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        wizard = self.get_wizard(cr, uid, ids, context=context)

        pain_flavor = wizard.payment_order_ids[0].mode.type.code

        if pain_flavor != 'pain.001.001.03':
            raise orm.except_orm(_(
                'The standard %s is not implemented for international '
                'credit transfers.') % pain_flavor)

        generator = XmlGeneratorInternational(
            cr, uid, wizard=wizard, context=context)

        generator.generate()

        logger.debug(
            "Generated SEPA XML file in format %s below" %
            generator.pain_flavor)

        generator.validate_xml()

        return wizard.finalize_payment_file_creation(generator)

    def prepare_export_payment(self, cr, uid, ids, generator, context=None):
        wizard = self.get_wizard(cr, uid, ids, context=context)

        return {
            'batch_booking': wizard.batch_booking,
            'charge_bearer': wizard.charge_bearer,
            'total_amount': generator.total_amount,
            'nb_transactions': generator.transactions_count,
            'file': base64.encodestring(generator.xml_string),
            'payment_order_ids': [(
                6, 0, [x.id for x in wizard.payment_order_ids]
            )],
        }

    def finalize_payment_file_creation(
        self, cr, uid, ids, generator, context=None
    ):
        wizard = self.get_wizard(cr, uid, ids, context=context)

        vals = wizard.prepare_export_payment(generator)

        file_id = generator.file_obj.create(
            cr, uid, vals, context=context)

        self.write(cr, uid, ids, {
            'file_id': file_id,
            'state': 'finish',
        }, context=context)

        action = {
            'name': 'SEPA File',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': self._name,
            'res_id': ids[0],
            'target': 'new',
        }
        return action

    def cancel_payment(self, cr, uid, ids, context=None):
        wizard = self.get_wizard(cr, uid, ids, context=context)

        self.pool.get('banking.export.international').unlink(
            cr, uid, wizard.file_id.id, context=context)

        return {'type': 'ir.actions.act_window_close'}

    def save_payment(self, cr, uid, ids, context=None):
        wizard = self.get_wizard(cr, uid, ids, context=context)

        self.pool.get('banking.export.international').write(
            cr, uid, wizard.file_id.id, {'state': 'sent'},
            context=context)

        wf_service = netsvc.LocalService('workflow')
        for order in wizard.payment_order_ids:
            wf_service.trg_validate(uid, 'payment.order', order.id, 'done', cr)

        return {'type': 'ir.actions.act_window_close'}
