# -*- coding: utf-8 -*-

def set_default_email_button_color(env):
    """Set company email button color to #418319 after install/upgrade.

    Odoo post-init hooks in recent versions receive a single ``env`` argument.
    """
    env["res.company"].search([]).write({
        "secondary_color": "#418319",
        "email_secondary_color": "#418319",
    })