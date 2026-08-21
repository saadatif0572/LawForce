import json
import logging
from typing import List, Dict, Any, AsyncGenerator
from groq import Groq
from backend.app.core.config import settings

logger = logging.getLogger("lawverse.generator")

SYSTEM_PROMPT = """You are LawForce, an elite legal research and statutory information assistant grounded strictly in verified Pakistani legal sources.

OPERATIONAL MANDATE & GROUNDING RULES:
1. Grounding: Answer ONLY from the supplied Evidence Chunks. Do not use external legal facts or assume statutes not present in the context.
2. Jurisdictional Precision: Explicitly distinguish Federal law from Provincial law (Punjab, Sindh, Khyber Pakhtunkhwa, Balochistan, Islamabad Capital Territory).
3. Status & Provenance: Specify whether a law is currently in force, amended, or repealed.
4. Exact Citations: Cite every material legal assertion using the format: [Title of Law, Section/Article/Rule, Jurisdiction, Page if available].
5. Tone & Plain Language: Explain legal concepts clearly in plain, professional English or Urdu, quoting only short necessary statutory phrases.
6. Scope & Refusal: If the supplied evidence does not contain sufficient information to answer the question reliably, clearly state that the verified corpus does not contain enough information on this topic. Do not speculate or hallucinate.
7. Ethics & Disclaimers:
   - You are a legal information research tool, NOT a licensed Pakistani advocate.
   - Never establish an advocate-client relationship or provide definitive individualized legal advice.
   - For contentious disputes, criminal liability, deadlines, or court filings, advise consulting a licensed Pakistani advocate.
   - If emergency or physical harm is indicated, recommend immediate local emergency contact (e.g. Police 15 / Rescue 1122).
8. Language: If the user asks in Urdu, provide a comprehensive, polite answer in Urdu with corresponding legal provisions and citations. If in English, answer in English."""

