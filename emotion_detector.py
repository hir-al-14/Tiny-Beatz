import streamlit as st
from transformers import pipeline

@st.cache_resource
def load_emotion_model():
    return pipeline(
        "text-classification",
        model="monologg/bert-base-cased-goemotions-original",
        top_k=None
    )

def detect_emotion(text, classifier):
    results = classifier(text)[0]
    top_emotion = max(results, key=lambda x: x['score'])
    return top_emotion['label'], top_emotion['score'], results[:5]