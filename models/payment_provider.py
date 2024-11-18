# Inherit the payment.provider class and implement the discount methods

class PaymentProvider:
    _name = "Payment Provider"
    _description = "Payment Provider"   
    _inherit = ['payment.provider']

    product = many2one('product.product', 'Product')
    discount_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percentage', 'Percentage'),
    ], string='Discount Type')
    discount_percentage = fields.Float('Discount Percentage')
    discount_fixed_amount = fields.Float('Discount Fixed Amount')
 
    def get_discount(self):
        if self.discount_type == 'fixed':
            return self.discount_fixed_amount
        elif self.discount_type == 'percentage':
            return self.discount_percentage
        return 0.0
    

    # <100 constrain on discount

    _sql_constraints = [
        ('discount_check', 'CHECK(discount_percentage < 100)', 'The discount must be less than 100'),
    ]
