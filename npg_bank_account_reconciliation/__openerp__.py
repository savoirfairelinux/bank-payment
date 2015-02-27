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
{
    'name': 'Bank Account Reconciliation with O/S entries',
    'version': '2.0',
    'category': 'Accounting and Financial Management',
    'description': """

Description
-----------
This module is designed to provide an easy method in which
OpenERP accounting
users can manually reconcile/validate their financial transactions from their
financial institution/transaction providers (e.g. Paypal, A financial
institution, google wallet, etc) against OpenERP GL Chart of Account
bank accounts.

Users will be able to validate and indicate if a transaction has
'Cleared the Bank' using a checkmark on a new Reconcile Financial Account
Statement view on each individual financial transaction.
Users will also be able to mark transactions on a bank account for future
research.

The idea is that as a first step users will manually look at their paper
statement and line-by-line check off which financial transactions have cleared
the bank in OpenERP using the new Bank Reconciliation Wizard. These changes
will be displayed on the  new Reconcile Financial Account Statement tree view
screen. This is the process in which many companies reconcile (aka Audit)
their bank account statements and accounting system today and represents
good segregation of duties

Users can save their in-process reconciliations.

Other Features
--------------
From the original module by NPG, this version adds :
* the computation of the registered balance which is the sum of the cleared
balance and the uncleared balance
* the ability to print a detailed bank statement report & a summary report
* these report are showing the Total Cleared Transactions, Total Un-Cleared
Transactions, Balance and Registered Balance amount
* the management of outstanding entries : all journal items which have not
been marked as cleared in a previous account, will be fetched in any new
statement (for the same account)
* multi-currency support : for any account which in not in the company's
currency, the form will show all the amounts in both currencies; the
starting balance and ending balance have to be set in the foreign currency;
the difference has to be 0 computed on the amounts in foreign currency;
finally, due to currency rates, the registered balance is likely to not match
the GL account balance... hence a button allow to automatically create the
adjustment journal entry.

Background
----------
Using the search view filters - users will also be able to effectively sort,
filter the transactions on a particular GL Financial Account.
This new screen will display the journal items associated with a particular
bank account. Several of the field labels have been relabeled to a more common
vernacular.

Contributors
------------
* based on module npg_bank_account_reconciliation from NovaPoint Group LLC
* Marc Cassuto (marc.cassuto@gmail.com)
* Mathieu Benoit (mathieu.benoit@savoirfairelinux.com) for reports
* Vincent Vinet (vincent.vinet@savoirfairelinux.com) for multi-currency support
""",
    'author': 'Marc Cassuto',
    'depends': [
        'account_cutoff_base',
        'account_voucher',
        'report_webkit',
    ],
    'init_xml': [],
    'update_xml': ["security/npg_bank_account_reconciliation_security.xml",
                   "security/ir.model.access.csv",
                   "npg_bank_account_reconciliation_view.xml",
                   "account_move_line_view.xml"],
    'demo_xml': [],
    'data': [
        'report/report.xml',
    ],
    'installable': True,
    'active': False,
}
