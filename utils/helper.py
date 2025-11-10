import subprocess
import time
import logging
import csv
from pathlib import Path
from schema.entity import Entity

logging.basicConfig(level=logging.DEBUG)

def run_ollama(model:str, system_prompt:str, user_prompt:str, max_tries=10, timeout=300) -> str:
    if system_prompt:
        prompt = f"<|system|>\n{system_prompt}\n<|end|>\n<|user|>\n{user_prompt}\n<|end|>\n"
    else:
        prompt = f"<|user|>\n{user_prompt}\n<|end|>\n"
    response = None
    while response is None and max_tries > 0:
        max_tries -= 1
        try:
            result = subprocess.run(
                ["ollama", "run", model],
                input=f"{prompt}".encode("utf-8"),
                capture_output=True,
                check=True,
                timeout=timeout
            )
            response = result.stdout.decode("utf-8").strip()
        except subprocess.CalledProcessError as e:
            logging.warning(f"Ollama Error: {e}. Re-run in 5 seconds... Attempts left: {max_tries}")
            time.sleep(5)
        except KeyboardInterrupt:
            logging.warning("User KeyboardInterrupt.")
            raise
        except Exception as e:
            logging.error(f"Error: {e}. Re-run in 5 seconds... Attempts left: {max_tries}")
            time.sleep(5)

    if response is None:
        raise RuntimeError("Failed to get response from Ollama after max_tries.")
    
    logging.debug(f"Model: {model}\n""Prompt:\n {user_prompt}\n""Result: {response}\n")
    return response

def validate_entity(entity_json: str) -> Entity:
    try:
        entity = Entity.model_validate_json(entity_json)
        logging.debug(f"Validated Entity: {entity}")
        return entity
    except Exception as e:
        logging.error(f"Validation error: {e}")
        raise

def save_e_to_csv(output_dir: str, output_file_name: str, entities: list[Entity]) -> None:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_file_path = Path(output_dir)/output_file_name
    file_exists = output_file_path.is_file()
    try:
        with open(output_file_path, mode='a', newline='', encoding='utf-8') as f:
            fieldnames = Entity.model_fields.keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            for entity in entities:
                writer.writerow(entity.model_dump())
        logging.info(f"Entities: {len(entities)} saved to {output_file_path}")
    except Exception as e:
        logging.error(f"Error saving to {output_file_path}: {e}")
        raise

def remove_duplicates_from_e_csv(input_file_path: str, output_file_path: str) -> None:
    #convert everything to lowercase for comparison
    try:
        unique_entities = {}
        with open(input_file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row['name'].lower(), row['type'].lower())
                if key not in unique_entities:
                    unique_entities[key] = row
            
        with open(output_file_path, mode='w', newline='', encoding='utf-8') as f:
            fieldnames = ['idx', 'name', 'type', 'confidence', 'description', 'properties']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for entity in unique_entities.values():
                writer.writerow(entity)
        logging.info(f"Removed duplicates, no. of unique entities: {len(unique_entities)}")

    except Exception as e:
        logging.error(f"Error removing duplicates from {input_file_path} to {output_file_path}: {e}")
        raise