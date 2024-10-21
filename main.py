import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()


@app.get("/")
def index():
    return {"data": {"name": "Sarthak"}}


@app.get("/blog")
def show(limit: int, published: bool):
    if published:
        return {"data": f"all published blogs, {limit}"}

    return {"data": f"Blog list, {limit}"}


@app.get("/blog/unpublished")
def unpublished():
    return {"data": "all unpublished blogs"}


@app.get("/blog/{id}/comments")
def commnets(id: int):
    return {"data": {"1", "2"}}


class Blog(BaseModel):
    title: str
    body: str
    pushlished_at: Optional[bool] = False


@app.post("/blog")
def create_blog(blog: Blog):
    return {"data": "blog created", "request": blog}


if __name__ == "__main__":

    uvicorn.run(app, host="127.0.0.1", port=8000)
