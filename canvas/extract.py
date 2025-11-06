from utils.helper import run_ollama, validate_entity, save_e_to_csv
from schema.entity import Entity
import logging

logger = logging.getLogger(__name__)
class Extractor:
    def __init__(self, input_text_file_path: str, output_dir: str, output_file_name: str) -> None:
        self.input_text_file_path = input_text_file_path
        self.output_dir = output_dir
        self.output_file_name = output_file_name

    def extract_json_objects(self, text: str) -> list[str]:
        json_objects = []
        start = None
        count = 0
        for i, ch in enumerate(text):
            if ch == '{':
                if not count:
                    start = i
                count += 1
            elif ch == '}':
                count -= 1
                if not count and start is not None:
                        json_objects.append(text[start:i+1])
                        start = None
        return json_objects
    
    def extract_entities(self) -> list[Entity]:
        raw_entities = []
        for idx, line in enumerate(open(self.input_text_file_path, 'r', encoding='utf-8')):
            if not line.strip():
                logger.info(f"Line {idx} skipped: Empty line.")
                continue
            system_prompt = f"""
            You are an expert entity extraction model. Extract each entity from the given text according to the Entity schema.\n
            Provide the output in JSON format. Don't include any explanations. structure the JSON as per the Entity schema.\n
            Entity Schema:
            {{
                "idx": int,
                "name": str,
                "type": str,
                "confidence": float (0.0 to 1.0),
                "description": str (optional), use empty string if not known,
                "properties": dict (optional), use empty dict {{}} if not known
            }}
            Rules:
            1. Always return a list of JSON objects.
            2. All objects must strictly follow the schema above.
            3. Ensure no null values; use "" or {{}} for missing optional fields.
            4. Output valid JSON only.
            Output: list of JSON objects strictly following the Entity schema.
            """
            user_prompt = f"Input Text:\n{line.strip()}"

            response = run_ollama("llama2", system_prompt, user_prompt)
            logger.info(f"Line {idx} run status: Completed")
            raw_jsons = self.extract_json_objects(response)
            logging.info(f"\tLine {idx} extracted entities count: {len(raw_jsons)}")
            raw_entities = raw_entities + raw_jsons

        entities = []
        for e in raw_entities:
            try:
                entities.append(validate_entity(e))
            except Exception as ve:
                logging.warning(f"Skipping Entity: {e}, due to failed pydantic validation")
                continue
        logging.info(f"Total validated entities count: {len(entities)}\n")

        if self.output_dir and self.output_file_name and self.output_file_name.endswith('.csv'):
            save_e_to_csv(self.output_dir, self.output_file_name, entities)

        return entities
    