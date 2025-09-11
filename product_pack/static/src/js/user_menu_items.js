/** @odoo-module **/

import { registry } from "@web/core/registry";

// Remove the "My Odoo.com account" item
const userMenuRegistry = registry.category("user_menuitems");

userMenuRegistry.remove("odoo_account");  // "account" is the ID of the Odoo.com account item


