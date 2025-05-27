from typing import Dict, Any, Optional
from pydantic import BaseModel

class WhatsAppMessage(BaseModel):
    client_id: int
    message: str

class WhatsAppTemplate(BaseModel):
    client_id: int
    template_name: str
    template_params: Optional[Dict[str, Any]] = None

class WhatsAppOrderNotification(BaseModel):
    client_id: int
    order_number: str
    status: str

class WhatsAppPaymentNotification(BaseModel):
    client_id: int
    order_number: str
    amount: float
    payment_method: str

class WhatsAppShippingNotification(BaseModel):
    client_id: int
    order_number: str
    tracking_code: str
    carrier: str

class WhatsAppPromotionNotification(BaseModel):
    client_id: int
    promotion_title: str
    promotion_description: str
    valid_until: str 