import re
import json
from typing import List
from src.education.schema_validator import Question, Section, QuestionType
from src.llm.ollama_client import OllamaProvider

class QuestionExtractor:
    def __init__(self):
        self.llm = OllamaProvider() # Local Qwen for extraction fallback
        
    async def extract_questions(self, text: str) -> List[Question]:
        """
        Uses a combination of Regex and LLM to extract questions.
        For MVP, we use regex to chunk and LLM to parse complex ones.
        """
        # A simple regex to split by Q1, Q2, etc.
        # Matches "Q1.", "Q 1.", "Question 1", "1." at start of line
        pattern = r'(?m)^(?:Q\s*\d+\.?|Question\s*\d+\.?|\d+\.)'
        
        chunks = re.split(pattern, text)
        # The first chunk is usually metadata/instructions
        metadata_chunk = chunks[0] if len(chunks) > 0 else ""
        
        questions = []
        
        # We need the actual question numbers. Let's find them.
        q_headers = re.findall(pattern, text)
        
        if len(q_headers) == len(chunks) - 1:
            for i in range(1, len(chunks)):
                header = q_headers[i-1].strip(' .')
                q_id = re.sub(r'[^0-9]', '', header) or str(i)
                q_text = chunks[i].strip()
                
                q = self._parse_single_question(q_id, q_text)
                questions.append(q)
        else:
            # Fallback to LLM for the entire block if regex failed badly
            print("[QuestionExtractor] Regex chunking failed. Using LLM fallback...")
            q = await self._extract_via_llm(text)
            if q:
                questions.extend(q)
                
        return questions
        
    def _parse_single_question(self, q_id: str, text: str) -> Question:
        """Parses a single regex chunk into a Question object."""
        # Check for marks
        marks_match = re.search(r'\[(\d+)\s*marks?\]|\((\d+)\s*m\)', text, re.IGNORECASE)
        marks = float(marks_match.group(1) or marks_match.group(2)) if marks_match else None
        
        # Clean text
        clean_text = re.sub(r'\[\d+\s*marks?\]|\(\d+\s*m\)', '', text, flags=re.IGNORECASE).strip()
        
        # Check for MCQ options (A, B, C, D)
        options = []
        opt_pattern = r'(?m)^\s*(?:[A-D]\)|[a-d]\.)\s*(.+)'
        opts = re.findall(opt_pattern, clean_text)
        if opts:
            options = [o.strip() for o in opts]
            clean_text = re.sub(opt_pattern, '', clean_text).strip()
            q_type = QuestionType.MCQ
        else:
            if len(clean_text) > 200:
                q_type = QuestionType.LONG_ANSWER
            else:
                q_type = QuestionType.SHORT_ANSWER
                
        return Question(
            id=q_id,
            text=clean_text,
            marks=marks,
            question_type=q_type,
            options=options if options else None
        )
        
    async def _extract_via_llm(self, text: str) -> List[Question]:
        """Calls the local LLM to extract JSON."""
        prompt = f"""
        Extract all educational questions from the following text into a JSON array.
        Each object must have: 'id' (string), 'text' (string), 'marks' (number, optional), 'question_type' (string), 'options' (array of strings, if MCQ).
        
        TEXT:
        {text[:4000]} # Limit to avoid context overflow
        """
        try:
            # We enforce JSON response format if supported, or just parse Markdown JSON
            res = await self.llm.agenerate(prompt)
            # Find json block
            start = res.find('[')
            end = res.rfind(']') + 1
            if start != -1 and end != 0:
                data = json.loads(res[start:end])
                questions = []
                for item in data:
                    questions.append(Question(**item))
                return questions
        except Exception as e:
            print(f"[QuestionExtractor] LLM Extraction failed: {e}")
            
        return []
