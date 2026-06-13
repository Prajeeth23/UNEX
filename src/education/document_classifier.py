import re

class DocumentType:
    QUESTION_PAPER = "Question Paper"
    ANSWER_KEY = "Answer Key"
    MARKING_SCHEME = "Marking Scheme"
    SYLLABUS = "Syllabus"
    UNKNOWN = "Unknown"

class DocumentClassifier:
    @staticmethod
    def classify(text: str) -> str:
        text_lower = text.lower()
        
        # Check first 2000 characters for title hints
        head = text_lower[:2000]
        
        if "marking scheme" in head or "rubric" in head or "step marks" in head:
            return DocumentType.MARKING_SCHEME
            
        if "answer key" in head or "solutions" in head or "suggested answers" in head:
            return DocumentType.ANSWER_KEY
            
        if "syllabus" in head or "curriculum" in head:
            return DocumentType.SYLLABUS
            
        # Count heuristic for Question Paper
        q_count = len(re.findall(r'\bq\d+|\bquestion\s*\d+', text_lower))
        marks_count = len(re.findall(r'\[\s*\d+\s*marks?\s*\]|\(\s*\d+\s*m\s*\)', text_lower))
        
        if q_count > 5 or marks_count > 3 or "time allowed" in head or "maximum marks" in head:
            return DocumentType.QUESTION_PAPER
            
        return DocumentType.UNKNOWN
