import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="Netflix Analysis Dashboard")
@st.cache_data
def load_data(filepath):
    try:
        data = pd.read_csv(filepath)
        data['country'] = data['country'].fillna('Unknown')
        data['director'] = data['director'].fillna('Unknown')
        data['cast'] = data['cast'].fillna('Unknown')
        data = data.dropna(subset=['rating', 'date_added'])
        return data
    except FileNotFoundError:
        st.error(f"Error: The file '{filepath}' was not found. Please make sure it's in the root of your GitHub repository.")
        return pd.DataFrame()
df = load_data('netflix_titles.csv')

st.title("A Data-Driven Analysis of Netflix")
st.markdown("This dashboard provides an interactive analysis of Netflix content, solving the 'decision fatigue' problem identified in the project background.")

st.sidebar.header("Dashboard Filters 🔎")

type_options = df['type'].unique()
type_filter = st.sidebar.multiselect(
    "Select Content Type (Movie/TV Show):",
    options=type_options,
    default=type_options 
)

rating_options = sorted(df['rating'].unique())
rating_filter = st.sidebar.multiselect(
    "Select Content Rating:",
    options=rating_options,
    default=rating_options 
)

min_year = int(df['release_year'].min())
max_year = int(df['release_year'].max())
year_slider = st.sidebar.slider(
    "Select Release Year Range:",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year) 
)


filtered_df = df[
    (df['type'].isin(type_filter)) &
    (df['rating'].isin(rating_filter)) &
    (df['release_year'] >= year_slider[0]) &
    (df['release_year'] <= year_slider[1])
]

if filtered_df.empty:
    st.warning("No data found for the selected filters. Please adjust your filter settings.")
else:
    
    st.subheader("High-Level Summary")
    total_titles = filtered_df.shape[0]
    total_movies = filtered_df[filtered_df['type'] == 'Movie'].shape[0]
    total_shows = filtered_df[filtered_df['type'] == 'TV Show'].shape[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Titles", f"{total_titles:,}")
    col2.metric("Total Movies", f"{total_movies:,}")
    col3.metric("Total TV Shows", f"{total_shows:,}")

    st.subheader("Interactive Visualizations")
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown("**Chart 1: Content Added Per Year**")
        year_data = filtered_df['release_year'].value_counts().reset_index()
        year_data.columns = ['Release Year', 'Count']
        year_data = year_data.sort_values(by='Release Year')
        
        fig1 = px.line(year_data, x='Release Year', y='Count', title="Titles Added by Year")
        st.plotly_chart(fig1, use_container_width=True)

    with col_chart2:
        st.markdown("**Chart 2: Top 10 Genres**")
        all_genres = filtered_df['listed_in'].str.split(', ').explode()
        genre_counts = all_genres.value_counts().head(10).reset_index()
        genre_counts.columns = ['Genre', 'Count']
        
        fig2 = px.bar(genre_counts, x='Count', y='Genre', orientation='h', title="Top 10 Genres")
        fig2.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Explore All Filtered Titles")
    st.dataframe(filtered_df)
