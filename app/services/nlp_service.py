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
    Extracts the most important keywords from text using noun chunks.
    Filters out stopwords and short tokens.
    """
    if not text or not text.strip():
        return []

    doc = nlp(text)

    keywords = list({
        chunk.text.lower().strip()
        for chunk in doc.noun_chunks
        if len(chunk.text.strip()) > 3 and not chunk.root.is_stop
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
    Named Entity Recognition (NER) — finds people, places, dates, and organizations.
    """
    if not text or not text.strip():
        return []

    doc = nlp(text)
    entities = []
    seen = set()  

    for ent in doc.ents:
        clean_text = ent.text.strip()
        if clean_text and clean_text not in seen:
            entities.append({
                "text": clean_text,
                "label": ent.label_,
                "description": spacy.explain(ent.label_) or ent.label_
            })
            seen.add(clean_text)

    return entities


def analyze_sentiment(text: str) -> Dict:
    """
    Enhanced sentiment analysis accounting for positive/negative word matches
    as well as negations ("not", "never", "no", "n't").
    """
    if not text or not text.strip():
        return {"label": "NEUTRAL", "score": 0.5}

    positive_words = {
        "good", "great", "excellent", "amazing", "wonderful",
        "fantastic", "best", "love", "perfect", "brilliant",
        "outstanding", "superb", "positive", "happy", "success",
        "successful", "innovative", "efficient", "effective", "growth",
        "profit", "strong", "benefit", "improved", "advantage"
    }
    negative_words = {
        "bad", "terrible", "awful", "horrible", "worst",
        "hate", "poor", "negative", "fail", "failed", "failure",
        "problem", "issue", "error", "wrong", "difficult", "hard",
        "loss", "decline", "risk", "damage", "corrupt", "defect"
    }
    negations = {"not", "never", "no", "neither", "nor", "n't"}

    doc = nlp(text.lower())
    tokens = [token.text for token in doc]

    pos_score = 0
    neg_score = 0

    for i, token in enumerate(tokens):
        # Check if preceding word is a negation
        is_negated = (i > 0 and tokens[i - 1] in negations)

        if token in positive_words:
            if is_negated:
                neg_score += 1.5
            else:
                pos_score += 1.0
        elif token in negative_words:
            if is_negated:
                pos_score += 1.5
            else:
                neg_score += 1.0

    total = pos_score + neg_score

    if total == 0:
        return {"label": "NEUTRAL", "score": 0.5}

    ratio = pos_score / total

    if ratio >= 0.6:
        return {"label": "POSITIVE", "score": round(ratio, 4)}
    elif ratio <= 0.4:
        return {"label": "NEGATIVE", "score": round(1 - ratio, 4)}
    else:
        return {"label": "NEUTRAL", "score": 0.5}


def summarize_text(text: str) -> str:
    """
    Extractive summarization — scores sentences based on keyword match & position.
    """
    if not text or not text.strip():
        return ""

    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 15]

    if len(sentences) <= 2:
        return text.strip()

    keywords = set(extract_keywords(text, top_n=15))
    sentence_scores = {}

    for idx, sent in enumerate(sentences):
        score = 0
        sent_doc = nlp(sent.lower())
        for token in sent_doc:
            if token.text in keywords:
                score += 1
        # Give slight boost to leading sentences
        if idx == 0:
            score += 0.5
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
    Runs unified NLP analysis pipeline safely.
    """
    sentiment_result = analyze_sentiment(text)

    return {
        "summary": summarize_text(text),
        "keywords": extract_keywords(text),
        "entities": extract_entities(text),
        "sentiment": sentiment_result["label"],
        "sentiment_score": sentiment_result["score"]
    }