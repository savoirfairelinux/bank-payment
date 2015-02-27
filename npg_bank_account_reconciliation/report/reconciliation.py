# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 NovaPoint Group LLC (<http://www.novapointgroup.com>)
#    Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
from openerp.report import report_sxw


class Reconciliation(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(Reconciliation, self).__init__(cr, uid, name, context=context)


report_sxw.report_sxw(
    'report.detailed.reco.webkit',
    'bank.acc.rec.statement',
    'addons/npg_bank_account_reconciliation/report/detailed_report.mako',
    parser=Reconciliation,
)


report_sxw.report_sxw(
    'report.summary.rec.webkit',
    'bank.acc.rec.statement',
    'addons/npg_bank_account_reconciliation/report/summary_report.mako',
    parser=Reconciliation
)
