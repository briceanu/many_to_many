from pydantic import BaseModel, EmailStr, PositiveFloat, Field, PositiveInt
from datetime import date
import uuid
from enum import Enum
from typing import List


class SubjectsEnum(str, Enum):
    History = 'History'
    Mathematics = 'Mathematics'
    English = 'English'
    Geography = 'Geography'

"""student's schema"""
# //////////////////////////////////////////////////////////////////////////////

class StudentSchemaCreate(BaseModel):
    name:str=Field(max_length=50)
    email: EmailStr
    budget: PositiveFloat
    date_of_birth: date

class StudentSchemaReturn(StudentSchemaCreate):
    student_id: uuid.UUID
    courses: List["CourseSchemaReturnWithOutStudents"]

class StudentSchemaReturnForCourse(StudentSchemaCreate):
    student_id:uuid.UUID

# for list_students  return we don't need courses


"""course's schema"""
# ///////////////////////////////////////////////////////////////////////////////////////

class CourseSchemaCreate(BaseModel):
    price: PositiveFloat
    start_date: date
    subject: SubjectsEnum   

    class Config:
        from_attributes = True
        extra = 'forbid'


class CourseSchemaReturnWithOutStudents(CourseSchemaCreate):
    course_id: uuid.UUID  
 
 

class CourseSchemaReturn(CourseSchemaReturnWithOutStudents):
    students:List["StudentSchemaReturnForCourse"]

 


 
class Number_of_students_schema(BaseModel):
    number_of_students:PositiveInt



 