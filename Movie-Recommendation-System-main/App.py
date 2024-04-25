import streamlit as st
from PIL import Image
import json
from Classifier import KNearestNeighbours
from bs4 import BeautifulSoup
import requests, io
import PIL.Image
from urllib.request import urlopen
from urllib.error import URLError

with open('./Data/movie_data.json', 'r+', encoding='utf-8') as f:
    data = json.load(f)
with open('./Data/movie_titles.json', 'r+', encoding='utf-8') as f:
    movie_titles = json.load(f)
hdr = {'User-Agent': 'Mozilla/5.0'}


def movie_poster_fetcher(imdb_link):
 
    hdr = {'User-Agent': 'Mozilla/5.0'}

    url_data = requests.get(imdb_link, headers=hdr).text
    s_data = BeautifulSoup(url_data, 'html.parser')
    try:
        imdb_dp = s_data.find("meta", property="og:image")
        movie_poster_link = imdb_dp.attrs['content']
    except (KeyError, AttributeError):
        # Handle the case where 'content' is not present or imdb_dp is not as expected
         print(f"Not Availabale")
    
    try:
        u = urlopen(movie_poster_link)
        raw_data = u.read()
        image = PIL.Image.open(io.BytesIO(raw_data))
        image = image.resize((158, 301))
        st.image(image, use_column_width=False)
    except URLError as e:
        print(f"An error occurred while opening the URL: {e}")

def get_movie_info(imdb_link):

    try:
        # Your headers dictionary (e.g., 'hdr') should be defined here
        url_data = requests.get(imdb_link, headers=hdr).text
        s_data = BeautifulSoup(url_data, 'html.parser')
        imdb_content = s_data.find("meta", property="og:description")
        movie_descr = imdb_content.attrs['content']
        movie_descr = str(movie_descr).split('.')
        movie_director = movie_descr[0]

        if len(movie_descr) >= 2:
            movie_cast = str(movie_descr[1])  # Convert to string if it's not already

            # Check for the presence of "With" before replacing
            if "With" in movie_cast:
                movie_cast = movie_cast.replace('With', 'Cast: ').strip()
        else:
            movie_cast = "Cast: Not available"

        if len(movie_descr) >= 3:
            movie_story = 'Story: ' + str(movie_descr[2]).strip() + '.'
        else:
            movie_story = 'Story: Not available.'

        rating = s_data.find("span", class_="sc-bde20123-1 iZlgcd").text
        movie_rating = 'Total Rating count: ' + str(rating)

        if all(isinstance(var, str) for var in [movie_director, movie_cast, movie_story, movie_rating]):
            return movie_director, movie_cast, movie_story, movie_rating
        else:
            # Handle the case where some data is missing or not in the expected format
            return "N/A", "N/A", "N/A", "N/A"
    except Exception as e:
        print(f"An error occurred: {e}")
        return "N/A", "N/A", "N/A", "N/A"


def KNN_Movie_Recommender(test_point, k):
    # Create dummy target variable for the KNN Classifier
    target = [0 for item in movie_titles]
    # Instantiate object for the Classifier
    model = KNearestNeighbours(data, target, test_point, k=k)
    # Run the algorithm
    model.fit()
    # Print list of 10 recommendations < Change value of k for a different number >
    table = []
    for i in model.indices:
        # Returns back movie title and imdb link
        table.append([movie_titles[i][0], movie_titles[i][2], data[i][-1]])
    print(table)
    return table


st.set_page_config(
    page_title="Movie Recommender System",
)


