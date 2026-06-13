from src.education.schema_validator import EducationalJSON, QuestionType
from typing import Dict, Any

class PaperAnalyzer:
    @staticmethod
    def analyze(data: EducationalJSON) -> Dict[str, Any]:
        total_questions = len(data.questions)
        for section in data.sections:
            total_questions += len(section.questions)
            
        type_distribution = {}
        total_marks = 0.0
        
        def count_q(q):
            nonlocal total_marks
            t = q.question_type.value
            type_distribution[t] = type_distribution.get(t, 0) + 1
            if q.marks:
                total_marks += q.marks
                
        for q in data.questions:
            count_q(q)
            
        for s in data.sections:
            for q in s.questions:
                if hasattr(q, 'question_type'):
                    count_q(q)
                    
        return {
            "total_questions": total_questions,
            "total_marks_calculated": total_marks,
            "question_types": type_distribution,
            "metadata": data.paper_metadata.model_dump()
        }
