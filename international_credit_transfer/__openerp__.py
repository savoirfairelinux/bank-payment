# -*- encoding: utf-8 -*-
##############################################################################
#
#    SEPA Credit Transfer module for OpenERP
#    Copyright (C) 2010-2013 Akretion (http://www.akretion.com)
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
#
#    Copyright (C) 2016 Savoir-faire Linux (http://www.savoirfairelinux.com)
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
{
    'name': 'International Credit Transfer',
    'summary': 'Create XML files for International Credit Transfers',
    'version': '7.0.1.0.0',
    'license': 'AGPL-3',
    'author': "Savoir-faire Linux, Akretion, Odoo Community Association (OCA)",
    'website': 'https://www.savoirfairelinux.com',
    'category': 'Banking addons',
    'depends': [
        'account_banking_pain_base',
        'account_banking_tests',
    ],
    'external_dependencies': {
        'python': ['unidecode'],
    },
    'data': [
        'account_banking_international_view.xml',
        'wizard/export_international_view.xml',
        'data/payment_mode_type.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'active': False,
    'installable': True,
}
