import stripe
from alipay import AliPay
from wechatpy.pay import WeChatPay
from config.payment import (
    STRIPE_SECRET_KEY,
    ALIPAY_APP_ID,
    ALIPAY_PRIVATE_KEY,
    ALIPAY_PUBLIC_KEY,
    WECHAT_APP_ID,
    WECHAT_MCH_ID,
    WECHAT_API_KEY
)

class PaymentService:
    @staticmethod
    async def create_wechat_payment(order):
        wechat_pay = WeChatPay(
            appid=WECHAT_APP_ID,
            mch_id=WECHAT_MCH_ID,
            api_key=WECHAT_API_KEY
        )
        
        result = wechat_pay.order.create(
            trade_type="NATIVE",
            body=f"音频转写服务-{order['plan_name']}",
            total_fee=int(order['amount'] * 100),
            out_trade_no=order['id']
        )
        
        return {
            "type": "qrcode",
            "data": result["code_url"]
        }

    @staticmethod
    async def create_alipay_payment(order):
        alipay = AliPay(
            appid=ALIPAY_APP_ID,
            app_private_key_string=ALIPAY_PRIVATE_KEY,
            alipay_public_key_string=ALIPAY_PUBLIC_KEY
        )
        
        result = alipay.api_alipay_trade_precreate(
            subject=f"音频转写服务-{order['plan_name']}",
            out_trade_no=order['id'],
            total_amount=order['amount']
        )
        
        return {
            "type": "qrcode",
            "data": result["qr_code"]
        }

    @staticmethod
    async def create_stripe_payment(order):
        stripe.api_key = STRIPE_SECRET_KEY
        
        payment_intent = stripe.PaymentIntent.create(
            amount=int(order['amount'] * 100),
            currency='usd',
            metadata={'order_id': order['id']}
        )
        
        return {
            "type": "stripe",
            "client_secret": payment_intent.client_secret
        }