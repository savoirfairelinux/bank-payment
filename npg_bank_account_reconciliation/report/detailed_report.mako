<html>
  <head>
    <style type="text/css">
      table {
      page-break-inside:auto
      }
      table tr {
      page-break-inside:avoid;
      page-break-after:auto;
      }
      thead {
      display:table-header-group;
      }
      .important_number_table {
      font-weight:bold;
      font-size: 110%;
      }
      .cell {
      border:none;
      width:2px;
      }
      .cell_invisible {
      width:5px;
      }
      .col_header {
      font-weight:bold;
      width:30px;
      }
      .col_header_third {
      font-style:italic;
      }
      .col_header_first {
      font-size: larger;
      }
      .col_date {
      width:10px;
      }
      .col_amount {
      width:100px;
      }
      .col_partner {
      width:40px;
      }
      .right_col {
      text-align:right;
      width:100px;
      }
      .with_border {
      font-weight:bold;
      border-style:solid;
      border-width:0px;
      border-bottom-width:1px;
      }
      .first_item {
      text-align:center;
      }
      ${css}
    </style>
  </head>
  <body>
    %for rec in objects:
    <table style="width:100%;">
        <tr>
          <td class="cell first_item important_number_table"
             colspan="6">
            ${_("Detailed statement %s") % rec.name}
            <br/>
            ${_("Account: %s - %s") % (rec .account_id.code, rec.account_id.name)}
          </td>
        </tr>
    </table>
    <br/>
    <table style="width:100%;font-size:70%;">
      <thead>
          <tr>
            <td class="cell_invisible with_border">
            </td>
            <td class="cell_invisible with_border">
            </td>
            <td class="cell_invisible with_border">
            </td>
            <td class="with_border col_date">
              ${_("Date")}
            </td>
            <td class="with_border">
              ${_("Reference")}
            </td>
            <td class="with_border col_partner">
              ${_("Partner")}
            </td>
            <td class="col_amount with_border">
              ${_("Amount")}
            </td>
          </tr>
      </thead>
      <tr>
        <td class="left_col cell col_header col_header_first" colspan="4">
          ${_("Beginning Balance")}
        </td>
        <td class="col_header">
        </td>
        <td class="cell_invisible">
        </td>
        <td class="cell right_col">
          ${formatLang(rec.starting_balance, monetary=True, currency_obj=rec.company_id.currency_id)}
        </td>
      </tr>
      <tr>
        <td class="cell_invisible">
        </td>
        <td class="cell col_header" colspan="4">
          ${_("Cleared Transactions")}
        </td>
        <td class="cell_invisible">
        </td>
        <td class="cell right_col">
        </td>
      </tr>
      <tr>
        <td class="cell_invisible">
        </td>
        <td class="cell_invisible">
        </td>
        <td class="cell col_header col_header_third" colspan="4">
          ${_("Deposits and Credits")}${" - %s " % int(rec.sum_of_debits_lines)}${_("items")}
        </td>
        <td class="cell right_col with_border">
          ${formatLang(rec.sum_of_debits, monetary=True, currency_obj=rec.company_id.currency_id)}
        </td>
      </tr>
      %for rec_line in [line for line in rec.debit_move_line_ids if line.cleared_bank_account]:
      <tr>
        <td class="cell_invisible">
        </td>
        <td class="cell_invisible">
        </td>
        <td class="cell_invisible">
        </td>
        <td class="col_date">
          ${rec_line.date}
        </td>
        <td>
         ${"%s - %s" %(rec_line.move_line_id.move_id.name, rec_line.move_line_id.name)}
        </td>
        <td class="col_partner">
          ${rec_line.partner_id.name and rec_line.partner_id.name or ""}
        </td>
        <td class="cell right_col col_amount">
          ${formatLang(rec_line.amount, monetary=True, currency_obj=rec.company_id.currency_id)}
        </td>
      </tr>
      %endfor
      <tr>
        <td>
        </td>
        <td>
        </td>
        <td class="cell col_header col_header_third" colspan="4">
          ${_("Checks and Debits")}${" - %s " % int(rec.sum_of_credits_lines)}${_("items")}
        </td>
        <td class="cell with_border right_col">
          ${formatLang(-rec.sum_of_credits, monetary=True, currency_obj=rec.company_id.currency_id)}
        </td>
      </tr>
      %for rec_line in [line for line in rec.credit_move_line_ids if line.cleared_bank_account]:
      <tr>
        <td class="cell left_col">
        </td>
        <td class="cell left_col">
        </td>
        <td class="cell left_col">
        </td>
        <td>
          ${rec_line.date}
        </td>
        <td>
          ${rec_line.ref and rec_line.ref or ""}
        </td>
        <td>
          ${rec_line.partner_id.name and rec_line.partner_id.name or ""}
        </td>
        <td class="cell right_col">
          ${formatLang(rec_line.amount, monetary=True, currency_obj=rec.company_id.currency_id)}
        </td>
      </tr>
      %endfor
      <tr>
        <td>
        </td>
        <td class="cell col_header" colspan="4">
          ${_("Total Cleared Transactions")}
        </td>
        <td>
        </td>
        <td class="cell right_col with_border">
          ${formatLang(rec.cleared_balance, monetary=True, currency_obj=rec.company_id.currency_id)}
        </td>
      </tr>
      <tr>
        <td class="cell col_header col_header_first" colspan="4">
          ${_("Cleared Balance")}
        </td>
        <td>
        </td>
        <td>
        </td>
        <td class="cell important_number_table right_col">
          ${formatLang(rec.cleared_balance + rec.starting_balance, monetary=True, currency_obj=rec.company_id.currency_id)}
        </td>
      </tr>
      <tr>
        <td>
        </td>
        <td class="cell col_header" colspan="4">
          ${_("Uncleared Transactions")}
        </td>
        <td>
        </td>
        <td class="cell right_col">
        </td>
      </tr>
      <tr>
        <td>
        </td>
        <td>
        </td>
        <td class="cell col_header col_header_third" colspan="4">
          ${_("Deposits and Credits")}${" - %s " % int(rec.sum_of_debits_lines_unclear)}${_("items")}
        </td>
        <td class="cell right_col with_border">
          ${formatLang(rec.sum_of_debits_unclear, monetary=True, currency_obj=rec.company_id.currency_id)}
        </td>
      </tr>
      %for rec_line in [line for line in rec.debit_move_line_ids if not line.cleared_bank_account]:
      <tr>
        <td class="cell left_col">
        </td>
        <td class="cell left_col">
        </td>
        <td class="cell left_col">
        </td>
        <td>
          ${rec_line.date}
        </td>
        <td>
          ${rec_line.ref and rec_line.ref or ""}
        </td>
        <td>
          ${rec_line.partner_id.name and rec_line.partner_id.name or ""}
        </td>
        <td class="cell right_col">
          ${formatLang(rec_line.amount, monetary=True, currency_obj=rec.company_id.currency_id)}
        </td>
      </tr>
      %endfor
      <tr>
        <td>
        </td>
        <td>
        </td>
        <td class="cell col_header col_header_third" colspan="4">
          ${_("Checks and Debits")}${" - %s " % int(rec.sum_of_credits_lines_unclear)}${_("items")}
        </td>
        <td class="cell right_col with_border">
          ${formatLang(-rec.sum_of_credits_unclear, monetary=True, currency_obj=rec.company_id.currency_id)}
        </td>
      </tr>
      %for rec_line in [line for line in rec.credit_move_line_ids if not line.cleared_bank_account]:
      <tr>
        <td class="cell left_col">
        </td>
        <td class="cell left_col">
        </td>
        <td class="cell left_col">
        </td>
        <td>
          ${rec_line.date}
        </td>
        <td>
          ${rec_line.ref and rec_line.ref or ""}
        </td>
        <td>
          ${rec_line.partner_id.name and rec_line.partner_id.name or ""}
        </td>
        <td class="cell right_col">
          ${formatLang(rec_line.amount, monetary=True, currency_obj=rec.company_id.currency_id)}
        </td>
      </tr>
      %endfor
      <tr>
        <td>
        </td>
        <td class="cell col_header" colspan="4">
          ${_("Total Uncleared Transactions")}
        </td>
        <td>
        </td>
        <td class="cell right_col with_border">
          ${formatLang(rec.uncleared_balance, monetary=True, currency_obj=rec.company_id.currency_id)}
        </td>
      </tr>
      <tr>
        <td class="cell col_header col_header_first" colspan="5">
          ${_("Registered Balance as of")}${" %s" % formatLang(rec
          .ending_date, date=True, currency_obj=rec.company_id.currency_id)}
        </td>
        <td>
        </td>
        <td class="cell important_number_table right_col">
          ${formatLang(rec.starting_balance + rec.cleared_balance + rec.uncleared_balance, monetary=True, currency_obj=rec.company_id.currency_id)}
        </td>
      </tr>
    </table>

    %endfor
  </body>
</html>
