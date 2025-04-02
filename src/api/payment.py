from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from src.services.payment_service import PaymentService
# from src.services.firestore_service import FirestoreService as DBService
from src.services.mongodb_service import MongoDBService as DBService
from src.utils.http_session_util import get_current_user

router = APIRouter(prefix="/payment")

@router.post("/create")
async def create_payment(request: Request):
    try:
        user = await get_current_user(request)
        if not user:
            raise HTTPException(status_code=401, detail="未登录")
        
        data = await request.json()
        payment_method = data.get("method")
        plan_id = data.get("plan_id")
        
        # 创建订单
        order = await DBService.create_order(user["id"], plan_id)
        
        # 生成支付二维码
        if payment_method == "wechat":
            qr_code = await PaymentService.create_wechat_payment(order)
        elif payment_method == "alipay":
            qr_code = await PaymentService.create_alipay_payment(order)
        else:
            raise HTTPException(status_code=400, detail="不支持的支付方式")
        
        return JSONResponse({
            "order_id": order["id"],
            "qr_code": qr_code,
            "amount": order["amount"]
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@router.get("/status/{order_id}")
async def check_payment_status(order_id: str, request: Request):
    try:
        user = await get_current_user(request)
        if not user:
            raise HTTPException(status_code=401, detail="未登录")
        
        status = await DBService.get_order_status(order_id)
        if status == "paid":
            # 激活订阅
            await DBService.activate_subscription(user["id"], order_id)
            
            # 获取订单详情，更新用户余额
            order_details = await DBService.get_order_details(order_id)
            if order_details:
                await DBService.update_user_balance(user["id"], order_details["plan_id"])
            
        return JSONResponse({"status": status})
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )