import httpx
from typing import Optional, Dict, Any
from fastapi import HTTPException, status

from app.core.config import settings
from app.models.client import Client

class WhatsAppService:
    def __init__(self):
        self.base_url = settings.WHATSAPP_API_URL
        self.token = settings.WHATSAPP_API_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    async def send_message(
        self,
        to: str,
        message: str,
        template_name: Optional[str] = None,
        template_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Envia uma mensagem para um número de WhatsApp.
        
        Args:
            to: Número do destinatário no formato internacional (ex: 5511999999999)
            message: Mensagem a ser enviada
            template_name: Nome do template a ser usado (opcional)
            template_params: Parâmetros do template (opcional)
        """
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            # Remove caracteres não numéricos do número
            to = ''.join(filter(str.isdigit, to))
            
            # Adiciona o código do país se não estiver presente
            if not to.startswith('55'):
                to = f"55{to}"
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {"body": message}
            }
            
            # Se um template for especificado, usa o template ao invés da mensagem simples
            if template_name:
                payload = {
                    "messaging_product": "whatsapp",
                    "to": to,
                    "type": "template",
                    "template": {
                        "name": template_name,
                        "language": {
                            "code": "pt_BR"
                        }
                    }
                }
                
                if template_params:
                    payload["template"]["components"] = [
                        {
                            "type": "body",
                            "parameters": [
                                {"type": "text", "text": value}
                                for value in template_params.values()
                            ]
                        }
                    ]
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao enviar mensagem WhatsApp: {str(e)}"
            )

    async def send_order_notification(self, client: Client, order_number: str, status: str) -> Dict[str, Any]:
        """
        Envia uma notificação sobre o status do pedido para o cliente.
        """
        message = (
            f"Olá {client.name}! Seu pedido #{order_number} foi atualizado.\n"
            f"Status atual: {status}\n"
            f"Acompanhe seu pedido em: {settings.FRONTEND_URL}/orders/{order_number}"
        )
        
        return await self.send_message(
            to=client.phone,
            message=message
        )

    async def send_payment_notification(
        self,
        client: Client,
        order_number: str,
        amount: float,
        payment_method: str
    ) -> Dict[str, Any]:
        """
        Envia uma notificação sobre o pagamento do pedido.
        """
        message = (
            f"Olá {client.name}! Recebemos seu pagamento.\n"
            f"Pedido: #{order_number}\n"
            f"Valor: R$ {amount:.2f}\n"
            f"Método: {payment_method}\n"
            f"Obrigado pela preferência!"
        )
        
        return await self.send_message(
            to=client.phone,
            message=message
        )

    async def send_shipping_notification(
        self,
        client: Client,
        order_number: str,
        tracking_code: str,
        carrier: str
    ) -> Dict[str, Any]:
        """
        Envia uma notificação sobre o envio do pedido.
        """
        message = (
            f"Olá {client.name}! Seu pedido #{order_number} foi enviado.\n"
            f"Transportadora: {carrier}\n"
            f"Código de rastreio: {tracking_code}\n"
            f"Acompanhe seu pedido em: {settings.FRONTEND_URL}/orders/{order_number}"
        )
        
        return await self.send_message(
            to=client.phone,
            message=message
        )

    async def send_promotion_notification(
        self,
        client: Client,
        promotion_title: str,
        promotion_description: str,
        valid_until: str
    ) -> Dict[str, Any]:
        """
        Envia uma notificação sobre uma promoção.
        """
        message = (
            f"Olá {client.name}! Temos uma promoção especial para você!\n"
            f"Promoção: {promotion_title}\n"
            f"{promotion_description}\n"
            f"Válido até: {valid_until}\n"
            f"Acesse: {settings.FRONTEND_URL}/promotions"
        )
        
        return await self.send_message(
            to=client.phone,
            message=message
        )

# Instância global do serviço
whatsapp_service = WhatsAppService() 