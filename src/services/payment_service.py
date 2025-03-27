import qrcode
from io import BytesIO
import base64
from alipay import AliPay
from wechatpy.pay import WeChatPay
from src.config.payment import (
    ALIPAY_APP_ID,
    ALIPAY_PRIVATE_KEY,
    ALIPAY_PUBLIC_KEY,
    WECHAT_APP_ID,
    WECHAT_MCH_ID,
    WECHAT_API_KEY
)

class PaymentService:
    @staticmethod
    def generate_test_qr(order_id: str, amount: float) -> str:
        """生成测试用的支付二维码"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(f"测试支付订单：{order_id}\n金额：¥{amount}")
        qr.make(fit=True)
        
        # 修正：使用 qr.make_image() 而不是 qrcode.make_image()
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"

    @staticmethod
    async def create_wechat_payment(order):
        # 测试模式下使用测试二维码
        if not WECHAT_APP_ID or WECHAT_APP_ID == '你的微信APP_ID':
            return PaymentService.generate_test_qr(order['id'], order['amount'])

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
        
        return result["code_url"]

    @staticmethod
    async def create_alipay_payment(order):
        # 测试模式下使用测试二维码
        if not ALIPAY_APP_ID or ALIPAY_APP_ID == '你的支付宝APP_ID':
            return PaymentService.generate_test_qr(order['id'], order['amount'])

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
        
        return result["qr_code"]