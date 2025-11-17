import streamlit as st
import pandas as pd
import plotly.express as px # A more interactive plotting library

# --- Page Configuration ---
# 'wide' layout uses the full screen width, which is better for dashboards
st.set_page_config(layout="wide", page_title="Netflix Analysis Dashboard")

# --- Data Loading ---
# @st.cache_data tells Streamlit to only load this data once,
# which makes your app run much faster.
@st.cache_data
def load_data(filepath):
    try:
        data = pd.read_csv(filepath)
        # Perform data cleaning as planned in your doc
        data['country'] = data['country'].fillna('Unknown')
        data['director'] = data['director'].fillna('Unknown')
        data['cast'] = data['cast'].fillna('Unknown')
        data = data.dropna(subset=['rating', 'date_added'])
        return data
    except FileNotFoundError:
        st.error(f"Error: The file '{filepath}' was not found. Please make sure it's in the root of your GitHub repository.")
        return pd.DataFrame() # Return empty dataframe

# Load the dataset
# This MUST match the name of the file you uploaded to GitHub
df = load_data('netflix_titles.csv')

# --- Main Dashboard Title ---
st.title("🎬 A Data-Driven Analysis of Netflix")
st.markdown("This dashboard provides an interactive analysis of Netflix content, solving the 'decision fatigue' problem identified in the project background.")

# --- Sidebar Filters ---
st.sidebar.header("Dashboard Filters 🔎")

# Filter 1: Type (Movie or TV Show) - as planned
type_options = df['type'].unique()
type_filter = st.sidebar.multiselect(
    "Select Content Type (Movie/TV Show):",
    options=type_options,
    default=type_options # Default to showing all
)

# Filter 2: Rating - as planned
rating_options = sorted(df['rating'].unique())
rating_filter = st.sidebar.multiselect(
    "Select Content Rating:",
    options=rating_options,
    default=rating_options # Default to showing all
)

# Filter 3: Release Year - as planned
min_year = int(df['release_year'].min())
max_year = int(df['release_year'].max())
year_slider = st.sidebar.slider(
    "Select Release Year Range:",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year) # Default to full range
)

# --- Apply Filters to Data ---
# This filtered_df will be used by all charts and tables
filtered_df = df[
    (df['type'].isin(type_filter)) &
    (df['rating'].isin(rating_filter)) &
    (df['release_year'] >= year_slider[0]) &
    (df['release_year'] <= year_slider[1])
]

# Show an error if the filters result in no data
if filtered_df.empty:
    st.warning("No data found for the selected filters. Please adjust your filter settings.")
else:
    # --- Main Page Content ---
    
    # Row 1: Key Metrics
    st.subheader("High-Level Summary")
    total_titles = filtered_df.shape[0]
    total_movies = filtered_df[filtered_df['type'] == 'Movie'].shape[0]
    total_shows = filtered_df[filtered_df['type'] == 'TV Show'].shape[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Titles", f"{total_titles:,}")
    col2.metric("Total Movies", f"{total_movies:,}")
    col3.metric("Total TV Shows", f"{total_shows:,}")

    # Row 2: Charts (as planned in your doc)
    st.subheader("Interactive Visualizations (Time & Genre)")
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        # Chart 1: Content added over time
        st.markdown("**Chart 1: Content Added Per Year**")
        year_data = filtered_df['release_year'].value_counts().reset_index()
        year_data.columns = ['Release Year', 'Count']
        year_data = year_data.sort_values(by='Release Year')
        
        fig1 = px.line(year_data, x='Release Year', y='Count', title="Titles Added by Year")
        st.plotly_chart(fig1, use_container_width=True)

    with col_chart2:
        # Chart 2: Genre Distribution
        st.markdown("**Chart 2: Top 10 Genres**")
        # Split 'listed_in' (genres) and count them
        all_genres = filtered_df['listed_in'].str.split(', ').explode()
        genre_counts = all_genres.value_counts().head(10).reset_index()
        genre_counts.columns = ['Genre', 'Count']
        
        fig2 = px.bar(genre_counts, x='Count', y='Genre', orientation='h', title="Top 10 Genres")
        fig2.update_layout(yaxis={'categoryorder':'total ascending'}) # Show largest at top
        st.plotly_chart(fig2, use_container_width=True)

    # Row 3: More Visualizations (Type, Country, Director)
    st.subheader("Content Breakdown (Type & Director)")
    col_chart3, col_chart4 = st.columns(2)

    with col_chart3:
        # Chart 3: Pie chart for Type (Movie vs TV Show)
        st.markdown("**Chart 3: Content Type Distribution**")
        type_counts = filtered_df['type'].value_counts().reset_index()
        type_counts.columns = ['Type', 'Count']
        
        fig3 = px.pie(type_counts, names='Type', values='Count', title="Movie vs. TV Show Split", hole=0.3)
        st.plotly_chart(fig3, use_container_width=True)

    with col_chart4:
        # Chart 4: Bar chart for Top 10 Directors
        st.markdown("**Chart 4: Top 10 Directors**")
        all_directors = filtered_df[filtered_df['director'] != 'Unknown']['director'].str.split(', ').explode()
        director_counts = all_directors.value_counts().head(10).reset_index()
        director_counts.columns = ['Director', 'Count']
        
        fig4 = px.bar(director_counts, x='Count', y='Director', orientation='h', title="Top 10 Directors by Content Count")
        fig4.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig4, use_container_width=True)

    # --- NEW: Row 4: Rating Visualization ---
    st.subheader("Content Analysis by Rating")
    
    # Chart 5: Bar chart for Top 10 Ratings
    rating_counts = filtered_df['rating'].value_counts().head(10).reset_index()
    rating_counts.columns = ['Rating', 'Count']
    
    fig5 = px.bar(rating_counts, 
                  x='Count', 
                  y='Rating', 
                  orientation='h', 
                  title="Top 10 Content Ratings")
    fig5.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig5, use_container_width=True)


    # Row 5: Raw Data Table (as planned)
    st.subheader("Explore All Filtered Titles")
    st.dataframe(filtered_df)
