"""offer_card_render.py"""
from __future__ import annotations
import json
from app.services.HTML.model_HTML import OfferCard
from app.services.HTML.offer_card import OFFER_CARD

def render_offer_card(card: OfferCard) -> str:
    return OFFER_CARD.replace("__OFFER_DATA__", json.dumps(card, ensure_ascii=False))
