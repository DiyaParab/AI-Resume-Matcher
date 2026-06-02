from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re


def calculate_similarity(resume, jd):

    vectorizer = TfidfVectorizer()

    vectors = vectorizer.fit_transform([resume, jd])

    similarity = cosine_similarity(vectors)[0][1]

    return similarity


def extract_skills(text, skills_list):

    text = text.lower()
    found = []

    for skill in skills_list:
        if skill in text:
            found.append(skill)

    return list(set(found))


def load_skills():

    with open("skills_db.txt", "r") as f:
        skills = [line.strip().lower() for line in f if line.strip()]

    return skills