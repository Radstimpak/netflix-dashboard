import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go 
import calendar


st.set_page_config(layout="wide", page_title="Netflix Analysis Dashboard")

#Data Loading 
@st.cache_data
def load_data(filepath):
    try:
        data = pd.read_csv(filepath)
        # Data Cleaning
        data['country'] = data['country'].fillna('Unknown')
        data['director'] = data['director'].fillna('Unknown')
        data['cast'] = data['cast'].fillna('Unknown')
        data = data.dropna(subset=['rating', 'date_added', 'duration'])
        
        # Convert date_added to datetime objects for time-based plots
        data['date_added'] = pd.to_datetime(data['date_added'], format='mixed')
        return data
    except FileNotFoundError:
        st.error(f"Error: The file '{filepath}' was not found. Please make sure it's in the root of your GitHub repository.")
        return pd.DataFrame()

df = load_data('netflix_titles.csv')

st.title("A Data-Driven Analysis of Netflix")
st.markdown("This dashboard provides an interactive analysis of Netflix content, solving the 'decision fatigue' problem identified in the project background.")

st.sidebar.header("Dashboard Filters")

# Filter 1
type_options = df['type'].unique()
type_filter = st.sidebar.multiselect(
    "Select Content Type (Movie/TV Show):",
    options=type_options,
    default=type_options
)

# Filter 2
rating_options = sorted(df['rating'].unique())
rating_filter = st.sidebar.multiselect(
    "Select Content Rating:",
    options=rating_options,
    default=rating_options
)

# Filter 3
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
    
    #Main Page
    
    #Key Metrics 
    st.subheader("High-Level Summary")
    total_titles = filtered_df.shape[0]
    total_movies = filtered_df[filtered_df['type'] == 'Movie'].shape[0]
    total_shows = filtered_df[filtered_df['type'] == 'TV Show'].shape[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Titles", f"{total_titles:,}")
    col2.metric("Total Movies", f"{total_movies:,}")
    col3.metric("Total TV Shows", f"{total_shows:,}")

    #Plots

    st.subheader("Genre/Rating & Seasonal Trends")
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        # Plot 1
        st.markdown("**Plot 1: Top 10 Genres by Rating**")
        
        genre_df = filtered_df.dropna(subset=['listed_in', 'rating'])
        genre_df['main_genre'] = genre_df['listed_in'].str.split(', ').str[0]
        
        top_10_genres = genre_df['main_genre'].value_counts().head(10).index.tolist()
        top_genres_df = genre_df[genre_df['main_genre'].isin(top_10_genres)]
        
        genre_rating_counts = top_genres_df.groupby(['main_genre', 'rating']).size().reset_index(name='count')

        if not genre_rating_counts.empty:
            fig1 = px.bar(
                genre_rating_counts,
                x='main_genre',
                y='count',
                color='rating',
                title="Rating Breakdown for Top 10 Genres",
                barmode='stack'
            )
            fig1.update_layout(xaxis_title="Genre", yaxis_title="Total Count",
                               xaxis={'categoryorder':'total descending'})
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No data for Genre/Rating chart.")


    with col_chart2:
        # Plot 2
        st.markdown("**Plot 2: Content Addition Heatmap (by Year & Month)**")
        heatmap_data = filtered_df.copy()
        heatmap_data['month_added'] = heatmap_data['date_added'].dt.month_name()
        heatmap_data['year_added'] = heatmap_data['date_added'].dt.year
        
        heatmap_grouped = heatmap_data.groupby(['year_added', 'month_added']).size().reset_index(name='count')
        
        month_order = list(calendar.month_name)[1:]
        heatmap_grouped['month_added'] = pd.Categorical(heatmap_grouped['month_added'], categories=month_order, ordered=True)
        heatmap_grouped = heatmap_grouped.sort_values(by='month_added')
        
        heatmap_pivot = heatmap_grouped.pivot(index='year_added', columns='month_added', values='count').fillna(0)

        if not heatmap_pivot.empty:
            fig2 = go.Figure(data=go.Heatmap(
                z=heatmap_pivot.values,
                x=heatmap_pivot.columns,
                y=heatmap_pivot.index,
                colorscale='Reds'
            ))
            fig2.update_layout(title="Monthly Content Additions Over Time",
                               xaxis_title="Month",
                               yaxis_title="Year")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No data for Heatmap.")


    st.subheader("Geographic & Rating Analysis")
    col_chart3, col_chart4 = st.columns(2)

    with col_chart3:
        # Plot 3
        st.markdown("**Plot 3: Top 10 Production Countries (Excl. USA)**")
        country_data = filtered_df[filtered_df['country'] != 'Unknown']['country'].str.split(', ').explode()
        
        country_data_no_usa = country_data[country_data != 'United States']
        
        if not country_data_no_usa.empty:
            country_counts = country_data_no_usa.value_counts().head(10).reset_index()
            country_counts.columns = ['Country', 'Count']
            
            fig3 = px.bar(
                country_counts,
                x='Count',
                y='Country',
                orientation='h',
                title="Top 10 Production Countries (Excluding United States)"
            )
            fig3.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No non-USA country data to display.")

    with col_chart4:
        #Plot 4
        st.markdown("**Plot 4: Overall Rating Distribution**")
        
        rating_counts = filtered_df['rating'].value_counts().reset_index()
        rating_counts.columns = ['rating', 'count']

        if not rating_counts.empty:
            fig4 = px.pie(
                rating_counts,
                names='rating',
                values='count',
                title="Overall Rating Distribution",
                hole=0.3
            )
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("No rating data to display.")



    st.subheader("Movie Runtime Analysis")
    
    # Plot 5
    st.markdown("**Plot 5: Movie Runtime Distribution by Genre**")
    
    box_data = filtered_df[
        (filtered_df['type'] == 'Movie') & 
        (filtered_df['duration'].str.contains(' min', na=False))
    ].copy()
    box_data = box_data.dropna(subset=['listed_in'])
    
    if not box_data.empty:
        box_data['duration_int'] = box_data['duration'].str.replace(' min', '').astype(int)
        box_data['main_genre'] = box_data['listed_in'].str.split(', ').str[0]
        
        # Get top 10 genres
        top_10_genres_box = box_data['main_genre'].value_counts().head(10).index.tolist()
        box_data_top_10 = box_data[box_data['main_genre'].isin(top_10_genres_box)]

        fig5 = px.box(
            box_data_top_10,
            x='main_genre',
            y='duration_int',
            title="Movie Runtime Distributions by Top 10 Genres",
        )
        fig5.update_layout(xaxis_title="Genre", yaxis_title="Duration (Minutes)")
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("No valid movie runtime data to display.")


    # Raw Data Table
    st.subheader("Explore All Filtered Titles")
    st.dataframe(filtered_df)
