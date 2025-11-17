import streamlit as st
import pandas as pd
import plotly.express as px
import calendar # Needed for sorting months

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="Netflix Analysis Dashboard")

# --- Data Loading ---
@st.cache_data
def load_data(filepath):
    try:
        data = pd.read_csv(filepath)
        # Data Cleaning
        data['country'] = data['country'].fillna('Unknown')
        data['director'] = data['director'].fillna('Unknown')
        data['cast'] = data['cast'].fillna('Unknown')
        data = data.dropna(subset=['rating', 'date_added'])
        
        # Convert date_added to datetime objects for time-based plots
        data['date_added'] = pd.to_datetime(data['date_added'], format='mixed')
        return data
    except FileNotFoundError:
        st.error(f"Error: The file '{filepath}' was not found. Please make sure it's in the root of your GitHub repository.")
        return pd.DataFrame()

# Load the dataset
df = load_data('netflix_titles.csv')

# --- Main Dashboard Title ---
st.title("🎬 A Data-Driven Analysis of Netflix")
st.markdown("This dashboard provides an interactive analysis of Netflix content, solving the 'decision fatigue' problem identified in the project background.")

# --- Sidebar Filters ---
st.sidebar.header("Dashboard Filters 🔎")

# Filter 1: Type
type_options = df['type'].unique()
type_filter = st.sidebar.multiselect(
    "Select Content Type (Movie/TV Show):",
    options=type_options,
    default=type_options
)

# Filter 2: Rating
rating_options = sorted(df['rating'].unique())
rating_filter = st.sidebar.multiselect(
    "Select Content Rating:",
    options=rating_options,
    default=rating_options
)

# Filter 3: Release Year
min_year = int(df['release_year'].min())
max_year = int(df['release_year'].max())
year_slider = st.sidebar.slider(
    "Select Release Year Range:",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# --- Apply Filters to Data ---
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
    
    # Row 1: Key Metrics (Kept from before)
    st.subheader("High-Level Summary")
    total_titles = filtered_df.shape[0]
    total_movies = filtered_df[filtered_df['type'] == 'Movie'].shape[0]
    total_shows = filtered_df[filtered_df['type'] == 'TV Show'].shape[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Titles", f"{total_titles:,}")
    col2.metric("Total Movies", f"{total_movies:,}")
    col3.metric("Total TV Shows", f"{total_shows:,}")

    # --- NEW PLOTS START HERE ---

    # Row 2: Duration Analysis (Plots 1 & 2)
    st.subheader("Content Duration Analysis")
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        # Plot 1: Histogram of Movie Durations
        st.markdown("**Plot 1: Histogram of Movie Durations**")
        df_movies = filtered_df[filtered_df['type'] == 'Movie'].copy()
        if not df_movies.empty:
            # Clean duration column (e.g., "90 min" -> 90)
            df_movies['duration_int'] = df_movies['duration'].str.replace(' min', '').astype(int)
            fig1 = px.histogram(
                df_movies, 
                x='duration_int', 
                nbins=40, 
                title="Distribution of Movie Durations (in minutes)"
            )
            fig1.update_layout(xaxis_title="Duration (Minutes)", yaxis_title="Number of Movies")
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No movies selected to display duration.")

    with col_chart2:
        # Plot 2: Bar Chart of TV Show Season Counts
        st.markdown("**Plot 2: TV Show Season Counts**")
        df_shows = filtered_df[filtered_df['type'] == 'TV Show'].copy()
        if not df_shows.empty:
            season_counts = df_shows['duration'].value_counts().reset_index()
            season_counts.columns = ['Seasons', 'Count']
            fig2 = px.bar(
                season_counts, 
                x='Seasons', 
                y='Count', 
                title="Distribution of TV Show Seasons"
            )
            fig2.update_layout(xaxis={'categoryorder':'total descending'})
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No TV shows selected to display season counts.")

    # Row 3: Actor Popularity & Content Seasonality (Plots 3 & 4)
    st.subheader("Actor Popularity & Monthly Trends")
    col_chart3, col_chart4 = st.columns(2)

    with col_chart3:
        # Plot 3: Bar Chart of Top 10 Actors
        st.markdown("**Plot 3: Top 10 Actors**")
        # Split 'cast', explode, and count, excluding 'Unknown'
        all_actors = filtered_df[filtered_df['cast'] != 'Unknown']['cast'].str.split(', ').explode()
        actor_counts = all_actors.value_counts().head(10).reset_index()
        actor_counts.columns = ['Actor', 'Count']
        
        fig3 = px.bar(
            actor_counts, 
            x='Count', 
            y='Actor', 
            orientation='h', 
            title="Top 10 Actors by Content Count"
        )
        fig3.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig3, use_container_width=True)

    with col_chart4:
        # Plot 4: Bar Chart of Content Added by Month
        st.markdown("**Plot 4: Content Added by Month**")
        df_monthly = filtered_df.copy()
        # Extract month name
        df_monthly['month_added'] = df_monthly['date_added'].dt.month_name()
        # Get counts
        month_counts = df_monthly['month_added'].value_counts().reset_index()
        month_counts.columns = ['Month', 'Count']
        
        # Sort by calendar month (Jan, Feb, Mar...)
        month_order = list(calendar.month_name)[1:]
        month_counts = month_counts.set_index('Month').reindex(month_order).reset_index()

        fig4 = px.bar(
            month_counts, 
            x='Month', 
            y='Count', 
            title="Content Additions by Month"
        )
        st.plotly_chart(fig4, use_container_width=True)

    # Row 4: Treemap Breakdown (Plot 5)
    st.subheader("Content Library Breakdown")
    
    # Plot 5: Treemap of Genres and Ratings
    st.markdown("**Plot 5: Treemap of Content by Genre and Rating**")
    
    # Use only the *first* listed genre for simplicity in the treemap
    treemap_data = filtered_df.copy()
    treemap_data['main_genre'] = treemap_data['listed_in'].str.split(', ').str[0]
    
    # Group by main_genre and rating
    treemap_grouped = treemap_data.groupby(['main_genre', 'rating']).size().reset_index(name='count')

    if not treemap_grouped.empty:
        fig5 = px.treemap(
            treemap_grouped, 
            path=[px.Constant("All Content"), 'main_genre', 'rating'], 
            values='count',
            title='Interactive Breakdown by Genre and Rating'
        )
        fig5.update_layout(margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("No data for treemap.")


    # Row 5: Raw Data Table (Kept from before)
    st.subheader("Explore All Filtered Titles")
    st.dataframe(filtered_df)