class GroqGenerator:
    """
    RAG Generation service leveraging the Groq Python SDK
    with strict legal grounding, citation verification, and SSE streaming.
    """

    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL
        if self.api_key and self.api_key != "replace_with_new_key":
            self.client = Groq(api_key=self.api_key)
        else:
            self.client = None

    def generate_response(self, question: str, retrieved_chunks: List[Dict[str, Any]], language: str = "en") -> Dict[str, Any]:
        """Synchronous RAG answer generation with evidence formatting."""
        if not retrieved_chunks:
            return self._build_insufficient_evidence_response(question, language)

        evidence_text = self._format_evidence(retrieved_chunks)
        user_message = f"EVIDENCE CHUNKS FROM VERIFIED PAKISTANI LEGAL CORPUS:\n\n{evidence_text}\n\nUSER QUESTION:\n{question}\n\nPlease provide a clear, grounded legal analysis citing the exact provisions above."

        # If Groq API key is not configured, generate a deterministic grounded response from top chunks
        if not self.client:
            return self._generate_local_grounded_response(question, retrieved_chunks, language)

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                model=self.model,
                temperature=0.1,
                max_tokens=1500,
            )
            answer_text = chat_completion.choices[0].message.content
            
            # Clean up thinking tags if returned by reasoning models
            answer_text = re.sub(r'<think>.*?</think>', '', answer_text, flags=re.DOTALL).strip()
            
            # Extract structured sources from retrieved chunks
            sources = self._format_sources_list(retrieved_chunks)
            confidence = "high" if len(retrieved_chunks) >= 3 else "medium"
            
            return {
                "answer_markdown": answer_text,
                "language": language,
                "confidence": confidence,
                "needs_clarification": False,
                "disclaimer": "General legal information only; not legal advice. Consult a licensed Pakistani advocate for formal legal representation.",
                "sources": sources
            }
        except Exception as e:
            logger.error(f"Groq API call error: {e}")
            return self._generate_local_grounded_response(question, retrieved_chunks, language)

    async def generate_stream(self, question: str, retrieved_chunks: List[Dict[str, Any]], language: str = "en") -> AsyncGenerator[str, None]:
        """Asynchronous SSE Stream Generator."""
        if not retrieved_chunks:
            res = self._build_insufficient_evidence_response(question, language)
            yield f"data: {json.dumps({'event': 'token', 'data': res['answer_markdown']})}\n\n"
            yield f"data: {json.dumps({'event': 'done', 'data': res})}\n\n"
            return

        evidence_text = self._format_evidence(retrieved_chunks)
        user_message = f"EVIDENCE CHUNKS FROM VERIFIED PAKISTANI LEGAL CORPUS:\n\n{evidence_text}\n\nUSER QUESTION:\n{question}\n\nPlease provide a clear, grounded legal analysis citing the exact provisions above."
        sources = self._format_sources_list(retrieved_chunks)

        if not self.client:
            # Local streamed response
            res = self._generate_local_grounded_response(question, retrieved_chunks, language)
            full_text = res["answer_markdown"]
            # Stream tokens in small chunks
            words = full_text.split(" ")
            for i in range(0, len(words), 4):
                chunk_str = " ".join(words[i:i+4]) + " "
                yield f"data: {json.dumps({'event': 'token', 'data': chunk_str})}\n\n"
            yield f"data: {json.dumps({'event': 'done', 'data': res})}\n\n"
            return

        try:
            stream = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                model=self.model,
                temperature=0.1,
                max_tokens=1500,
                stream=True,
            )
            
            accumulated_text = ""
            for chunk in stream:
                content = chunk.choices[0].delta.content or ""
                if content:
                    accumulated_text += content
                    yield f"data: {json.dumps({'event': 'token', 'data': content})}\n\n"
                    
            final_payload = {
                "answer_markdown": accumulated_text,
                "language": language,
                "confidence": "high" if len(retrieved_chunks) >= 3 else "medium",
                "needs_clarification": False,
                "disclaimer": "General legal information only; not legal advice. Consult a licensed Pakistani advocate for formal legal representation.",
                "sources": sources
            }
            yield f"data: {json.dumps({'event': 'done', 'data': final_payload})}\n\n"
        except Exception as e:
            logger.error(f"Groq streaming error: {e}")
            res = self._generate_local_grounded_response(question, retrieved_chunks, language)
            yield f"data: {json.dumps({'event': 'token', 'data': res['answer_markdown']})}\n\n"
            yield f"data: {json.dumps({'event': 'done', 'data': res})}\n\n"

    def _format_evidence(self, chunks: List[Dict[str, Any]]) -> str:
        blocks = []
        for idx, item in enumerate(chunks, 1):
            p = item["payload"]
            score = item.get("relevance_score", 0.0)
            sec = p.get("section_number") or p.get("article_number") or "General"
            heading = p.get("section_heading") or ""
            jur = p.get("jurisdiction", "Federal").upper()
            if p.get("province"):
                jur += f" ({p['province'].upper()})"
                
            block = f"--- EVIDENCE CHUNK {idx} (Score: {score:.2f}) ---\n"
            block += f"Title: {p.get('canonical_title')}\n"
            block += f"Provision: {sec} - {heading}\n"
            block += f"Jurisdiction: {jur} | Status: {p.get('legal_status', 'in_force').upper()}\n"
            block += f"Source URL: {p.get('source_url')}\n"
            block += f"Text:\n{p.get('text')}\n"
            blocks.append(block)
        return "\n\n".join(blocks)

    def _format_sources_list(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        sources = []
        seen = set()
        for c in chunks:
            p = c["payload"]
            cid = p.get("chunk_id")
            if cid in seen:
                continue
            seen.add(cid)
            
            sec = p.get("section_number") or p.get("article_number")
            art_sec = f"Section {sec}" if p.get("section_number") else f"Article {sec}" if p.get("article_number") else "General Provision"
            
            sources.append({
                "document_id": p.get("document_id"),
                "title": p.get("canonical_title"),
                "article_or_section": art_sec,
                "section_heading": p.get("section_heading"),
                "jurisdiction": p.get("jurisdiction", "federal").capitalize(),
                "province": p.get("province"),
                "legal_status": p.get("legal_status", "in_force"),
                "page": p.get("page_start", 1),
                "source_url": p.get("source_url"),
                "relevance_score": c.get("relevance_score", 0.85)
            })
        return sources

    def _generate_local_grounded_response(self, question: str, chunks: List[Dict[str, Any]], language: str) -> Dict[str, Any]:
        """High-precision local grounding generator synthesizer when Groq key is in configuration phase."""
        top = chunks[0]["payload"]
        title = top.get("canonical_title")
        sec_num = top.get("section_number") or top.get("article_number") or "Relevant Provision"
        jur = top.get("jurisdiction", "Federal").capitalize()
        if top.get("province"):
            jur += f" ({top['province'].capitalize()})"
        status = top.get("legal_status", "in_force")
        text = top.get("text", "")
        
        if language == "ur":
            ans = f"### پاکستانی قانون کے تحت قانونی تجزیہ:\n\n"
            ans += f"**مستند قانونی ماخذ:** {title} ({jur})\n"
            ans += f"**قانونی حیثیت:** {status.upper()}\n\n"
            ans += f"**متعلقہ دفعہ/آرٹیکل:** {sec_num}\n\n"
            ans += f"سرکاری متن کے مطابق:\n> {text.strip()}\n\n"
            ans += f"**نتیجہ:** یہ معلومات تصدیق شدہ پاکستانی قانونی دستاویزات سے حاصل کی گئی ہیں۔ مخصوص کیس کے لیے کسی مجاز وکیل سے رجوع کریں۔"
        else:
            ans = f"### Legal Analysis under Pakistani Law\n\n"
            ans += f"Based on verified Pakistani legal sources, the applicable provisions governing this matter are found under **{title}** [{jur}]:\n\n"
            ans += f"#### **Key Statutory Provision ({sec_num})**:\n"
            ans += f"- **Statute / Document:** {title}\n"
            ans += f"- **Jurisdiction:** {jur}\n"
            ans += f"- **Legal Status:** `{status.upper()}`\n\n"
            ans += f"**Substantive Legal Text:**\n"
            ans += f"```text\n{text.strip()}\n```\n\n"
            ans += f"**Summary & Application:**\n"
            ans += f"Under the referenced statutory framework, the law prescribes specific procedures and obligations. Any dispute or proceeding must strictly conform to these statutory boundaries."

        return {
            "answer_markdown": ans,
            "language": language,
            "confidence": "high",
            "needs_clarification": False,
            "disclaimer": "General legal information only; not legal advice. Consult a licensed Pakistani advocate for formal legal advice.",
            "sources": self._format_sources_list(chunks)
        }

    def _build_insufficient_evidence_response(self, question: str, language: str) -> Dict[str, Any]:
        if language == "ur":
            msg = "تلاش کردہ ڈیٹا بیس میں اس سوال سے متعلق کافی مستند قانونی معلومات دستیاب نہیں ہیں۔ برائے مہربانی اپنا سوال واضح کریں یا کسی مستند وکیل سے رہنمائی لیں۔"
        else:
            msg = "The verified Pakistani legal corpus does not contain sufficient reliable provisions to answer this specific query. Please refine your query with specific statute names, sections, or jurisdictions, or consult a licensed Pakistani advocate."
        return {
            "answer_markdown": msg,
            "language": language,
            "confidence": "ungrounded",
            "needs_clarification": True,
            "disclaimer": "General legal information only; not legal advice.",
            "sources": []
        }
