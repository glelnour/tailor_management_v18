
from odoo import api, models
import logging
_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _expand_pack_lines(self, product, qty):
        """
        Recursively expand pack products to their base components.
        Returns a list of order lines for all nested sub-products.
        """
        result_lines = []

        if not product.pack_ok or not product.pack_line_ids:
            return []

        for pack_line in product.pack_line_ids:
            sub_product = pack_line.product_id
            sub_qty = qty * pack_line.quantity
            if sub_product.pack_ok and sub_product.pack_line_ids:
                # Recursively expand nested pack product
                result_lines += self._expand_pack_lines(sub_product, sub_qty)
            else:
                # Base product, add line
                result_lines.append([0, 0, {
                    'qty': sub_qty,
                    'price_unit': 0.0,
                    'price_subtotal': 0.0,
                    'price_subtotal_incl': 0.0,
                    'product_id': sub_product.id,
                    'full_product_name': sub_product.name,
                    'is_component': True
                }])
        return result_lines

    @api.model
    def _process_order(self, order, existing_order):
        """
        Create or update a pos.order from a given dictionary, with support for pack products.
        """
        draft = True if order.get('state') == 'draft' else False
        pos_session = self.env['pos.session'].browse(order['session_id'])
        if pos_session.state in ['closing_control', 'closed']:
            order['session_id'] = self._get_valid_session(order).id

        # Handle missing partner
        if order.get('partner_id'):
            partner = self.env['res.partner'].browse(order['partner_id'])
            if not partner.exists():
                order.update({
                    "partner_id": False,
                    "to_invoice": False,
                })

        # Expand Pack Product Lines
        new_lines = []
        line_datas = order.get('lines', [])

        for line_data in line_datas:
            new_lines.append(line_data)
            line_qty = line_data[2].get('qty')
            product = self.env['product.product'].browse(line_data[2].get('product_id'))
            if product and product.pack_ok:
                nested_lines = self._expand_pack_lines(product, line_qty)
                new_lines.extend(nested_lines)
                # for pack_line in product.pack_line_ids:
                #     new_lines.append([0, 0, {
                #         'qty': line_qty * pack_line.quantity,
                #         'price_unit': 0.0,
                #         'price_subtotal': 0.0,
                #         'price_subtotal_incl': 0.0,
                #         'product_id': pack_line.product_id.id,
                #         'full_product_name': pack_line.product_id.name,
                #         'is_component': True
                #     }])
        if new_lines:
            order['lines'] = new_lines

        # Prepare combo uuids (used by built-in combo logic)
        combo_child_uuids_by_parent_uuid = self._prepare_combo_line_uuids(order)

        # Create or update pos.order
        if not existing_order:
            pos_order = self.create({
                **{key: value for key, value in order.items() if key != 'name'},
                'pos_reference': order.get('name'),
            })
            pos_order = pos_order.with_company(pos_order.company_id)
        else:
            pos_order = existing_order

            # Handle session mismatch
            if order.get('session_id') and order['session_id'] != pos_order.session_id.id:
                pos_order.write({'session_id': order['session_id']})

            # Handle update of lines/payments
            for field in ['lines', 'payment_ids']:
                if order.get(field):
                    existing_ids = self.env[pos_order[field]._name].browse(
                        [r[1] for r in order[field] if r[1] != 0]).exists().ids
                    filtered_vals = [r for r in order[field] if r[0] not in [1, 2, 3, 4] or r[1] in existing_ids]
                    pos_order.write({field: filtered_vals})
                    order[field] = []

            del order['uuid']
            del order['access_token']
            pos_order.write(order)

        pos_order._link_combo_items(combo_child_uuids_by_parent_uuid)

        self = self.with_company(pos_order.company_id)
        self._process_payment_lines(order, pos_order, pos_session, draft)

        return pos_order._process_saved_order(draft)
