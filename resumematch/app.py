import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from utils.pdf_reader import extract_text_from_pdf
from utils.text_cleaner import clean_text
from utils.matcher import calculate_similarity, extract_skills, load_skills


# Page configuration
st.set_page_config(page_title="AI Resume Matcher", page_icon="📄", layout="wide")

# Header
st.title("📄 AI Resume vs Job Description Matcher")
st.info("Upload resumes and compare them with a job description using NLP.")

st.divider()

# Upload section
st.subheader("Upload Data")

col1, col2 = st.columns(2)

with col1:
    resume_files = st.file_uploader(
        "Upload Resumes",
        type=["pdf"],
        accept_multiple_files=True
    )

with col2:
    jd = st.text_area("Paste Job Description")


# Analyze button
if st.button("Analyze"):

    if resume_files and jd:

        with st.spinner("Analyzing resumes..."):

            try:
                jd_clean = clean_text(jd)

                skills_list = load_skills()

                results = []
                best_resume_skills = []
                best_missing_skills = []

                for file in resume_files:

                    resume_text = extract_text_from_pdf(file)

                    if not resume_text:
                        continue

                    resume_clean = clean_text(resume_text)

                    score = calculate_similarity(resume_clean, jd_clean)
                    score = round(score * 100, 2)

                    resume_skills = extract_skills(resume_clean, skills_list)
                    jd_skills = extract_skills(jd_clean, skills_list)

                    st.write("Detected JD Skills:", jd_skills)
                    st.write("Detected Resume Skills:", resume_skills)

                    missing_skills = list(set(jd_skills) - set(resume_skills))

                    st.write("Missing Skills:", missing_skills)

                    results.append({
                        "Resume": file.name,
                        "Score": score
                    })

                    if not best_resume_skills or score > max(r["Score"] for r in results[:-1]):
                        best_resume_skills = resume_skills
                        best_missing_skills = missing_skills

                if not results:
                    st.error("No readable resumes uploaded.")
                    st.stop()

                st.divider()

                # Ranking table
                df = pd.DataFrame(results)
                df = df.sort_values(by="Score", ascending=False)

                st.subheader("🏆 Candidate Ranking")
                st.dataframe(df, use_container_width=True)

                # Top candidate score
                top_score = df.iloc[0]["Score"]

                st.metric("Top Resume Match", f"{top_score}%")
                st.progress(int(top_score))

                if top_score > 75:
                    st.success("Strong Match")
                elif top_score > 50:
                    st.warning("Moderate Match")
                else:
                    st.error("Low Match")

                st.divider()

                # Skill display
                col3, col4 = st.columns(2)

                with col3:
                    st.markdown("### Matched Skills")
                    if best_resume_skills:
                        st.write(", ".join(best_resume_skills))
                    else:
                        st.write("No matching skills detected.")

                with col4:
                    st.markdown("### Missing Skills")
                    if best_missing_skills:
                        st.write(", ".join(best_missing_skills))
                    else:
                        st.write("No major skills missing.")

                st.divider()

                # Charts
                st.subheader("📊 Skills Analysis")

                chart_col1, chart_col2 = st.columns(2)

                with chart_col1:
                    data = {
                        "Category": ["Matched Skills", "Missing Skills"],
                        "Count": [len(best_resume_skills), len(best_missing_skills)]
                    }

                    chart_df = pd.DataFrame(data)
                    st.bar_chart(chart_df.set_index("Category"))

                with chart_col2:
                    sizes = [len(best_resume_skills), len(best_missing_skills)]
                    labels = ["Matched", "Missing"]

                    fig, ax = plt.subplots()
                    ax.pie(sizes, labels=labels, autopct='%1.1f%%')
                    st.pyplot(fig)

                st.divider()

                # Resume ranking chart
                st.subheader("📈 Resume Score Comparison")
                st.bar_chart(df.set_index("Resume"))

            except Exception as e:
                st.error(f"Error processing resumes: {e}")

    else:
        st.warning("Please upload at least one resume and paste a job description.")