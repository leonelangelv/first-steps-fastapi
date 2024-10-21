from fastapi import FastAPI, Depends, status, Query
from fastapi.responses import JSONResponse
from . import schemas, models
from .database import engine, SessionLocal
from .hashing import Hash
from sqlalchemy.orm import Session

app = FastAPI()

models.Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.post("/blog")
def create(request: schemas.Blog, db: Session = Depends(get_db)):
    new_blog = models.Blog(title=request.title, body=request.body)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)

    for i in range(0, 1000):
        other_blog = models.Blog(title="title " + str(i), body="body " + str(i))
        db.add(other_blog)
        db.commit()
        db.refresh(other_blog)

    return {"data": request, "db": db}


@app.get("/blog")
def get_blogs(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
):
    offset = (page - 1) * size

    blogs = db.query(models.Blog).offset(offset).limit(size).all()

    blogs_data = [blog.to_dict() for blog in blogs]

    total_blogs = db.query(models.Blog).count()
    total_pages = (total_blogs + size - 1) // size

    return JSONResponse(
        {
            "data": blogs_data,
            "total": total_blogs,
            "page": page,
            "size": size,
            "total_pages": total_pages,
        }
    )


@app.get("/blogs")
def get_blogs(db: Session = Depends(get_db)):
    blogs = db.query(models.Blog).all()

    # blogs2 = [blog.to_dict() for blog in blogs]

    # return JSONResponse({"data": blogs})
    return blogs


@app.get("/blog/{id}")
def get_blog(id: int, db: Session = Depends(get_db)):
    try:
        blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    except Exception as e:
        print("Error in get_blog: ", str(e))

    data = {"data": blog.to_dict()}

    return JSONResponse(data, status_code=status.HTTP_201_CREATED)


@app.delete("/blog/{id}")
def delete_blog(id: int, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()

    if not blog:
        return JSONResponse(
            {"data": "blog not found"}, status_code=status.HTTP_404_NOT_FOUND
        )

    db.delete(blog)
    db.commit()

    return JSONResponse({"data": "deleted"})


@app.put("/blog/{id}")
def update_blog(id: int, request: schemas.Blog, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()

    if not blog:
        return JSONResponse(
            {"data": "blog not found"}, status_code=status.HTTP_404_NOT_FOUND
        )

    blog.title = request.title
    blog.body = request.body

    db.commit()

    return {"data": "blog updated"}


@app.post("/user")
def create_user(request: schemas.User, db: Session = Depends(get_db)):
    user_data = request.to_dict()

    user_data["password"] = Hash.bcrypt(request.password)

    new_user = models.User(**user_data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    res = JSONResponse({"data": new_user.to_dict()})
    return res


@app.get("/user/{id}")
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        return JSONResponse(
            {"data": "user not found"}, status_code=status.HTTP_404_NOT_FOUND
        )

    return JSONResponse({"data": user.to_dict()})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
