from typing import List, Dict
from src.education.schema_validator import Question, Answer, MarkingStep
import re

class AnswerKeyMapper:
    """Maps extracted Answer text to extracted Questions using Question IDs."""
    
    def map_answers(self, questions: List[Question], answer_text: str) -> List[Answer]:
        answers = []
        
        # Similar regex to split answers by Q1, Q2, etc.
        pattern = r'(?m)^(?:Ans(?:wer)?\s*\d+\.?|Sol(?:ution)?\s*\d+\.?|\d+\.)'
        chunks = re.split(pattern, answer_text)
        headers = re.findall(pattern, answer_text)
        
        ans_dict = {}
        if len(headers) == len(chunks) - 1:
            for i in range(1, len(chunks)):
                header = headers[i-1].strip(' .')
                q_id = re.sub(r'[^0-9]', '', header) or str(i)
                ans_dict[q_id] = chunks[i].strip()
                
        # Now map to questions
        for q in questions:
            ans_text = ans_dict.get(q.id, "Answer not found.")
            answers.append(Answer(
                question_id=q.id,
                text=ans_text,
                confidence=1.0 if q.id in ans_dict else 0.0
            ))
            
        return answers
