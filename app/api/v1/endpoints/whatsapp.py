from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.models.client import Client
from app.services.whatsapp import whatsapp_service
from app.schemas.whatsapp import (
    WhatsAppMessage,
    WhatsAppTemplate,
    WhatsAppOrderNotification,
    WhatsAppPaymentNotification,
    WhatsAppShippingNotification,
    WhatsAppPromotionNotification
)

router = APIRouter()

@router.post("/send", response_model=Dict[str, Any])
async def send_message(
    *,
    db: Session = Depends(deps.get_db),
    message: WhatsAppMessage,
    current_user: User = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    Envia uma mensagem WhatsApp para um cliente.
    """
    client = db.query(Client).filter(Client.id == message.client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    return await whatsapp_service.send_message(
        to=client.phone,
        message=message.message
    )

@router.post("/send-template", response_model=Dict[str, Any])
async def send_template(
    *,
    db: Session = Depends(deps.get_db),
    template: WhatsAppTemplate,
    current_user: User = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    Envia uma mensagem usando um template do WhatsApp.
    """
    client = db.query(Client).filter(Client.id == template.client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    return await whatsapp_service.send_message(
        to=client.phone,
        message="",  # Mensagem vazia pois usaremos template
        template_name=template.template_name,
        template_params=template.template_params
    )

@router.post("/notify-order", response_model=Dict[str, Any])
async def notify_order(
    *,
    db: Session = Depends(deps.get_db),
    notification: WhatsAppOrderNotification,
    current_user: User = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    Envia uma notificação sobre o status do pedido.
    """
    client = db.query(Client).filter(Client.id == notification.client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    return await whatsapp_service.send_order_notification(
        client=client,
        order_number=notification.order_number,
        status=notification.status
    )

@router.post("/notify-payment", response_model=Dict[str, Any])
async def notify_payment(
    *,
    db: Session = Depends(deps.get_db),
    notification: WhatsAppPaymentNotification,
    current_user: User = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    Envia uma notificação sobre o pagamento do pedido.
    """
    client = db.query(Client).filter(Client.id == notification.client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    return await whatsapp_service.send_payment_notification(
        client=client,
        order_number=notification.order_number,
        amount=notification.amount,
        payment_method=notification.payment_method
    )

@router.post("/notify-shipping", response_model=Dict[str, Any])
async def notify_shipping(
    *,
    db: Session = Depends(deps.get_db),
    notification: WhatsAppShippingNotification,
    current_user: User = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    Envia uma notificação sobre o envio do pedido.
    """
    client = db.query(Client).filter(Client.id == notification.client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    return await whatsapp_service.send_shipping_notification(
        client=client,
        order_number=notification.order_number,
        tracking_code=notification.tracking_code,
        carrier=notification.carrier
    )

@router.post("/notify-promotion", response_model=Dict[str, Any])
async def notify_promotion(
    *,
    db: Session = Depends(deps.get_db),
    notification: WhatsAppPromotionNotification,
    current_user: User = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    Envia uma notificação sobre uma promoção.
    """
    client = db.query(Client).filter(Client.id == notification.client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    return await whatsapp_service.send_promotion_notification(
        client=client,
        promotion_title=notification.promotion_title,
        promotion_description=notification.promotion_description,
        valid_until=notification.valid_until
    ) 