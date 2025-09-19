/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { user } from "@web/core/user";
import { useService } from "@web/core/utils/hooks";

export class SaleDashboard extends Component {
    setup() {
        // Odoo services
        this.orm = useService("orm");
        this.action = useService("action");

        // Reactive state
        this.state = useState({
            from_date: this._getLastWeek(),
            to_date: this._getToday(),
            sale_order_count: 0,
            account_move_count: 0,
            stock_picking_count: 0,
            new_customer_count: 0,
            sale_order_amount: 0,
            account_move_amount: 0,
            not_stock_picking_count: 0,
            retained_customer_count: 0,
            payment_details: [],
            new_customer_ids: [],
            retained_customer_ids: [],
        });

        // Initial fetch
        onWillStart(async () => {
            await this.fetchData();
        });
    }

    /**
     * Return today’s date (YYYY-MM-DD).
     */
    _getToday() {
        return new Date().toISOString().slice(0, 10);
    }

     _getLastWeek() {
        const today = new Date();
        today.setDate(today.getDate() - 7);
        return today.toISOString().slice(0, 10);
    }

    /**
     * Fetch dashboard data from backend.
     */
    async fetchData() {
        const values = await this.orm.call("sale.order", "get_data_based_date", [
            this.state.from_date,
            this.state.to_date,
        ]);
        if (values) {
            Object.assign(this.state, values);
        }
    }

    /**
     * Trigger when date fields change.
     */
     async onDateChange() {
        if (this.state.from_date && this.state.to_date) {
            await this.fetchData();
        }
    }

    /**
     * Generic record opening helper.
     */
    async openAction(name, model, domain) {
        const hasAccess = await user.hasGroup("hr.group_hr_user");
        if (!hasAccess) {
            return;
        }
        this.action.doAction({
            name,
            type: "ir.actions.act_window",
            res_model: model,
            views: [[false, "list"], [false, "form"]],
            target: "current",
            domain,
        });
    }

    // ----------------- CLICK HANDLERS -----------------
    onSaleOrders() {
        this.openAction("Sale Orders", "sale.order", [
            ["state", "=", "sale"],
            ["date_order", ">=", this.state.from_date],
            ["date_order", "<=", this.state.to_date],
        ]);
    }

    onInvoices() {
        this.openAction("Invoices", "account.move", [
            ["state", "=", "posted"],
            ["invoice_date", ">=", this.state.from_date],
            ["invoice_date", "<=", this.state.to_date],
            ["move_type", "=", "out_invoice"],
        ]);
    }

    onDelivered() {
        this.openAction("Delivered", "stock.picking", [
            ["state", "=", "done"],
            ["date_done", ">=", this.state.from_date],
            ["date_done", "<=", this.state.to_date],
            ["name", "like", "OUT"],
        ]);
    }

    onNotDelivered() {
        this.openAction("Not Delivered", "stock.picking", [
            ["state", "!=", "done"],
            ["scheduled_date", ">=", this.state.from_date],
            ["scheduled_date", "<=", this.state.to_date],
            ["name", "like", "OUT"],
        ]);
    }

        onNewCustomers() {
        this.openAction("New Customers", "res.partner", [
            ["id", "in", this.state.new_customer_ids]
        ]);
    }

    onRetainedCustomers() {
        this.openAction("Retained Customers", "res.partner", [
            ["id", "in", this.state.retained_customer_ids]
        ]);
    }
}

// Register template
SaleDashboard.template = "gl_sale_dashboard.SaleDashboard";
registry.category("actions").add("sale_dashboard", SaleDashboard);
