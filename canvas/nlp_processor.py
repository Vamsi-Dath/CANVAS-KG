from pathlib import Path
import spacy
import logging
from utils.helper import remove_duplicates_from_e_csv, save_e_to_csv
from schema.entity import Entity

logging.basicConfig(level=logging.DEBUG)
nlp = spacy.load("en_core_web_md")

def nlp_process_entities(entities: list[Entity], input_text_file_path: str, openai_model=None ) -> list[Entity]:
    processed_entities = []
    for entity in entities:
        if len(entity.name.split()) < 3:
            processed_entities.append(entity)
            continue

        doc = nlp(entity.name)
        noun_chunks = list(doc.noun_chunks)
        hint_text = f"{entity.category}, {entity.type.replace('_', ' ')}"

        hint_doc = nlp(hint_text)
        selected_chunk = max(noun_chunks, key=lambda x: x.similarity(hint_doc), default=doc).text

        original_name = doc.text
        entity.name = selected_chunk
        entity.properties.update({
            "original_name": original_name,
            "noun_chunks": [chunk.text for chunk in noun_chunks]
        })

        logging.info(f"Processed Entity: '{original_name}' to '{selected_chunk}'")
        processed_entities.append(entity)

    dir = Path("./data/output/")/Path(input_text_file_path).stem/Path("nlp_processed_entities")

    if openai_model:
        dir = dir / openai_model
    else:
        dir = dir / "llama3.1_8b"

    dir.mkdir(parents=True, exist_ok=True)
    save_e_to_csv(dir, "nlp_processed_entities.csv", processed_entities)
    remove_duplicates_from_e_csv(
        dir / "nlp_processed_entities.csv",
        dir / "nlp_processed_entities_dedup.csv"
    )
    return processed_entities