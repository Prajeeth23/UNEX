from src.education.schema_validator import EducationalJSON
import json
import os

class JSONExporter:
    @staticmethod
    def export(data: EducationalJSON, filepath: str):
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(data.model_dump_json(indent=2))
            
    @staticmethod
    def dumps(data: EducationalJSON) -> str:
        return data.model_dump_json(indent=2)
