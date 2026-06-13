from pydantic import BaseModel, Field
from typing import List, Optional, Union
from enum import Enum

class QuestionType(str, Enum):
    MCQ = "MCQ"
    FILL_IN_BLANKS = "Fill in the Blanks"
    MATCH_FOLLOWING = "Match the Following"
    TRUE_FALSE = "True/False"
    SHORT_ANSWER = "Short Answer"
    LONG_ANSWER = "Long Answer"
    NUMERICAL = "Numerical"
    CASE_STUDY = "Case Study"
    UNKNOWN = "Unknown"

class SubQuestion(BaseModel):
    id: str = Field(description="The sub-question identifier, e.g., 'a', 'i'")
    text: str = Field(description="The text of the sub-question")
    marks: Optional[float] = Field(None, description="Marks allocated to this sub-question")
    question_type: QuestionType = Field(default=QuestionType.UNKNOWN)
    options: Optional[List[str]] = Field(None, description="Options if MCQ")

class ChoiceGroup(BaseModel):
    """Represents an internal choice, e.g. 'Attempt any one of the following'"""
    description: Optional[str] = Field(None, description="E.g., 'OR'")
    questions: List[Union['Question', SubQuestion]]

class Question(BaseModel):
    id: str = Field(description="The primary question identifier, e.g., '1', 'Q2'")
    text: str = Field(description="The text of the primary question")
    marks: Optional[float] = Field(None, description="Total marks allocated to this question")
    question_type: QuestionType = Field(default=QuestionType.UNKNOWN)
    options: Optional[List[str]] = Field(None, description="Options if MCQ")
    sub_questions: Optional[List[Union[SubQuestion, ChoiceGroup]]] = Field(default_factory=list)

class Section(BaseModel):
    id: str = Field(description="Section identifier, e.g., 'Section A'")
    instructions: Optional[str] = Field(None, description="Instructions for the section")
    total_marks: Optional[float] = Field(None, description="Total marks for the section")
    questions: List[Union[Question, ChoiceGroup]] = Field(default_factory=list)

class PaperMetadata(BaseModel):
    title: Optional[str] = Field(None)
    subject: Optional[str] = Field(None)
    grade: Optional[str] = Field(None)
    board: Optional[str] = Field(None) # CBSE, ICSE, State Board, etc.
    year: Optional[str] = Field(None)
    total_marks: Optional[float] = Field(None)
    duration_minutes: Optional[int] = Field(None)
    general_instructions: Optional[str] = Field(None)

class MarkingStep(BaseModel):
    step_description: str
    marks_awarded: float

class Answer(BaseModel):
    question_id: str
    text: str
    marking_scheme: Optional[List[MarkingStep]] = Field(default_factory=list)
    confidence: float = Field(1.0, description="Confidence score of the extraction and mapping")

class EducationalJSON(BaseModel):
    paper_metadata: PaperMetadata = Field(default_factory=PaperMetadata)
    sections: List[Section] = Field(default_factory=list)
    questions: List[Question] = Field(default_factory=list) # Fallback if no sections
    answer_key: List[Answer] = Field(default_factory=list)
    
# Fix forward references for recursive types
ChoiceGroup.model_rebuild()
Question.model_rebuild()
