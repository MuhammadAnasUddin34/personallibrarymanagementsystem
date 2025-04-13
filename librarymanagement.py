import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from streamlit_lottie import st_lottie
import plotly.express as px 
import requests

# --- Setup ---
st.set_page_config(page_title="📚 Library Manager", layout="wide")

st.markdown("""
    <style>
    .main-title { font-size: 2.5rem; color: #1E40AF; text-align: center; font-weight: bold; }
    .section-header { font-size: 1.5rem; color: #3B82F6; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# --- Load Lottie ---
def load_lottie_url(url):
    r = requests.get(url)
    return r.json() if r.status_code == 200 else None

# --- Data Handling ---
LIBRARY_FILE = "library.json"

def load_library():
    if os.path.exists(LIBRARY_FILE):
        with open(LIBRARY_FILE, "r") as f:
            return json.load(f)
    return []

def save_library(data):
    with open(LIBRARY_FILE, "w") as f:
        json.dump(data, f, indent=2)

library = load_library()

# --- Sidebar ---
st.sidebar.title("📚 Navigation")
#st.sidebar.lottie(load_lottie_url("https://assets9.lottiefiles.com/temp/lf20_aKAfIn.json"), height=200, key="book")
lottie_book = load_lottie_url("https://assets9.lottiefiles.com/temp/lf20_aKAfIn.json")
if lottie_book:
    with st.sidebar:
        st_lottie(lottie_book, height=200, key="book_animation")

page = st.sidebar.radio("Go to:", ["Add Book", "Library", "Search", "Statistics"])

# --- Add Book ---
if page == "Add Book":
    st.markdown("<h1 class='main-title'>📘 Add a New Book</h1>", unsafe_allow_html=True)
    with st.form("book_form"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Title")
            author = st.text_input("Author")
            year = st.number_input("Year", min_value=1000, max_value=datetime.now().year, step=1)
        with col2:
            genre = st.selectbox("Genre", ["Fiction", "Non-Fiction", "Sci-Fi", "Fantasy", "Romance", "Thriller", "Other"])
            read = st.radio("Read?", ["Yes", "No"])
        submitted = st.form_submit_button("Add Book")

        if submitted and title and author:
            new_book = {
                "title": title,
                "author": author,
                "year": int(year),
                "genre": genre,
                "read": read == "Yes",
                "added": datetime.now().isoformat()
            }
            library.append(new_book)
            save_library(library)
            st.success("Book added successfully!")
            st.balloons()

# --- Library View ---
elif page == "Library":
    st.markdown("<h1 class='main-title'>📚 Your Library</h1>", unsafe_allow_html=True)
    if library:
        df = pd.DataFrame(library)
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Your library is empty. Add some books!")

# --- Search ---
elif page == "Search":
    st.markdown("<h1 class='main-title'>🔍 Search Books</h1>", unsafe_allow_html=True)
    option = st.selectbox("Search by", ["Title", "Author", "Genre"])
    keyword = st.text_input("Enter keyword")

    if keyword:
        results = [book for book in library if keyword.lower() in book[option.lower()].lower()]
        if results:
            st.success(f"Found {len(results)} matching book(s)")
            st.dataframe(pd.DataFrame(results), use_container_width=True)
        else:
            st.warning("No matches found.")

# --- Statistics ---
elif page == "Statistics":
    st.markdown("<h1 class='main-title'>📊 Library Statistics</h1>", unsafe_allow_html=True)
    if not library:
        st.warning("No data to show stats. Add some books first!")
    else:
        df = pd.DataFrame(library)
        total = len(df)
        read_count = df[df['read'] == True].shape[0]
        st.metric("Total Books", total)
        st.metric("Books Read", read_count)
        st.metric("% Read", f"{read_count / total * 100:.1f}%")

        genre_count = df["genre"].value_counts()
        st.markdown("<h3 class='section-header'>Books by Genre</h3>", unsafe_allow_html=True)
        st.plotly_chart(px.bar(genre_count, x=genre_count.index, y=genre_count.values, labels={"x": "Genre", "y": "Count"}))

        year_count = df["year"].value_counts().sort_index()
        st.markdown("<h3 class='section-header'>Books by Year</h3>", unsafe_allow_html=True)
        st.plotly_chart(px.line(x=year_count.index, y=year_count.values, labels={"x": "Year", "y": "Count"}))

# --- Footer ---
st.markdown("---")
st.caption(" Personal Library Manager")
