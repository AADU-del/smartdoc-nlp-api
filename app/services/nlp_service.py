

import spacy
from typing import Dict, Any, List


try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    
    raise OSError(
        "spaCy model not found. Run: python -m spacy download en_core_web_sm"
    )


def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    """
    Extracts the most important keywords from text.
    Uses spaCy's noun chunks — phrases that act as nouns.
    Filters out stopwords (the, a, is, etc.) and short words.
    """
    doc = nlp(text)

    keywords = list({
        chunk.text.lower()
        for chunk in doc.noun_chunks
        if len(chunk.text) > 3 and not chunk.root.is_stop
    })

    keyword_freq = {kw: text.lower().count(kw) for kw in keywords}

  
    sorted_keywords = sorted(
        keyword_freq,
        key=lambda k: keyword_freq[k],
        reverse=True
    )
    return sorted_keywords[:top_n]


def extract_entities(text: str) -> List[Dict]:
    """
    Named Entity Recognition (NER) — finds real world objects in text.
    Examples:
    - "Google" → ORG (organization)
    - "Elon Musk" → PERSON
    - "India" → GPE (geopolitical entity)
    - "January 2024" → DATE
    - "$500" → MONEY
    spaCy identifies these automatically using its trained model.
    """
    doc = nlp(text)
    entities = []
    seen = set()  

    for ent in doc.ents:
       
        if ent.text not in seen:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "description": spacy.explain(ent.label_) or ent.label_
            })
            seen.add(ent.text)

    return entities


def analyze_sentiment(text: str) -> Dict:
    """
    Simple rule-based sentiment analysis using spaCy.
    Counts positive vs negative words to determine sentiment.
    For production, you'd use a HuggingFace model — but this
    works without downloading large ML models.
    """
   
    positive_words = {
        "good", "great", "excellent", "amazing", "wonderful",
        "fantastic", "best", "love", "perfect", "brilliant",
        "outstanding", "superb", "positive", "happy", "success",
        "successful", "innovative", "efficient", "effective"
    }
    negative_words = {
        "bad", "terrible", "awful", "horrible", "worst",
        "hate", "poor", "negative", "fail", "failed", "failure",
        "problem", "issue", "error", "wrong", "difficult", "hard"
    }

    doc = nlp(text.lower())
    tokens = {token.text for token in doc if not token.is_stop}

    pos_count = len(tokens & positive_words)
    neg_count = len(tokens & negative_words)
    total = pos_count + neg_count

    if total == 0:
        return {"label": "NEUTRAL", "score": 0.5}

    score = pos_count / total
    if score >= 0.6:
        return {"label": "POSITIVE", "score": round(score, 4)}
    elif score <= 0.4:
        return {"label": "NEGATIVE", "score": round(1 - score, 4)}
    else:
        return {"label": "NEUTRAL", "score": 0.5}


def summarize_text(text: str) -> str:
    """
    Extractive summarization — picks the most important sentences.
    Works by scoring sentences based on keyword frequency.
    No ML model needed — fast and works offline.
    For production, you'd use facebook/bart-large-cnn from HuggingFace.
    """
  
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 20]

    if len(sentences) <= 2:
        return text  

   
    keywords = set(extract_keywords(text, top_n=15))
    sentence_scores = {}

    for sent in sentences:
        score = 0
        sent_doc = nlp(sent.lower())
        for token in sent_doc:
            if token.text in keywords:
                score += 1
        sentence_scores[sent] = score

   
    top_sentences = sorted(
        sentence_scores,
        key=lambda s: sentence_scores[s],
        reverse=True
    )[:3]

   
    ordered = [s for s in sentences if s in top_sentences]
    return " ".join(ordered)


def full_analysis(text: str) -> Dict[str, Any]:
    """
    Runs ALL NLP tasks and returns unified results dict.
    This is what gets called by the background task after upload.
    """
    sentiment_result = analyze_sentiment(text)

    return {
        "summary": summarize_text(text),
        "keywords": extract_keywords(text),
        "entities": extract_entities(text),
        "sentiment": sentiment_result["label"],
        "sentiment_score": sentiment_result["score"]
    }