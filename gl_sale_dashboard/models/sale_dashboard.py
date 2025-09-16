# -*- coding: utf-8 -*-
import pytz
from datetime import datetime, time, timedelta
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class SaleOrderDashboard(models.Model):
    _inherit = "sale.order"

    # ----------------- Helpers -----------------
    def _user_utc_range(self, from_date_str=None, to_date_str=None):
        """
        Returns (utc_start_dt, utc_end_dt, start_date_for_date_fields, end_date_for_date_fields)
        - utc_start_dt/utc_end_dt: naive datetimes in UTC suitable for datetime field comparisons (date_order, scheduled_date)
        - start_date_for_date_fields/end_date_for_date_fields: date strings 'YYYY-MM-DD' suitable for domain on date fields
        If from_date_str/to_date_str are None, use user's "today" (based on user's timezone).
        """
        user_tz_name = self.env.user.tz or "UTC"
        user_tz = pytz.timezone(user_tz_name)

        if from_date_str and to_date_str:
            # parse incoming 'YYYY-MM-DD'
            try:
                from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
                to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
            except Exception:
                # fallback to today in user tz
                today_user = fields.Datetime.context_timestamp(self, datetime.utcnow())
                from_date = today_user.date()
                to_date = today_user.date()
        else:
            # use user's current day
            now_user = fields.Datetime.context_timestamp(self, datetime.utcnow())
            from_date = now_user.date()
            to_date = now_user.date()

        # start/end as localized datetimes in user's timezone
        local_start = datetime.combine(from_date, time.min)
        local_end = datetime.combine(to_date, time.max)

        local_start = user_tz.localize(local_start)
        local_end = user_tz.localize(local_end)

        # convert to UTC and make naive (Odoo stores datetimes in UTC without tzinfo)
        utc_start = local_start.astimezone(pytz.UTC).replace(tzinfo=None)
        utc_end = local_end.astimezone(pytz.UTC).replace(tzinfo=None)

        # date strings for domains on 'date' fields
        start_date_str = from_date.strftime("%Y-%m-%d")
        end_date_str = to_date.strftime("%Y-%m-%d")

        return utc_start, utc_end, start_date_str, end_date_str

    # ----------------- Core endpoints -----------------
    @api.model
    def _aggregate_payment_summary(self, payments):
        """
        Return list of {'journal': name, 'amount': sum} aggregated by journal.
        Uses read_group for performance when possible.
        'payments' can be an account.payment recordset.
        """
        if not payments:
            return []
        # Use read_group to aggregate by journal_id
        domain = [('id', 'in', payments.ids)]
        grouped = self.env['account.payment'].sudo().read_group(
            domain, ['journal_id', 'amount'], ['journal_id']
        )
        result = []
        for g in grouped:
            journal = self.env['account.journal'].browse(g.get('journal_id')[0]) if g.get('journal_id') else None
            name = journal.name if journal else (g.get('journal_id') and g.get('journal_id')[1]) or _("Unknown")
            amount = float(g.get('amount') or 0.0)
            result.append({'journal': name, 'amount': amount})
        return result

    @api.model
    def get_today_data(self):
        """
        Return dashboard values for 'today' in user's timezone.
        """
        utc_start, utc_end, start_date_str, end_date_str = self._user_utc_range(None, None)
        print("---------", start_date_str, end_date_str)
        company_domain = [('company_id', '=', self.env.company.id)]

        # sale orders (date_order is datetime)
        sale_domain = [('state', '=', 'sale'), ('date_order', '>=', utc_start), ('date_order', '<=', utc_end)] + company_domain
        sale_order_count = self.env['sale.order'].sudo().search_count(sale_domain)
        sale_order_amount = sum(self.env['sale.order'].sudo().search(sale_domain).mapped('amount_total')) if sale_order_count else 0.0

        # account moves (invoice_date is date)
        inv_domain = [('state', '=', 'posted'), ('move_type', '=', 'out_invoice'),
                      ('invoice_date', '>=', start_date_str), ('invoice_date', '<=', end_date_str)] + company_domain
        account_move_count = self.env['account.move'].sudo().search_count(inv_domain)
        account_move_amount = sum(self.env['account.move'].sudo().search(inv_domain).mapped('amount_total_signed')) if account_move_count else 0.0

        # stock picking counts (scheduled_date is datetime)
        stock_done_domain = [('name', 'like', 'OUT'), ('state', '=', 'done'), ('scheduled_date', '>=', utc_start), ('scheduled_date', '<=', utc_end)]
        stock_not_done_domain = [('name', 'like', 'OUT'), ('state', '!=', 'done'), ('scheduled_date', '>=', utc_start), ('scheduled_date', '<=', utc_end)]
        stock_picking_count = self.env['stock.picking'].sudo().search_count(stock_done_domain)
        not_stock_picking_count = self.env['stock.picking'].sudo().search_count(stock_not_done_domain)

        # customers: compute is_new_customer values lazily (ResPartner compute handles per-record)
        # We'll compute counts by reading partners' stored field (faster) if already computed
        partners = self.env['res.partner'].sudo().search([])  # may be large; alternative: compute via SQL if needed
        new_customer_count = sum(1 for p in partners if p.is_new_customer == 1)
        retained_customer_count = sum(1 for p in partners if p.is_new_customer and p.is_new_customer > 1)

        # payments (account.payment.date is a date field) - filter by date range
        payment_domain = [('partner_type', '=', 'customer'), ('date', '>=', start_date_str), ('date', '<=', end_date_str)]
        payments = self.env['account.payment'].sudo().search(payment_domain)
        payment_summary = self._aggregate_payment_summary(payments)

        return {
            'sale_order_count': int(sale_order_count),
            'sale_order_amount': float(sale_order_amount),
            'account_move_count': int(account_move_count),
            'account_move_amount': float(account_move_amount),
            'stock_picking_count': int(stock_picking_count),
            'not_stock_picking_count': int(not_stock_picking_count),
            'new_customer_count': int(new_customer_count),
            'retained_customer_count': int(retained_customer_count),
            'payment_details': payment_summary,
        }

    @api.model
    def get_data_based_date(self, from_date_cus, to_date_cus):
        """
        Return dashboard values for a given date range (YYYY-MM-DD).
        from_date_cus and to_date_cus expected as 'YYYY-MM-DD' strings.
        """
        # Convert to UTC datetimes and date strings for date fields
        utc_start, utc_end, start_date_str, end_date_str = self._user_utc_range(from_date_cus, to_date_cus)

        company_domain = [('company_id', '=', self.env.company.id)]

        # Sale orders: date_order is datetime (use UTC datetimes)
        sale_domain = [('state', '=', 'sale'), ('date_order', '>=', utc_start), ('date_order', '<=', utc_end)] + company_domain
        sale_order_count = self.env['sale.order'].sudo().search_count(sale_domain)
        sale_order_amount = sum(self.env['sale.order'].sudo().search(sale_domain).mapped('amount_total')) if sale_order_count else 0.0

        # Account moves: invoice_date is date
        inv_domain = [('state', '=', 'posted'), ('move_type', '=', 'out_invoice'),
                      ('invoice_date', '>=', start_date_str), ('invoice_date', '<=', end_date_str)] + company_domain
        account_move_count = self.env['account.move'].sudo().search_count(inv_domain)
        account_move_amount = sum(self.env['account.move'].sudo().search(inv_domain).mapped('amount_total_signed')) if account_move_count else 0.0
        # Stock pickings
        stock_done_domain = [('name', 'like', 'OUT'), ('state', '=', 'done'), ('date_done', '>=', start_date_str), ('date_done', '<=', end_date_str)]
        stock_not_done_domain = [('name', 'like', 'OUT'), ('state', '!=', 'done'), ('scheduled_date', '>=', start_date_str), ('scheduled_date', '<=', end_date_str)]
        stock_picking_count = self.env['stock.picking'].sudo().search_count(stock_done_domain)
        not_stock_picking_count = self.env['stock.picking'].sudo().search_count(stock_not_done_domain)

        # Customers: reuse stored is_new_customer field (computed)
        # partners = self.env['res.partner'].sudo().search([])
        # new_customer_count = sum(1 for p in partners if p.is_new_customer == 1)
        # retained_customer_count = sum(1 for p in partners if p.is_new_customer and p.is_new_customer > 1)
        order_stats = self.env['sale.order'].sudo().read_group(
            domain=[
                ('date_order', '>=', start_date_str),
                ('date_order', '<=', end_date_str),
                ('state', 'in', ['sale', 'done']),  # count only confirmed/done orders
            ],
            fields=['partner_id'],
            groupby=['partner_id'],
        )

        new_customer_ids = [rec['partner_id'][0] for rec in order_stats if rec['partner_id_count'] == 1]
        retained_customer_ids = [rec['partner_id'][0] for rec in order_stats if rec['partner_id_count'] > 1]

        # payments (date field)
        payment_domain = [('partner_type', '=', 'customer'), ('date', '>=', start_date_str), ('date', '<=', end_date_str)]
        payments = self.env['account.payment'].sudo().search(payment_domain)
        payment_summary = self._aggregate_payment_summary(payments)

        return {
            'sale_order_count': int(sale_order_count),
            'sale_order_amount': float(sale_order_amount),
            'account_move_count': int(account_move_count),
            'account_move_amount': float(account_move_amount),
            'stock_picking_count': int(stock_picking_count),
            'not_stock_picking_count': int(not_stock_picking_count),
            'new_customer_count': len(new_customer_ids),
            'retained_customer_count': len(retained_customer_ids),
            'payment_details': payment_summary,
            "new_customer_ids": new_customer_ids,
            "retained_customer_ids": retained_customer_ids,
        }


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_new_customer = fields.Integer(string='Sale Order Count (Today)', compute="_compute_is_new_customer", store=True)

    @api.depends()
    def _compute_is_new_customer(self):
        """
        Compute number of sale.orders for this partner for 'today' (in user's timezone).
        Optimized to compute per-record using search_count.
        """
        # compute user's today range in UTC
        utc_start, utc_end, _, _ = self.env['sale.order']._user_utc_range(None, None)
        for partner in self:
            cnt = self.env['sale.order'].sudo().search_count([
                ('partner_id', '=', partner.id),
                ('date_order', '>=', utc_start),
                ('date_order', '<=', utc_end),
            ])
            partner.is_new_customer = int(cnt)
