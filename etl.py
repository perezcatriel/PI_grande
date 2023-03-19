import datetime

import pandas as pd

# Cargo los dataset de las peliculas
amazon_df = pd.read_csv("./datasets/amazon_prime_titles.csv")
disney_df = pd.read_csv("./datasets/disney_plus_titles.csv")
hulu_df = pd.read_csv("./datasets/hulu_titles.csv")
netflix_df = pd.read_csv("./datasets/netflix_titles.csv")

# creo una columna "id" mas el "show_id"
amazon_df["id"] = "a" + amazon_df["show_id"]
disney_df["id"] = "d" + disney_df["show_id"]
hulu_df["id"] = "h" + hulu_df["show_id"]
netflix_df["id"] = "n" + netflix_df["show_id"]

# Concateno todos los dataset en "movies_df"
movies_df = pd.concat([amazon_df, disney_df, hulu_df, netflix_df], axis=0)

# el "rating" que este nulo le escribo "G"
movies_df["rating"].fillna("G", inplace=True)

# le doy formato YYYY-mm-dd a la columna "date_added
movies_df["date_added"] = pd.to_datetime(movies_df["date_added"])

# transformo todo el dataset en minusculas
movies_df = movies_df.apply(
    lambda x: x.str.lower() if x.dtype == "object" else x)

# separo "duration" en "duration_int" y "duration_type"
movies_df[["duration_int", "duration_type"]] = movies_df[
    "duration"].str.extract(r'(\d+)\s*(\D+)', expand=True)
movies_df['duration_int'] = movies_df['duration_int'].astype(
    'Int64')

# elimino la columna "duration"
movies_df.drop("duration", inplace=True, axis=1)

# cargo todos los csv de rating
rating_1 = pd.read_csv("./datasets/1.csv")
rating_2 = pd.read_csv("./datasets/2.csv")
rating_3 = pd.read_csv("./datasets/3.csv")
rating_4 = pd.read_csv("./datasets/4.csv")
rating_5 = pd.read_csv("./datasets/5.csv")
rating_6 = pd.read_csv("./datasets/6.csv")
rating_7 = pd.read_csv("./datasets/7.csv")
rating_8 = pd.read_csv("./datasets/8.csv")

# uno todos en uno
ratings = pd.concat(
    [rating_1, rating_2, rating_3, rating_4, rating_5, rating_6, rating_7,
     rating_8], axis=0)

# elimino los duplicados
ratings.drop_duplicates(inplace=True)

# cambio el nombre "rating" por "scores" para poder trabajarlo con movies_df
# posteriormente
ratings.rename(columns={"rating": "scores"}, inplace=True)

# le doy formato a la columna "timestamp"
ratings["timestamp"] = ratings["timestamp"].apply(
    lambda d: datetime.datetime.fromtimestamp(int(d)).strftime('%Y-%m-%d'))

# guardo el scores.csv
ratings.to_csv("./datasets/scores.csv", index=False)

# calculo el score medio
scores_df = ratings.groupby("movieId")[
    "scores"].mean().to_frame().reset_index()

# redondeo a dos decimales
scores_df["scores"] = round(scores_df["scores"], 2)

# cambio el nombre de "scores" a "prom_scores"
scores_df.rename(columns={"scores": "prom_scores"}, inplace=True)

# uno los dos csv en un solo csv final
movies_df = movies_df.merge(scores_df, left_on="id",
                            right_on="movieId")

# elimino esta columna que despues de la union ya no la necesitamos
movies_df.drop("movieId", inplace=True, axis=1)

# csv final
movies_df.to_csv("./datasets/df_final.csv", index=False)
