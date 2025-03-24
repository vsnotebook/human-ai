SUBSCRIPTION_PLANS = {
    'basic': {
        'name': '基础版',
        'minutes': 100,
        'price': {
            'CNY': 99,
            'USD': 15,
        },
        'description': '每月100分钟转写时长'
    },
    'pro': {
        'name': '专业版',
        'minutes': 300,
        'price': {
            'CNY': 259,
            'USD': 39,
        },
        'description': '每月300分钟转写时长'
    },
    'enterprise': {
        'name': '企业版',
        'minutes': 1000,
        'price': {
            'CNY': 699,
            'USD': 99,
        },
        'description': '每月1000分钟转写时长'
    }
}

PAYMENT_METHODS = {
    'wechat': {
        'name': '微信支付',
        'currencies': ['CNY'],
        'icon': 'wechat-pay.png'
    },
    'alipay': {
        'name': '支付宝',
        'currencies': ['CNY'],
        'icon': 'alipay.png'
    },
    'stripe': {
        'name': 'Stripe',
        'currencies': ['USD'],
        'icon': 'stripe.png'
    }
}