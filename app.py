import streamlit as st
import os
from utils import (
    parse_docx,
    parse_pdf,
    parse_txt,
    parse_csv,
    search_docs,
    embed_docs,
    text_to_docs,
    get_sources,
)
from openai.error import OpenAIError

def clear_submit():
    st.session_state["submit"] = False

def set_openai_api_key(api_key: str):
    st.session_state["OPENAI_API_KEY"] = api_key

st.markdown('<h1>Semantic Search 🔍<small> by <a href="https://codegpt.co">Code GPT</a></small></h1>', unsafe_allow_html=True)

# Sidebar
index = None
doc = None
with st.sidebar:
    user_secret = st.text_input(
        "OpenAI API Key",
        type="password",
        placeholder="Paste your OpenAI API key here (sk-...)",
        help="You can get your API key from https://platform.openai.com/account/api-keys.",
        value=st.session_state.get("OPENAI_API_KEY", ""),
    )
    if user_secret:
        set_openai_api_key(user_secret)

    uploaded_file = st.file_uploader(
        "Upload a pdf, docx, or txt file",
        type=["pdf", "docx", "txt", "csv"],
        help="Scanned documents are not supported yet!",
        on_change=clear_submit,
    )

    if uploaded_file is not None:
        if uploaded_file.name.endswith(".pdf"):
            doc = parse_pdf(uploaded_file)
        elif uploaded_file.name.endswith(".docx"):
            doc = parse_docx(uploaded_file)
        elif uploaded_file.name.endswith(".csv"):
            doc = parse_csv(uploaded_file)
        elif uploaded_file.name.endswith(".txt"):
            doc = parse_txt(uploaded_file)
        else:
            st.error("File type not supported")
            doc = None
        text = text_to_docs(doc)
        try:
            with st.spinner("Indexing document... This may take a while⏳"):
                index = embed_docs(text)
                st.session_state["api_key_configured"] = True
        except OpenAIError as e:
            st.error(e._message)

tab1, tab2 = st.tabs(["Intro", "Semantic Search"])
with tab1:
    st.markdown("### Semantic Search")
    st.write("Semantic Search was written with the following tools:")
    st.markdown("#### Code GPT")
    st.write("All code was written with the help of Code GPT. Visit [codegpt.co]('https://codegpt.co') to get the extension.")
    st.markdown("#### Streamlit")
    st.write("The design was written with [Streamlit]('https://streamlit.io/').")
    st.markdown("#### LangChain")
    st.write('[Embedding]("https://platform.openai.com/docs/guides/embeddings") is done via the OpenAI API with "text-embedding-ada-002" and LangChain.')
    st.markdown("""---""")
    st.write('Author: [Daniel Ávila](https://www.linkedin.com/in/daniel-avila-arias/)')
    st.write('Repo: [Github](https://github.com/davila7/semantic-search)')
    st.write("This software was developed with Code GPT, for more information visit: https://codegpt.co")

with tab2:
    st.write('To obtain an API Key you must create an OpenAI account at the following link: https://openai.com/api/')
    query = st.text_area("Ask a question about the document", on_change=clear_submit)
    button = st.button("Submit")
    if button or st.session_state.get("submit"):
        if not query:
            st.error("Please enter a question!")
        else:
            st.session_state["submit"] = True
            sources = search_docs(index, query)
            st.markdown("#### Sources")
            for source in sources:
                st.markdown(source.page_content)
                st.markdown(source.metadata["source"])
                st.markdown("---")