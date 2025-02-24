from sqlalchemy.orm import (
    mapped_column,
    Mapped,
    DeclarativeBase,
    validates,
    relationship
         )
import uuid
from sqlalchemy import Numeric, Float, String , CheckConstraint, Table, Column,ForeignKey, Date,Enum
from datetime import date
import enum
from typing import List
class Base(DeclarativeBase):
    ...


class Subjects(enum.Enum):
    History = 'History'
    Mathematics = 'Mathematics'
    English = 'English'
    Geography = 'Geography'



student_course_association = Table(
    'student_course',
    Base.metadata,
    Column('student_id',ForeignKey('student.student_id'),primary_key=True),
    Column('course_id',ForeignKey('course.course_id'),primary_key=True)
    )





class Course(Base):
    __tablename__ = 'course'
    course_id:Mapped[uuid.UUID]= mapped_column(default=lambda:uuid.uuid4(), primary_key=True,unique=True)
    price:Mapped[Float]= mapped_column(Numeric(4,2),CheckConstraint('price > 0.0'), nullable=False)
    start_date:Mapped[date] = mapped_column(Date(),nullable=False) 
    subject:Mapped[Subjects] = mapped_column(Enum(Subjects, native_enum=False))
    students:Mapped[List['Student']]= relationship(back_populates='courses',secondary=student_course_association)


    class Config:
        from_attributes=True
        extra='forbid'


class Student(Base):
    __tablename__ = 'student'
    student_id:Mapped[uuid.UUID]= mapped_column(default=lambda:uuid.uuid4(), primary_key=True,unique=True)
    name:Mapped[str] = mapped_column(String(50))
    email:Mapped[str]= mapped_column(String(100), nullable=False,unique=True)
    budget:Mapped[Float]= mapped_column(Numeric(4,2),CheckConstraint('budget >= 0.0'),nullable=False)
    date_of_birth:Mapped[date] = mapped_column(Date(),nullable=False)
    courses:Mapped[List['Course']] = relationship(back_populates='students',secondary=student_course_association)





    @validates('date_of_birth')
    def validate_date_of_birth(self,key,value):
        min_date = date(1950,1,1)
        if value  < min_date:
            raise ValueError('date of birth can not be less than 01-01-1950')
        return value
        




