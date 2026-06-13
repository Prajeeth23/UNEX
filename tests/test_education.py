import pytest
import os
import asyncio
from src.education.schema_validator import EducationalJSON, Question, QuestionType
from src.education.question_extractor import QuestionExtractor
from src.education.document_classifier import DocumentClassifier, DocumentType
from src.education.answer_key_mapper import AnswerKeyMapper
from src.education.marking_scheme_generator import MarkingSchemeGenerator

def test_document_classification():
    q_paper = "Maximum Marks: 100\nTime Allowed: 3 Hours\nQ1. What is gravity?\nQ2. Explain photosynthesis [5 marks]."
    assert DocumentClassifier.classify(q_paper) == DocumentType.QUESTION_PAPER
    
    ans_key = "Suggested Answers / Solutions\nAns 1. Gravity is a force.\nAns 2. Photosynthesis is..."
    assert DocumentClassifier.classify(ans_key) == DocumentType.ANSWER_KEY
    
    marking = "Marking Scheme / Rubric\n+1 for formula\n+2 for calculation."
    assert DocumentClassifier.classify(marking) == DocumentType.MARKING_SCHEME

def test_question_extraction_regex():
    extractor = QuestionExtractor()
    text = "Q1. What is the capital of France?\nA) Paris\nB) London\nC) Rome\nD) Berlin\n\nQ2. Explain Newton's laws. [10 marks]"
    questions = asyncio.run(extractor.extract_questions(text))
    
    assert len(questions) == 2
    assert questions[0].id == "1"
    assert questions[0].question_type == QuestionType.MCQ
    assert len(questions[0].options) == 4
    
    assert questions[1].id == "2"
    assert questions[1].marks == 10.0
    assert questions[1].question_type == QuestionType.SHORT_ANSWER

def test_answer_key_mapping():
    mapper = AnswerKeyMapper()
    questions = [
        Question(id="1", text="What is gravity?"),
        Question(id="2", text="Explain Newton's laws.")
    ]
    
    ans_text = "Ans 1. Gravity is a fundamental force.\nAns 2. Here are the three laws..."
    answers = mapper.map_answers(questions, ans_text)
    
    assert len(answers) == 2
    assert answers[0].question_id == "1"
    assert "fundamental force" in answers[0].text
    assert answers[1].question_id == "2"

def test_marking_scheme_generation():
    generator = MarkingSchemeGenerator()
    from src.education.schema_validator import Answer
    
    answers = [
        Answer(question_id="1", text="Formula F=ma [1 mark]\nCalculation gives 10N [2 marks]")
    ]
    
    answers = generator.generate_scheme(answers)
    assert len(answers[0].marking_scheme) == 2
    assert answers[0].marking_scheme[0].marks_awarded == 1.0
    assert answers[0].marking_scheme[1].marks_awarded == 2.0
