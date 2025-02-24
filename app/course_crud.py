from models import Course, Student
from schemas import CourseSchemaCreate, Number_of_students_schema
from sqlalchemy.orm import Session, joinedload
import uuid
from datetime import date
from sqlalchemy import func ,select
from models import student_course_association
 
def create_course(
    course:CourseSchemaCreate,
    session:Session):

    course = Course(**course.model_dump())
    session.add(course)
    session.commit()
    session.refresh(course)
    return course



def list_courses(
    session:Session):
    courses = (session
            .query(Course)
            .options(joinedload(Course.students))
            .all()
        )
    return courses

 
# when enroll to course check money and decrease the amount of the course ,,.,,transaction

def enrol_in_course(
        course_id:uuid.UUID,
        student_id:uuid.UUID,
        session:Session):
    student = session.get(Student, student_id)
    if not student:
        return {"error": "Student not found"}

    course = session.get(Course, course_id)
    # if not course:
    if course is None:
        return {"error": "Course not found"}

    if student.budget < course.price:
        return {"error": f"Insufficient funds to enroll in the course. Budget = {student.budget}"}
    try:
        # we are using transactions to decrease the budget of the student 
        # and add the course to the student courses
        student.budget -= course.price  
        student.courses.append(course) 
        session.commit()
        return student   
    except Exception as e:
        session.rollback() 
        return {"error": f"An unexpected error occurred: {str(e.orig)}"}
    finally:
        session.close()


# show all the names of the students enrolled in a course

def show_students_enrolled_in_one_course(
        course_id:uuid.UUID,
        session:Session
        ):
    course = (session
            .query(Course)
            .options(joinedload(Course.students))
            .filter(Course.course_id==course_id)
            .first() 
        )
    if not course:
        return None
    students_name = [{"student name": student.name} for student in course.students]
    return students_name


def all_money_in_one_course(
        course_id:uuid.UUID,
        session:Session
        ):
        # price * count_students
        # total amout of money in one course
    course = (session
            .query(Course)
            .options(joinedload(Course.students))
            .filter(Course.course_id==course_id)
            .first()
        )
    if course is None:
        return None
    number_of_students_enrolled = len(course.students)
    course_amount = {'total_sum':course.price * number_of_students_enrolled}

    return course_amount

#   get all the courses by buject
def select_course_by_subject(subject:str,session:Session):
    courses =  (session
               .query(Course)
               .filter(Course.subject.ilike(f'%{subject}%'))
            #    .filter(Course.subject==f'{subject}')
            #    .filter(Course.subject.ilike(f'{subject}'))
               .order_by(Course.start_date.desc())
               .all()
              )
    if not courses:
        return None
    return courses


def select_course_by_date(date:date,session:Session):
    courses =  (session
               .query(Course)
               .filter(Course.start_date > (f'%{date}%'))
               .order_by(Course.start_date.desc())
               .all()
              )
    if not courses:
        return None
    return courses

# get course by the number of students enrolled in the course
def get_course_by_number_of_students(
        no_of_students:Number_of_students_schema,
        session:Session):
    query = (session
            .query(
            (Course.subject).label('course_subject'),
            func.coalesce(func.count((Student.student_id)),0).label('students_enrolled'))
            .outerjoin(Course.students)
            .having(func.count(Student.student_id) <= no_of_students.number_of_students)
            .group_by(Course.course_id)
            .order_by(func.count((Student.student_id)).desc())
            .all()
             )
 
    data = [{'subject':data.course_subject,
            'students':data.students_enrolled} 
            for data in query]
    return data
    

# subquery
# give us all the students that are enrolled in a course


def subquery(session:Session):
    stmt = (session.query(
            Course.course_id)
            # .outerjoin(Course.students)
            .filter(Course.price < 500)
            .subquery()
            )
    query = (session.query(
        Course.subject,
        Student.name)
        # .outerjoin(Student.courses)
        # .join(Course, Student.student_id == Course.student_id)  # Join students with enrollments
        .filter(Course.course_id.in_(stmt))
        .group_by(Course.course_id)
        # .order_by(Student.name)
        # .distinct()
        .all() 
        )   


            
    print(query)
    return
 


def filter_students_by_course(
        course:str,session:Session):
    query = session.query(Course.course_id).filter(Course.subject.ilike(f'%{course}%')).subquery()
    data = (
        session.query(
            Course.course_id,
            Student.name
        )
        .join(student_course_association, student_course_association.c.student_id == Student.student_id)
        .join(Course, student_course_association.c.course_id == Course.course_id)
        .filter(Course.course_id.in_(query))  # Filter by course_id from subquery
        .all()
    )
 

    students = { 'course_id':data[0][0],
                'students':[student_name for data in data for student_name in data[1:]]}
    return students



# Find Courses with More than 2 Students
# Use a subquery to find courses where the number of enrolled students is greater than 2.

def course_without_students(session:Session):

    # Subquery to get courses where student count > 2
    students =student_course_association.c.student_id
    subquery = (
        session.query(
            student_course_association.c.course_id
        )
        .group_by(student_course_association.c.course_id)
        .having(func.count(student_course_association.c.student_id) >= 2)  # Filter where student count > 2
    )

    # Query to get the actual Course details
    courses = (
        session.query(Course)
        .filter(Course.course_id.in_(subquery))  # Get courses that match the subquery
        .all()
    )

    return [{"subject": course.subject, "course_id": str(course.course_id)} for course in courses]



 
 