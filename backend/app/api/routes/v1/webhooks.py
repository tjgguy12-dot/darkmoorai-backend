"""
Webhook Routes
"""

from fastapi import APIRouter, Request
import json

router = APIRouter()


@router.post("/stripe")
async def stripe_webhook(request: Request):
    """Stripe webhook endpoint"""
    body = await request.body()
    return {"status": "received"}


@router.post("/sendgrid")
async def sendgrid_webhook(request: Request):
    """SendGrid webhook endpoint"""
    body = await request.body()
    return {"status": "received"}