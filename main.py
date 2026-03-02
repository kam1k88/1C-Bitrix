from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from automation.lead_processor import LeadProcessor
from automation.mass_operations import MassOperations
from bitrix24.sdk_client import Bitrix24SDKClient, create_client_from_webhook
from ai_services.openai_service import OpenAIService
from ai_services.claude_service import ClaudeService
from config.settings import settings
import logging

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Integration Platform",
    description="Автоматизация бизнес-процессов с Bitrix24 и AI",
    version="2.0.0"
)

# Инициализация сервисов
try:
    lead_processor = LeadProcessor()
    mass_ops = MassOperations()
    openai_service = OpenAIService()
    claude_service = ClaudeService()
    
    # Создаем отдельный клиент для API endpoints
    if settings.BITRIX24_WEBHOOK_URL:
        bitrix = create_client_from_webhook(
            settings.BITRIX24_WEBHOOK_URL,
            prefer_api_version=settings.BITRIX24_API_VERSION
        )
    else:
        bitrix = Bitrix24SDKClient(
            domain=settings.BITRIX24_DOMAIN,
            auth_token=settings.BITRIX24_ACCESS_TOKEN,
            auth_type="oauth",
            client_id=settings.BITRIX24_CLIENT_ID,
            client_secret=settings.BITRIX24_CLIENT_SECRET,
            refresh_token=settings.BITRIX24_REFRESH_TOKEN,
            prefer_api_version=settings.BITRIX24_API_VERSION
        )
    
    logger.info("All services initialized successfully with b24pysdk")
    
except Exception as e:
    logger.error(f"Failed to initialize services: {e}")
    raise

class LeadWebhook(BaseModel):
    lead_id: int

class AnalyzeRequest(BaseModel):
    text: str

class OfferRequest(BaseModel):
    lead_id: int
    products: list[str]

class BatchUpdateRequest(BaseModel):
    lead_ids: list[int]
    status: str


@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "message": "AI Integration Platform API v2.0",
        "status": "running",
        "sdk": "b24pysdk",
        "api_version": settings.BITRIX24_API_VERSION
    }


@app.post("/webhook/bitrix/lead")
def process_lead_webhook(data: LeadWebhook):
    """
    Webhook для обработки новых лидов из Bitrix24
    Автоматически анализирует лид через AI
    """
    try:
        result = lead_processor.process_new_lead(data.lead_id)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error processing lead webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze-request")
def analyze_customer_request(request: AnalyzeRequest):
    """Анализ запроса клиента через Claude"""
    try:
        analysis = claude_service.analyze_customer_request(request.text)
        return {"success": True, "analysis": analysis}
    except Exception as e:
        logger.error(f"Error analyzing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-offer")
def generate_offer(request: OfferRequest):
    """Генерация коммерческого предложения для лида"""
    try:
        offer = lead_processor.generate_offer_for_lead(
            request.lead_id, 
            request.products
        )
        return {"success": True, "offer": offer}
    except Exception as e:
        logger.error(f"Error generating offer: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/leads")
def get_leads(status: str = None, limit: int = 50):
    """
    Получить список лидов из Bitrix24
    
    Args:
        status: Фильтр по статусу (опционально)
        limit: Максимальное количество записей
    """
    try:
        filter_params = {"STATUS_ID": status} if status else None
        leads = bitrix.get_leads(filter_params=filter_params, limit=limit)
        return {"success": True, "leads": leads, "count": len(leads)}
    except Exception as e:
        logger.error(f"Error getting leads: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/deals")
def get_deals(stage: str = None, limit: int = 50):
    """
    Получить список сделок из Bitrix24
    
    Args:
        stage: Фильтр по стадии (опционально)
        limit: Максимальное количество записей
    """
    try:
        filter_params = {"STAGE_ID": stage} if stage else None
        deals = bitrix.get_deals(filter_params=filter_params, limit=limit)
        return {"success": True, "deals": deals, "count": len(deals)}
    except Exception as e:
        logger.error(f"Error getting deals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/batch/analyze-leads")
def batch_analyze_leads():
    """
    Массовый анализ всех новых лидов через AI
    Использует batch API для оптимизации
    """
    try:
        result = mass_ops.analyze_all_new_leads()
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error in batch analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/batch/update-status")
def batch_update_status(request: BatchUpdateRequest):
    """
    Массовое обновление статуса лидов
    
    Args:
        lead_ids: Список ID лидов
        status: Новый статус
    """
    try:
        result = mass_ops.batch_update_leads_status(request.lead_ids, request.status)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error in batch update: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/batch/create-deals")
def batch_create_deals(lead_ids: list[int]):
    """
    Массовое создание сделок из лидов
    
    Args:
        lead_ids: Список ID лидов
    """
    try:
        result = mass_ops.batch_create_deals_from_leads(lead_ids)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error in batch deal creation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
def health_check():
    """Проверка состояния всех сервисов"""
    health = {
        "api": "ok",
        "bitrix24": "unknown",
        "openai": "unknown",
        "anthropic": "unknown"
    }
    
    # Проверка Bitrix24
    try:
        bitrix.get_current_user()
        health["bitrix24"] = "ok"
    except Exception as e:
        health["bitrix24"] = f"error: {str(e)}"
    
    # Проверка OpenAI
    try:
        if settings.OPENAI_API_KEY:
            health["openai"] = "configured"
    except:
        health["openai"] = "not configured"
    
    # Проверка Anthropic
    try:
        if settings.ANTHROPIC_API_KEY:
            health["anthropic"] = "configured"
    except:
        health["anthropic"] = "not configured"
    
    return {"success": True, "health": health}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
