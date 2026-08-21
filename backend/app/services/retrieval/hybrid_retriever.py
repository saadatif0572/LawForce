import re
import math
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from backend.app.core.config import settings
from backend.app.services.embeddings.embedding_service import EmbeddingService

logger = logging.getLogger("lawverse.retriever")

class HybridRetriever:
    """
    Hybrid Legal Retrieval Engine combining:
    1. Dense Semantic Retrieval via Qdrant query_points
    2. Sparse Lexical / Exact Match Retrieval for Sections, Articles, and Statutes
    3. Reciprocal Rank Fusion (RRF)
    4. Jurisdictional & Metadata Filtering
    """

    def __init__(self):
        from backend.app.core.qdrant_client_factory import get_qdrant_client
        self.client = get_qdrant_client()
        self.collection_name = settings.QDRANT_COLLECTION

    def search(
        self,
        query: str,
        jurisdiction_filter: Optional[str] = None,
        province_filter: Optional[str] = None,
        doc_type_filter: Optional[str] = None,
        top_k: int = 8
    ) -> List[Dict[str, Any]]:
        """
        Executes hybrid dense + sparse retrieval with Reciprocal Rank Fusion (RRF).
        """
        query_info = self.parse_legal_query(query)
        dense_results = self._dense_search(query, query_info, jurisdiction_filter, province_filter, doc_type_filter, limit=30)
        sparse_results = self._sparse_search(query, query_info, jurisdiction_filter, province_filter, limit=30)
        
        # Fuse results with RRF
        fused = self._reciprocal_rank_fusion(dense_results, sparse_results, rrf_k=60)
        
        # Deduplicate by section/chunk
        seen_chunks = set()
        deduped = []
        for item in fused:
            chunk_id = item["payload"]["chunk_id"]
            if chunk_id not in seen_chunks:
                seen_chunks.add(chunk_id)
                deduped.append(item)
            if len(deduped) >= top_k:
                break
                
        return deduped

    def parse_legal_query(self, query: str) -> Dict[str, Any]:
        """Detects language, legal sections, articles, statute mentions, and jurisdictions."""
        lang = "ur" if re.search(r'[\u0600-\u06FF]', query) else "en"
        
        # Extract section/article/rule citations (e.g. "Section 302", "Article 199", "Order 39", "498", "دفعہ 302", "آرٹیکل 199")
        sec_match = re.search(r'(?:section|sec|دفعہ|article|art|آرٹیکل|order|rule|رول)\s*([0-9A-Za-z\-\(\)\s&]+?)(?=\s+(?:of|in|under|cpc|ppc|crpc|constitution|family|act|ord|19\d\d|20\d\d|$|[,\.\?]))', query, re.IGNORECASE)
        exact_section = sec_match.group(1).strip() if sec_match else None
        
        # Direct number extraction fallback if specific keywords exist
        if not exact_section:
            direct_num = re.search(r'\b(302|497|498|154|199|184|420|375|17|117|42|54|10|73|114|14|20|5|25|6|7|372|34|3|9|13|28|40|4|11|12|15)\b', query)
            if direct_num:
                exact_section = direct_num.group(1)

        # Detect province mentions
        prov = None
        lower_q = query.lower()
        if "punjab" in lower_q or "پنجاب" in lower_q:
            prov = "punjab"
        elif "sindh" in lower_q or "سندھ" in lower_q:
            prov = "sindh"
        elif "khyber" in lower_q or "kp" in lower_q or "kpk" in lower_q or "خیبر" in lower_q or "پختونخوا" in lower_q:
            prov = "khyber_pakhtunkhwa"
        elif "balochistan" in lower_q or "بلوچستان" in lower_q:
            prov = "balochistan"

        # Statute keywords
        statute_hints = []
        if "penal" in lower_q or "ppc" in lower_q or "تعزیرات" in lower_q or "قتل" in lower_q or "qatl" in lower_q:
            statute_hints.append("penal")
        if "criminal" in lower_q or "crpc" in lower_q or "فوجداری" in lower_q or "bail" in lower_q or "ضمانت" in lower_q or "fir" in lower_q:
            statute_hints.append("criminal")
        if "civil" in lower_q or "cpc" in lower_q or "دیوانی" in lower_q or "injunction" in lower_q:
            statute_hints.append("civil")
        if "constitution" in lower_q or "آئین" in lower_q or "writ" in lower_q or "habeas" in lower_q:
            statute_hints.append("constitution")
        if "family" in lower_q or "خاندان" in lower_q or "khula" in lower_q or "خلع" in lower_q or "dower" in lower_q or "talaq" in lower_q:
            statute_hints.append("family")
        if "peca" in lower_q or "cyber" in lower_q or "defamation" in lower_q or "harassment" in lower_q:
            statute_hints.append("electronic")
        if "specific relief" in lower_q:
            statute_hints.append("specific_relief")
        if "tenancy" in lower_q or "batai" in lower_q or "مزارع" in lower_q:
            statute_hints.append("tenancy")
        if "land revenue" in lower_q or "mutation" in lower_q or "انتقال" in lower_q:
            statute_hints.append("revenue")
        if "shahadat" in lower_q or "evidence" in lower_q or "witness" in lower_q or "ثبوت" in lower_q or "گواہ" in lower_q:
            statute_hints.append("shahadat")
        if "consumer" in lower_q or "صارف" in lower_q:
            statute_hints.append("consumer")

        return {
            "language": lang,
            "exact_section": exact_section,
            "detected_province": prov,
            "statute_hints": statute_hints,
            "keywords": [w.lower() for w in re.findall(r'\w+', query) if len(w) > 2]
        }

    def _dense_search(self, query: str, query_info: dict, jurisdiction: Optional[str], province: Optional[str], doc_type: Optional[str], limit: int) -> List[Dict[str, Any]]:
        query_vector = EmbeddingService.get_embedding(query)
        
        must_conditions = []
        if jurisdiction and jurisdiction.lower() not in ["all", "any"]:
            must_conditions.append(
                qmodels.FieldCondition(key="jurisdiction", match=qmodels.MatchValue(value=jurisdiction.lower()))
            )
        if province:
            must_conditions.append(
                qmodels.FieldCondition(key="province", match=qmodels.MatchValue(value=province.lower()))
            )
        if doc_type:
            must_conditions.append(
                qmodels.FieldCondition(key="document_type", match=qmodels.MatchValue(value=doc_type.lower()))
            )

        q_filter = qmodels.Filter(must=must_conditions) if must_conditions else None
        
        try:
            # In qdrant-client >=1.10+, query_points is the primary dense retrieval interface
            res = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                query_filter=q_filter,
                limit=limit
            )
            return [{"payload": point.payload, "score": point.score or 0.5, "source": "dense"} for point in res.points]
        except Exception as e:
            logger.warning(f"Dense search in Qdrant fallback: {e}")
            return []

    def _sparse_search(self, query: str, query_info: dict, jurisdiction: Optional[str], province: Optional[str], limit: int) -> List[Dict[str, Any]]:
        """Exact statutory and keyword lexical retrieval matching across points."""
        keywords = query_info["keywords"]
        exact_sec = query_info["exact_section"]
        hints = query_info["statute_hints"]
        
        try:
            scroll_result, _ = self.client.scroll(
                collection_name=self.collection_name,
                limit=1800,
                with_payload=True,
                with_vectors=False
            )
            
            scored_candidates = []
            for point in scroll_result:
                payload = point.payload
                text_lower = payload.get("text", "").lower()
                title_lower = payload.get("canonical_title", "").lower()
                doc_id = payload.get("document_id", "").lower()
                sec_num = str(payload.get("section_number") or payload.get("article_number") or "")
                
                # Check jurisdiction filter
                if jurisdiction and jurisdiction.lower() not in ["all", "any"]:
                    if payload.get("jurisdiction", "").lower() != jurisdiction.lower():
                        continue
                if province:
                    if (payload.get("province") or "").lower() != province.lower():
                        continue
                        
                score = 0.0
                
                # Exact section match boost
                if exact_sec:
                    clean_exact = exact_sec.lower().replace(" ", "")
                    clean_sec = sec_num.lower().replace(" ", "")
                    if clean_exact == clean_sec or clean_exact in clean_sec:
                        score += 15.0
                    elif exact_sec.lower() in text_lower or f"section {exact_sec}" in text_lower or f"article {exact_sec}" in text_lower:
                        score += 8.0

                # Statute category hint boost
                for hint in hints:
                    if hint in doc_id or hint in title_lower:
                        score += 6.0
                        
                # Keyword matches
                for kw in keywords:
                    if kw in title_lower:
                        score += 2.0
                    if kw in text_lower:
                        score += 0.8
                        
                if score > 0.0:
                    scored_candidates.append({
                        "payload": payload,
                        "score": score,
                        "source": "sparse"
                    })
                    
            scored_candidates.sort(key=lambda x: x["score"], reverse=True)
            return scored_candidates[:limit]
        except Exception as e:
            logger.warning(f"Sparse search error: {e}")
            return []

    @staticmethod
    def _reciprocal_rank_fusion(dense_hits: List[Dict], sparse_hits: List[Dict], rrf_k: int = 60) -> List[Dict[str, Any]]:
        scores = {}
        payloads = {}
        
        # Rank sparse (given high weight for exact legal sections)
        for rank, item in enumerate(sparse_hits):
            cid = item["payload"]["chunk_id"]
            scores[cid] = scores.get(cid, 0.0) + (1.5 / (rrf_k + rank + 1))
            payloads[cid] = item["payload"]

        # Rank dense
        for rank, item in enumerate(dense_hits):
            cid = item["payload"]["chunk_id"]
            scores[cid] = scores.get(cid, 0.0) + (1.0 / (rrf_k + rank + 1))
            payloads[cid] = item["payload"]
            
        # Sort by fused score
        sorted_ids = sorted(scores.keys(), key=lambda k: scores[k], reverse=True)
        
        max_score = max(scores.values()) if scores else 1.0
        results = []
        for cid in sorted_ids:
            norm_score = round(min(1.0, scores[cid] / (max_score + 1e-6) * 0.92 + 0.08), 3)
            results.append({
                "payload": payloads[cid],
                "relevance_score": norm_score,
                "fused_rank_score": scores[cid]
            })
            
        return results
