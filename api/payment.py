from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from services.payment_service import PaymentService
from services.firestore_service import FirestoreService
from utils.auth import get_current_user

router = APIRouter(prefix="/payment")

@router.post("/create")
async def create_payment(request: Request):
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    data = await request.json()
    payment_method = data.get("method")
    plan_id = data.get("plan_id")
    
    # 创建支付订单
    order = await FirestoreService.create_order(user["id"], plan_id)
    
    # 根据支付方式生成支付信息
    if payment_method == "wechat":
        payment_data = await PaymentService.create_wechat_payment(order)
    elif payment_method == "alipay":
        payment_data = await PaymentService.create_alipay_payment(order)
    elif payment_method == "stripe":
        payment_data = await PaymentService.create_stripe_payment(order)
    else:
        raise HTTPException(status_code=400, detail="Invalid payment method")
    
    return JSONResponse(content=payment_data)

@router.post("/notify/{payment_method}")
async def payment_notify(payment_method: str, request: Request):
    data = await request.json()
    
    if payment_method == "wechat":
        result = await PaymentService.handle_wechat_notify(data)
    elif payment_method == "alipay":
        result = await PaymentService.handle_alipay_notify(data)
    elif payment_method == "stripe":
        result = await PaymentService.handle_stripe_notify(data)
    else:
        raise HTTPException(status_code=400, detail="Invalid payment method")
    
    if result:
        return JSONResponse(content={"status": "success"})
    return JSONResponse(content={"status": "failed"})

@router.get("/status/{order_id}")
async def check_payment_status(order_id: str, request: Request):
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    status = await FirestoreService.get_order_status(order_id)
    return JSONResponse(content={"status": status})