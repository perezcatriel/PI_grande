from typing import Optional

import pandas as pd
from fastapi import FastAPI

# instancio FastAPI
app = FastAPI()
app.title = 'MLops'
app.version = '0.0.1'

# leo el csv con ETL
movies_df = pd.read_csv("./datasets/df_final.csv")

# lista de "plataformas"
platforms = ["netflix", "amazon", "hulu", "disney"]

# lista de "duration_type"
duration_types = ["min", "season", "seasons"]


# pelicula mas larga
@app.get("/movies/get_max_duration", tags=['movies'])
def get_max_duration(year: Optional[int] = None, platform: Optional[str] = None,
                     duration_type: Optional[str] = "min"):
    def get_platform_mask(duration_type):
        switcher = {
            "min": movies_df[movies_df["duration_type"] == "min"],
            "season": movies_df[movies_df["duration_type"] == "season"],
            "season": movies_df[
                movies_df["duration_type"].isin(["season", "seasons"])],
        }
        return switcher.get(duration_type.lower(),
                            {"error": "Inserte un valor correcto"})

    platform_mask = get_platform_mask(duration_type)

    if "error" in platform_mask:
        return platform_mask

    if year is not None:
        platform_mask = platform_mask[platform_mask["release_year"] == year]

    if platform is not None:
        if platform.lower() in platforms:
            platform_id = platform.lower()[0]
            platform_mask = platform_mask[
                platform_mask["id"].str.startswith(platform_id)]
        else:
            return {"error": "Inserte un valor correcto"}

    title = platform_mask.sort_values('duration_int', ascending=False).iloc[0][
        'title']
    return {"max_duration_title": title}


# devuelve el numero de peliculas en una plataforma con score superior a XX
# en un año determinado
@app.get("/movies/get_score_count)", tags=['movies'])
def get_score_count(platform: str, scored: float, year: int):
    if platform.lower() in platforms:
        platform_id = platform.lower()[0]
        platform_mask = movies_df[
            movies_df["id"].str.startswith(platform_id)]
        platform_mask = platform_mask[platform_mask["prom_scores"] > scored]
        platform_mask = platform_mask[platform_mask["release_year"] == year]
        if len(platform_mask) == 0:
            return {
                "error": "Vacio"}
        else:
            platform_count = len(platform_mask)
            return {"platform": platform, "count": platform_count}
    else:
        return {
            "error": "Inserte un valor correcto"}


# Cantidad de peliculas por plataforma
@app.get("/movies/get_count_platform", tags=['movies'])
def get_count_platform(platform: str):
    if platform.lower() in platforms:
        platform_id = platform.lower()[0]
        platform_mask = movies_df['id'].str.startswith(platform_id)
        platform_count = int(platform_mask.sum())
        return {"platform": platform, "count": platform_count}
    else:
        return {
            "error": "Inserte un valor correcto"}


# retorna el actor que mas apariciones tuvo
@app.get("/movies/get_actor)", tags=['movies'])
def get_actor(platform: str, year: int):
    platform_id = platform.lower()[0]
    platform_mask = movies_df[
        movies_df["id"].str.startswith(platform_id)]
    platform_mask = platform_mask[platform_mask["release_year"] == year]
    platform_actors = platform_mask.assign(
        actor=platform_mask.cast.str.split(',')).explode('cast')
    actor_counts = platform_actors.cast.value_counts()
    max_count = actor_counts.max()
    top_actors = actor_counts[actor_counts == max_count].index.tolist()

    return {"platform": platform, "top_actors": top_actors}
