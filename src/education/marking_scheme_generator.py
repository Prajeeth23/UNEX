import re
from typing import List
from src.education.schema_validator import Answer, MarkingStep

class MarkingSchemeGenerator:
    """Extracts step-wise marking rubrics from answer texts."""
    
    def generate_scheme(self, answers: List[Answer]) -> List[Answer]:
        for ans in answers:
            # Look for patterns like "[1 mark]", "(0.5m)", "+1 for formula"
            pattern = r'\[(\d+\.?\d*)\s*m(?:arks?)?\]|\((\d+\.?\d*)\s*m(?:arks?)?\)'
            matches = list(re.finditer(pattern, ans.text, re.IGNORECASE))
            
            if matches:
                steps = []
                last_idx = 0
                for match in matches:
                    marks = float(match.group(1) or match.group(2))
                    step_text = ans.text[last_idx:match.start()].strip()
                    if not step_text:
                        step_text = "Step marks"
                        
                    steps.append(MarkingStep(step_description=step_text, marks_awarded=marks))
                    last_idx = match.end()
                    
                ans.marking_scheme = steps
                
        return answers
