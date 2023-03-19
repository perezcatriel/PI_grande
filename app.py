import gradio as gr
import numpy as np
import pandas as pd
from surprise import Dataset
from surprise import Reader
from surprise import SVD
from surprise.model_selection import train_test_split

scores_df = pd.read_csv("./datasets/scores.csv")
scores_df["scores"] = np.float16(scores_df["scores"])

platform_movies = pd.read_csv("./datasets/df_final.csv")

reader = Reader(rating_scale=(1, 5))

data = Dataset.load_from_df(scores_df[['userId', 'movieId', 'scores']], reader)

# divide el conjunto en train y test
train_set, test_set = train_test_split(data, test_size=.25, random_state=42)

# Algoritmo de recomendacion
model = SVD()

# Entrena el modelo de "train_set"
model.fit(train_set)

# Predice el modelo usando "test_set"
predictions = model.test(test_set)


def evaluate_recommendation_movie(userId, movieId):
    movie_title = platform_movies[platform_movies.id == movieId].title.iloc[
        0].title()
    prediction = model.predict(userId, str(movieId))
    if prediction.est > 3.6:
        return "todo OK", prediction.est, movie_title
    else:
        return "No, no te va a gustar", \
            prediction.est, \
            movie_title


title = str("Movie Recommendation System")

with gr.Blocks(title=title) as demo:
    userId = gr.inputs.Number(label="Inserta tu userID")
    movieId = gr.Textbox(label="Inserta el movieID de la peli")
    evaluate_recommendation_movie_btn = gr.Button(
        "Peli recomendada...")
    movie_title = gr.Textbox(label="Película:")
    output = gr.Textbox(label="Esta Peli es para mí?")
    score = gr.Textbox(label="Score:")
    evaluate_recommendation_movie_btn.click(fn=evaluate_recommendation_movie,
                                            inputs=[userId, movieId],
                                            outputs=[output, score,
                                                     movie_title])

demo.launch()