def run():
    st.title("Movie Recommender System")
    genres = ['Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family',
              'Fantasy', 'Film-Noir', 'Game-Show', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'News',
              'Reality-TV', 'Romance', 'Sci-Fi', 'Short', 'Sport', 'Thriller', 'War', 'Western']
    movies = [title[0] for title in movie_titles]
    category = ['--Select--', 'Movie based', 'Genre based']
    cat_op = st.selectbox('Select Recommendation Type', category)
    if cat_op == category[0]:
        st.warning('Please select Recommendation Type!!')
    elif cat_op == category[1]:
        select_movie = st.selectbox('Select movie: (Recommendation will be based on this selection)',
                                    ['--Select--'] + movies)
        dec = st.radio("Want to Fetch Movie Poster?", ('Yes', 'No'))
        st.markdown(
            '''<h4 style='text-align: left; color: #d73b5c;'>Please wait. It will take a time.</h4>''',
            unsafe_allow_html=True)
        if dec == 'No':
            if select_movie == '--Select--':
                st.warning('Please select Movie!!')
            else:
                no_of_reco = st.slider('Number of movies you want Recommended:', min_value=5, max_value=20, step=1)
                genres = data[movies.index(select_movie)]
                test_points = genres
                table = KNN_Movie_Recommender(test_points, no_of_reco + 1)
                table.pop(0)
                c = 0
                st.success('Movies Recommended for You!')
                for movie, link, ratings in table:
                    c += 1
                    director, cast, story, total_rat = get_movie_info(link)
                    st.markdown(f"({c})[ {movie}]({link})")
                    st.markdown(director)
                    st.markdown(cast)
                    st.markdown(story)
                    st.markdown(total_rat)
                    st.markdown('IMDB Rating: ' + str(ratings) + '⭐')

                #Allow users to provide feedbacks
                user_feedback = st.slider('How would you rate the Recommendation?', 1, 10, 8)
                
                #save the feedback ratings
                st.write("Thank You for your response!")
                st.write(f"You rated the recommendations as {user_feedback}")
        
        else:
            if select_movie == '--Select--':
                st.warning('Please select Movie!!')
            else:
                no_of_reco = st.slider('Number of movies you want Recommended:', min_value=5, max_value=20, step=1)
                genres = data[movies.index(select_movie)]
                test_points = genres
                table = KNN_Movie_Recommender(test_points, no_of_reco + 1)
                table.pop(0)
                c = 0
                st.success('Movies Recommended for You!')
                for movie, link, ratings in table:
                    c += 1
                    st.markdown(f"({c})[ {movie}]({link})")
                    movie_poster_fetcher(link)
                    director, cast, story, total_rat = get_movie_info(link)
                    st.markdown(director)
                    st.markdown(cast)
                    st.markdown(story)
                    st.markdown(total_rat)
                    st.markdown('IMDB Rating: ' + str(ratings) + '⭐')


                #Allow users to provide feedbacks
                user_feedback = st.slider('How would you rate the Recommendation?', 1, 10, 8)
    
                #save the feedback ratings
                st.write("Thank You for your response!")
                st.write(f"You rated the recommendations as {user_feedback}")
    
    elif cat_op == category[2]:
        sel_gen = st.multiselect('Select Genres:', genres)
        dec = st.radio("Want to Fetch Movie Poster?", ('Yes', 'No'))
        st.markdown(
            '''<h4 style='text-align: left; color: #d73b5c;'>Please wait. It will take a time.</h4>''',
            unsafe_allow_html=True)
        if dec == 'No':
            if sel_gen:
                imdb_score = st.slider('Choose IMDb score:', 1, 10, 8)
                no_of_reco = st.number_input('Number of movies:', min_value=5, max_value=20, step=1)
                test_point = [1 if genre in sel_gen else 0 for genre in genres]
                test_point.append(imdb_score)
                table = KNN_Movie_Recommender(test_point, no_of_reco)
                c = 0
                st.success('Movies Recommended for You!')
                for movie, link, ratings in table:
                    c += 1
                    st.markdown(f"({c})[ {movie}]({link})")
                    director, cast, story, total_rat = get_movie_info(link)
                    st.markdown(director)
                    st.markdown(cast)
                    st.markdown(story)
                    st.markdown(total_rat)
                    st.markdown('IMDB Rating: ' + str(ratings) + '⭐')

                #Allow users to provide feedbacks
                user_feedback = st.slider('How would you rate the Recommendation?', 1, 10, 8)
    
                #save the feedback ratings
                st.write("Thank You for your response!")
                st.write(f"You rated the recommendations as {user_feedback}")
        
        else:
            if sel_gen:
                imdb_score = st.slider('Choose IMDb score:', 1, 10, 8)
                no_of_reco = st.number_input('Number of movies:', min_value=5, max_value=20, step=1)
                test_point = [1 if genre in sel_gen else 0 for genre in genres]
                test_point.append(imdb_score)
                table = KNN_Movie_Recommender(test_point, no_of_reco)
                c = 0
                st.success('Movies Recommended for You!')
                for movie, link, ratings in table:
                    c += 1
                    st.markdown(f"({c})[ {movie}]({link})")
                    movie_poster_fetcher(link)
                    director, cast, story, total_rat = get_movie_info(link)
                    st.markdown(director)
                    st.markdown(cast)
                    st.markdown(story)
                    st.markdown(total_rat)
                    st.markdown('IMDB Rating: ' + str(ratings) + '⭐')

                #Allow users to provide feedbacks
                user_feedback = st.slider('How would you rate the Recommendation?', 1, 10, 8)
    
                #save the feedback ratings
                st.write("Thank You for your response!")
                st.write(f"You rated the recommendations as {user_feedback}")

    
    # #Allow users to provide feedbacks
    # user_feedback = st.selectbox("How would you rate the Recommendation?", [5,4,3,2,1,0])
    
    # #save the feedback ratings
    # st.write("Thank You for your response!")
    # st.write(f"You rated the recommendations as {user_feedback}")


run()