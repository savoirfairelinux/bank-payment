<html>
  <head>
    <style type="text/css">
        table {
               page-break-inside:auto
    }

    table tr {
                page-break-inside:avoid; page-break-after:auto;
  }
      .important_number_table
      {
      font-weight:bold;
      font-size: 110%;
      }
      .bold{
      font-weight:bold;
      }
      .cell
      {
      border:none;
      }
      .left_col
      {
      width:40%;
      }
      .col_header
      {
      }
      .right_col_sum
      {
      width:20%;
      text-align:right;
      }
      .right_col
      {
      text-align:right;
      }
      .second_line
      {
      padding-left:3em;
      }
      .third_line
      {
      padding-left:6em;
      }
      .first_item
      {
      text-align:center;
      }
      ${css}
    </style>
  </head>
  <body>
    %for rec in objects:
      <table style="width:100%">
        <tr>
          <td class="cell left_col first_item important_number_table"
              colspan="2">
            ${_("Summary statement %s") % rec.name}
            <br/>
            ${_("Account: %s - %s") % (rec .account_id.code, rec.account_id.name)}
          </td>
        </tr>
        <tr>
          <td>
            <br/>
          </td>
        </tr>
        <tr>
          <td class="left_col cell">
            ${_("Beginning Balance")}
          </td>
          <td class="cell right_col_sum">
            ${formatLang(rec.starting_balance, monetary=True, currency_obj=rec.company_id.currency_id)}
          </td>
        </tr>
        <tr>
          <td class="cell second_line left_col">
            ${_("Cleared Transactions")}
          </td>
          <td class="cell right_col_sum">
          </td>
        </tr>
        <tr>
          <td class="cell third_line left_col">
            ${_("Deposits and Credits")}${" - %s " % int(rec.sum_of_debits_lines)}${_("items")}
          </td>
          <td class="cell right_col_sum">
            ${formatLang(rec.sum_of_debits, monetary=True, currency_obj=rec.company_id.currency_id)}
          </td>
        </tr>
        <tr>
          <td class="cell third_line left_col">
            ${_("Checks and Debits")}${" - %s " % int(rec
            .sum_of_credits_lines)}${_("items")}
          </td>
          <td class="cell right_col_sum">
            ${formatLang(-rec.sum_of_credits, monetary=True, currency_obj=rec.company_id.currency_id)}
          </td>
        </tr>
        <tr>
          <td class="cell second_line left_col">
            ${_("Total Cleared Transactions")}
          </td>
          <td class="cell right_col_sum bold">
            ${formatLang(rec.cleared_balance, monetary=True, currency_obj=rec.company_id.currency_id)}
          </td>
        </tr>
        <tr>
          <td class="cell left_col bold">
            ${_("Cleared Balance")}
          </td>
          <td class="cell important_number_table right_col_sum">
            ${formatLang(rec.cleared_balance + rec.starting_balance, monetary=True, currency_obj=rec.company_id.currency_id)}
          </td>
        </tr>
        <tr>
          <td class="cell second_line left_col">
            ${_("Uncleared Transactions")}
          </td>
          <td class="cell right_col_sum">
          </td>
        </tr>
        <tr>
          <td class="cell third_line left_col">
            ${_("Deposits and Credits")}${" - %s " % int(rec.sum_of_debits_lines_unclear)}${_("items")}
          </td>
          <td class="cell right_col_sum">
            ${formatLang(rec.sum_of_debits_unclear, monetary=True, currency_obj=rec.company_id.currency_id)}
          </td>
        </tr>
        <tr>
          <td class="cell third_line left_col">
            ${_("Checks and Debits")}${" - %s " % int(rec
            .sum_of_credits_lines_unclear)}${_("items")}
          </td>
          <td class="cell right_col_sum">
            ${formatLang(-rec.sum_of_credits_unclear, monetary=True, currency_obj=rec.company_id.currency_id)}
          </td>
        </tr>
        <tr>
          <td class="cell second_line left_col">
            ${_("Total Uncleared Transactions")}
          </td>
          <td class="cell right_col_sum bold">
            ${formatLang(rec.uncleared_balance, monetary=True, currency_obj=rec.company_id.currency_id)}
          </td>
        </tr>
        <tr>
          <td class="cell left_col bold">
            ${_("Registered Balance as of")}${" %s" % formatLang(rec
            .ending_date, date=True, currency_obj=rec.company_id.currency_id)}
          </td>
          <td class="cell important_number_table right_col_sum">
            ${formatLang(rec.starting_balance + rec.cleared_balance + rec.uncleared_balance, monetary=True, currency_obj=rec.company_id.currency_id)}
          </td>
        </tr>
      </table>

    %endfor
  </body>
</html>
