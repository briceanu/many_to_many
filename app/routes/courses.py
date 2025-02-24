from fastapi import APIRouter, Body,Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from db.db_connection import get_db
from schemas import (
    CourseSchemaCreate,
    CourseSchemaReturn,
    CourseSchemaReturnWithOutStudents,
    Number_of_students_schema)
from sqlalchemy.exc import IntegrityError
import course_crud
from typing import Annotated
router = APIRouter(prefix='/course',tags=['all the routes for the courses'])
import uuid
from datetime import date



@router.post('/create',description='create a course')
async def create_course(
    course:Annotated[CourseSchemaCreate,Body()],
    session:Session=Depends(get_db)
    )-> CourseSchemaReturn:
    try:
        course = course_crud.create_course(course,session)
        return course
    except IntegrityError as e:
        raise HTTPException(status_code=400,detail=f'an error occured: {str(e.orig)}')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.get('/list_courses',description='list all courses')
async def list_courses(
    session:Session=Depends(get_db)
    ) ->list[CourseSchemaReturn]:
    try:
        courses = course_crud.list_courses(session)
        return courses
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")








@router.post('/enrol_course',description='enrol student in course')
async def enrol_in_course(
    course_id: Annotated[uuid.UUID,Body()],
    student_id: Annotated[uuid.UUID,Body()],
    session:Session=Depends(get_db),
    )-> dict:
    try:
        student = course_crud.enrol_in_course(course_id, student_id, session)
        if isinstance(student,dict) and 'error' in student:
            raise HTTPException(status_code=400,detail=student['error'])    
        return {'status_code':status.HTTP_201_CREATED,
                'success':f'User {student_id} enroled in course {course_id}'}
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Database error: {str(e.orig)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

 
@router.get('/students_enrolled_in_course')
async def students_enrolled(
    course_id:uuid.UUID,
    session:Session=Depends(get_db),
    )-> list[dict]:
    try:
        students = course_crud.show_students_enrolled_in_one_course(course_id,session)
        if students is None:
            raise HTTPException(status_code=400,detail=f'no course with the id {course_id} found.')
        return students
    except ValueError as e:
        raise HTTPException(status_code=400,detail=f'an error occured: {str(e)}')    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")



@router.get('/all_sum_in_course')
async def all_sum(
    course_id:uuid.UUID,
    session:Session=Depends(get_db),
    ) -> dict:
    try:
        course = course_crud.all_money_in_one_course(course_id,session)
        if course is None:
            raise HTTPException(status_code=400,detail=f'no course with the id {course_id} found.')
        return course
    except ValueError as e:
        raise HTTPException(status_code=400,detail=f'an error occured: {str(e)}')    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@router.get('/query_course_by_subject')
async def query_course(
    subject:str,
    session:Session=Depends(get_db),
    ) -> list[CourseSchemaReturnWithOutStudents]:
    try:
        course = course_crud.select_course_by_subject(subject,session)
        if course is None:
            raise HTTPException(status_code=400,detail=f'no course with the subject {subject} found.')
        return course
    except ValueError as e:
        raise HTTPException(status_code=400,detail=f'an error occured: {str(e)}')    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@router.get('/query_course_by_date')
async def query_course(
    date:date,
    session:Session=Depends(get_db),
    ) -> list[CourseSchemaReturnWithOutStudents]:
    try:
        course = course_crud.select_course_by_date(date,session)
        if course is None:
            raise HTTPException(status_code=400,detail=f'no course with the date {date} found.')
        return course
    except ValueError as e:
        raise HTTPException(status_code=400,detail=f'an error occured: {str(e)}')    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get('/get_course_by_number_of_students')
async def query_course(
    number_of_students:Annotated[Number_of_students_schema,Query()],
    session:Session=Depends(get_db),
    ) -> list[dict]:
    try:
        course = course_crud.get_course_by_number_of_students(number_of_students, session)
        return course
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")




@router.get('/subquery')
async def subquery(
    session:Session=Depends(get_db),
    ) :
    try:
        course = course_crud.subquery(session)
        return course
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get('/filter_students')
async def filter_students_by_course(
    course:str,
    session:Session=Depends(get_db),
    ) -> dict:
    try:
        course = course_crud.filter_students_by_course(course,session)
        return course
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")



@router.get('/courses_without_students')
async def courses_without_students(
    session:Session=Depends(get_db),
    ) :
    try:
        course =  course_crud.course_without_students(session)
        return course
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
 