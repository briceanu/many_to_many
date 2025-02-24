from fastapi import APIRouter, Depends, Body,Path, status
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
import student_crud
from db.db_connection import get_db
from sqlalchemy.orm import Session
from schemas import  StudentSchemaCreate,StudentSchemaReturn
from typing import Annotated
import uuid
from datetime import date


router = APIRouter(prefix='/student',tags=['all the routes for the student'])




@router.post('/create')   
async def create_student(
    student: Annotated[StudentSchemaCreate,Body()],
    session: Session = Depends(get_db)) -> StudentSchemaReturn:
    try:
        student = student_crud.create_student(student, session)
        return student
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"An error occurred: {str(e.orig)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")



@router.get('/list_students',description='list all students')   
async def list_students(
    session: Session = Depends(get_db)) ->list[StudentSchemaReturn]:
    try:
        students = student_crud.list_all_students(session)
        return students
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.delete('/remove/{student_id}')
async def remove_student(
    session:Session=Depends(get_db),
    student_id=Annotated[uuid.UUID,Path()],
    ) -> dict:
    try:
        student = student_crud.remove_student(session,student_id)
        if student is None:
            raise HTTPException(status_code=400, detail=f"no student with the id {student_id} found.")        
        return {'status':status.HTTP_200_OK,"success":f'user with the id {student_id} removed.'}
        # raise an error in case it occurs
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")    
    



@router.get('/filter')
async def filter_students_by_courses(
    exclude_word:str,
    search_word:str,
    session:Session=Depends(get_db),
    )-> list[StudentSchemaReturn]:
    try:
        students = student_crud.filter_students(exclude_word,search_word, session)
        if not students:
            raise HTTPException(status_code=400, detail='no students match the searching criteria.')
        return students
    except HTTPException: 
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")    
    
@router.get('/aggreagation')
async def aggreation(
    session:Session=Depends(get_db),
    ) ->list[dict]:
    try:
        data = student_crud.aggregation(session)
        return data
    except HTTPException: 
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")    
    
@router.get('/annotation')
async def annotation(
    session:Session=Depends(get_db),
    ) ->list[dict]:
    try:
        data = student_crud.annotation(session)
        return data
    except HTTPException: 
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")    
    

@router.get('/get_students_by_course')
async def get_students_by_course(
    course_id:uuid.UUID,
    session:Session=Depends(get_db),
    ) :
    try:
        course = student_crud.get_students(course_id,session)
        if not course:
            raise HTTPException(status_code=400, detail='no course matchs the searching criteria.')
        return course
    except HTTPException: 
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")    
    


@router.get('/students_per_course')
async def students_per_course(
    session:Session=Depends(get_db),
    ) -> list[dict]:
    try:
        course = student_crud.number_of_students_per_course(session)
        return course
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")    
    


@router.get('/sum_per_course')
async def get_total_sum_per_course(session:Session=Depends(get_db))-> list[dict]:
    try:
        data = student_crud.sum_per_course(session)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")    
    

@router.get('/get_all_money')
def get_all_sum(session:Session=Depends(get_db)):
    try:
        query = student_crud.get_money(session)
        return query
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")    
    
@router.get('/get_students')
def get_students(
    subject:str,
    session:Session=Depends(get_db),
    ):
    try:
        query = student_crud.students_per_course(subject,session)
        return query
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")    
    

@router.get('/oldest_student')
def get_student(
    session:Session=Depends(get_db),
    ):
    try:
        query = student_crud.find_the_oldest_student(session)
        return query
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")    
    
@router.get('/born_before')
def get_students(
    born_date:date,
    session:Session=Depends(get_db),
    ):
    try:
        query = student_crud.students_born_before(born_date,session)
        return query
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")    
    