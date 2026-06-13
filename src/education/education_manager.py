import os
from src.education.pdf_parser import PDFParser
from src.education.document_classifier import DocumentClassifier, DocumentType
from src.education.question_extractor import QuestionExtractor
from src.education.answer_key_mapper import AnswerKeyMapper
from src.education.marking_scheme_generator import MarkingSchemeGenerator
from src.education.schema_validator import EducationalJSON
from src.education.paper_analyzer import PaperAnalyzer
from src.education.json_exporter import JSONExporter

class EducationManager:
    """Orchestrates the entire PDF -> JSON pipeline."""
    
    def __init__(self):
        self.parser = PDFParser(use_ocr=True)
        self.extractor = QuestionExtractor()
        self.mapper = AnswerKeyMapper()
        self.scheme_gen = MarkingSchemeGenerator()
        
    async def process_pdf(self, pdf_path: str) -> EducationalJSON:
        print(f"[EducationManager] Parsing PDF: {pdf_path}")
        text = self.parser.extract_text(pdf_path)
        
        doc_type = DocumentClassifier.classify(text)
        print(f"[EducationManager] Detected Type: {doc_type}")
        
        json_data = EducationalJSON()
        
        if doc_type in [DocumentType.QUESTION_PAPER, DocumentType.UNKNOWN]:
            questions = await self.extractor.extract_questions(text)
            json_data.questions = questions
            
        elif doc_type == DocumentType.ANSWER_KEY:
            # If standalone answer key, we'd need a reference question paper.
            # For simplicity, we just extract text for now or map if provided in future APIs.
            pass
            
        return json_data
        
    def map_answer_key(self, json_data: EducationalJSON, answer_pdf_path: str) -> EducationalJSON:
        ans_text = self.parser.extract_text(answer_pdf_path)
        answers = self.mapper.map_answers(json_data.questions, ans_text)
        answers = self.scheme_gen.generate_scheme(answers)
        json_data.answer_key = answers
        return json_data
