import spacy
import logging
from utils.helper import remove_duplicates_from_e_csv, save_e_to_csv

logging.basicConfig(level=logging.DEBUG)
nlp = spacy.load("en_core_web_md")

def nlp_process_entities(entities):
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

    save_e_to_csv("./data/output/", "nlp_processed_entities.csv", processed_entities)
    remove_duplicates_from_e_csv(
        "./data/output/nlp_processed_entities.csv",
        "./data/output/nlp_processed_entities_dedup.csv"
    )
    return processed_entities