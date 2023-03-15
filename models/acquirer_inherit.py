from odoo import models, fields, api
from odoo.osv import expression


class RestrictAcquirer(models.Model):
    _inherit = "payment.provider"
    _description = "Restrict Payment Acquirer"

    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    main_currency_id = fields.Many2one(related='company_id.currency_id')
    minimum_amount = fields.Monetary(string="Minimum Amount", currency_field='main_currency_id')
    maximum_amount = fields.Monetary(string="Maximum Amount", currency_field='main_currency_id')

    @api.model
    def _get_compatible_providers(
            self, company_id, partner_id, amount, currency_id=None, force_tokenization=False,
            is_express_checkout=False, is_validation=False, **kwargs):
        domain = ['&', ('state', 'in', ['enabled', 'test']), ('company_id', '=', company_id)]
        currency = self.env['res.currency'].browse(currency_id).exists()
        if not is_validation and currency:  # The currency is required to convert the amount.
            company = self.env['res.company'].browse(company_id).exists()
            date = fields.Date.context_today(self)
            converted_amount = currency._convert(amount, company.currency_id, company, date)
            # print(converted_amount)
            domain = expression.AND([
                domain, ['&', '|','&',
                         ('minimum_amount', '<=', converted_amount),
                         ('maximum_amount', '>=', converted_amount),
                         ('maximum_amount', '=', 0),
                         ('minimum_amount', '<=', converted_amount)
                         ]
            ])
        compatible_providers = self.env['payment.provider'].search(domain)
        return compatible_providers
