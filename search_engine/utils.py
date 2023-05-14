import io
import os
import tempfile
from typing import List
import PyPDF2
from sentence_transformers import SentenceTransformer
import numpy as np
import pinecone
from tqdm.auto import tqdm
from nltk.corpus import wordnet
import nltk
nltk.download('wordnet')
nltk.download('omw-1.4')
import spacy



nlp = spacy.load("en_core_web_sm")
def extract_entities(doc):
    entities = set()
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG", "GPE"]:
            entities.add(ent.text)
    return entities

def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())
    return list(synonyms)

def expand(query: str):
    synonyms = get_synonyms(query)
    if synonyms:
        expanded = query + " " + " ".join(synonyms)
    else:
        expanded = query
    return expanded


model = SentenceTransformer('distiluse-base-multilingual-cased-v2',device='cpu') # I have used Cpu instead of Gpu because of unavailability.
documents = []
embeddings = []

def extract_text(data: bytes, filename: str) -> str:
    if filename.lower().endswith(".pdf"):
        with tempfile.TemporaryFile() as temp:
            temp.write(data)
            temp.seek(0)
            reader = PyPDF2.PdfFileReader(temp)
            return " ".join([reader.getPage(i).extractText() for i in range(reader.getNumPages())])
    else:
        return data.decode("utf-8")

def process_data(text: str):
    
    global documents, embeddings,index
    document = text.split('.')
    index_name = 'para' # name of my defined index in my pinecone account
    

    pinecone.init(
        api_key="320f485d-2788-49a3-bf0d-89fd5db9f817",
        environment="us-west1-gcp-free"  #  api key 
    )
    
    
    
    
    print(document)
    
    if index_name not in pinecone.list_indexes():
        pinecone.create_index(index_name, dimension=512,metric="cosine")
   
    index = pinecone.Index(index_name)
    count = 0  
    batch_size = 16 
    
    for i in tqdm(range(0, len(document), batch_size)):
        
        i_end = min(i+batch_size, len(document))
        lines_batch = document[i: i+batch_size]
        ids_batch = [str(n) for n in range(i, i_end)]
        
        embeds =model.encode(lines_batch)
       
        meta = [{'text': line} for line in lines_batch]
        to_upsert = zip(ids_batch, embeds.tolist(), meta)
        index.upsert(vectors=list(to_upsert))
        

def search(query: str, top_k: int = 15) -> List[str]:
    global embeddings
    
    index_name = 'para' # name of my defined index
    pinecone.init(
        api_key="320f485d-2788-49a3-bf0d-89fd5db9f817",
        environment="us-west1-gcp-free"
    )
    index = pinecone.Index(index_name)
    expanded = expand(query)
    print(f"Original: {query}")
    print(f"Expanded: {expanded}")
    query = model.encode(expanded)
    res = index.query([query.tolist()], top_k=10, include_metadata=True)
    output = [i["metadata"]['text'].strip() for i in res['matches'] if i["metadata"]['text'].strip()]
    
    
    results = []
    for text in output:
        doc = nlp(text)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        results.append((text, entities))
    
    if len(results) < 9:
        results.append(('Sorry!!! But it seems we got no search results.', []))

    return results[:9]