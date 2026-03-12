"""Streamlit app for building Google dorks from simple query inputs."""

import streamlit as st

st.set_page_config(page_title="Zwanski Dork Engine", page_icon="🔎", layout="centered")

st.title("🔎 Zwanski Dork Engine")
st.caption("Build Google dorks quickly from a base term and common filters.")

base_query = st.text_input("Base query", placeholder="e.g. inurl:admin")
site = st.text_input("Limit to site", placeholder="e.g. example.com")
filetype = st.text_input("File type", placeholder="e.g. pdf")
required_phrase = st.text_input("Exact phrase", placeholder="e.g. confidential")
exclude_terms = st.text_input("Exclude terms (comma-separated)", placeholder="login, test")

parts: list[str] = []
if base_query.strip():
    parts.append(base_query.strip())
if site.strip():
    parts.append(f"site:{site.strip()}")
if filetype.strip():
    parts.append(f"filetype:{filetype.strip()}")
if required_phrase.strip():
    parts.append(f'"{required_phrase.strip()}"')

for term in exclude_terms.split(","):
    term = term.strip()
    if term:
        parts.append(f"-{term}")

dork = " ".join(parts)

st.subheader("Generated dork")
if dork:
    st.code(dork, language="text")
    st.link_button("Open in Google", f"https://www.google.com/search?q={dork.replace(' ', '+')}")
else:
    st.info("Enter at least one field to generate a query.")
