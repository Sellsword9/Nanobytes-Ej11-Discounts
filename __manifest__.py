{
        "name": "Ej11",
        "summary": "Ejercicio 11",
        "description": "Ejercicio 11 heredando website_sale",
        "author": "Yeray Romero",

        "application": True,

        "depends": [
            "base",
            "website_sale",
            "web",
            "portal",
            ],
        
        "data": [
            "views/payment_provider_form.xml",
            "views/payment_form_templates.xml",
            "views/total.xml"
            ],
        "assets": {
            "web.assets_frontend": [
                "ej11/static/src/js/provider_discount_widget.js",
                "ej11/static/src/js/provider_discount_widget.xml",
                ],
        },
        
        "installable": True,
}
