# Copyright 2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    def _compute_price_rule(
                self, products, quantity, currency=None, uom=None, date=False, compute_price=True,
                **kwargs
        ):
        products_super = self.env[products._name]
        for product in products:
            if not product in product.split_pack_products()[0]:
                products_super += product
        res = super(Pricelist, self)._compute_price_rule(
            products_super, quantity, currency, uom, date, **kwargs
        )
        for product in products:
            if product in product.split_pack_products()[0]:
                res[product.id] = (
                    product.price_compute("list_price")[product.id],
                    False,
                )
        return res

    #