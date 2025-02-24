from fastapi import FastAPI
from routes.courses import router as course_router
from routes.students import router as student_router

app = FastAPI()


app.include_router(course_router)
app.include_router(student_router)