from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from automation.lead_processor import LeadProcessor
from bitrix24.client import Bitrix24Client
from ai_services.openai_service import OpenAIService
from ai_services.claude_service import ClaudeService

app = FastAPI(title="AI Integration Platform")

lead_processor = LeadProcessor()
bitrix = Bitrix24Client()
openai_service = OpenAIService()
claude_service = ClaudeService()

class LeadWebhook(BaseModel):
    lead_id: int

class AnalyzeRequest(BaseModel):
    text: str

class OfferRequest(BaseModel):
    lead_id: int
    products: list[str]

@app.get("/")
def root():
    return {"message": "AI Integration Platform API", "status": "running"}

@app.post("/webhook/bitrix/lead")
def process_lead_webhook(data: LeadWebhook):
    """Webhook для обработки новых лидов из Bitrix24"""
    try:
        result = lead_processor.process_new_lead(data.lead_id)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze-request")
def analyze_customer_request(request: AnalyzeRequest):
    """Анализ запроса клиента через Claude"""
    try:
        analysis = claude_service.analyze_customer_request(request.text)
        return {"success": True, "analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-offer")
def generate_offer(request: OfferRequest):
    """Генерация коммерческого предложения"""
    try:
        offer = lead_processor.generate_offer_for_lead(
            request.lead_id, 
            request.products
        )
        return {"success": True, "offer": offer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/leads")
def get_leads():
    """Получить список лидов из Bitrix24"""
    try:
        leads = bitrix.get_leads()
        return {"success": True, "leads": leads}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
