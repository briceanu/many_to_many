from sqlalchemy.orm import Session, joinedload, selectinload
from models import Student, Course, student_course_association
from schemas import  StudentSchemaCreate
from sqlalchemy import func,cast, Integer,  Float , desc, select, exists
import uuid
from collections import defaultdict
from datetime import date


def create_student(student_data: StudentSchemaCreate, session: Session):
    student = Student(**student_data.model_dump())  # Convert Pydantic schema to SQLAlchemy model
    session.add(student)
    session.commit()
    session.refresh(student)
    return student  



def list_all_students(session:Session):
    students = session.query(Student).options(joinedload(Student.courses)).all()
    return students

def remove_student(session:Session,student_id:uuid):
    valid_student_id = uuid.UUID(student_id)
    student = session.get(Student,valid_student_id)
    if not student:
        return None
    session.delete(student)    
    session.commit()
    return student

def filter_students(
        exclude_word:str,
        search_word:str,
        session:Session,
        ):
      subquery = session.query(Student.student_id).join(Student.courses).filter(
        Course.subject.ilike(f"%{exclude_word}%")
    ).subquery()



      students = (
        session.query(Student)
        .join(Student.courses)
        .options(joinedload(Student.courses))
        .filter(
            Course.subject.ilike(f"%{search_word}%"),  # Search for students with the wanted subject
            ~Student.student_id.in_(subquery)  # Exclude students who have a course with the excluded subject
        )
        .distinct()
        .all()
    )
      return students
 


def aggregation(session:Session):
        # all the budget of the students 
    # we are using aggregation to find the total_sum of budget and the max value of it.
    all_budget = session.query(
        func.sum(Student.budget).label('total_sum'),
        func.max(Student.budget).label("max_of_budget")
        ).all()

    return [{'sum':data.total_sum,'total':data.max_of_budget}for data in all_budget] 
 
        

def annotation(session:Session):
    # we are returning an annotation as an integer not decimal
        data = (
             session.query(
             (Student.name).label('name'),
             (cast(Student.budget,Float)).label('old_budget'),
             (cast(Student.budget,Integer) - 200).label('new_budget')
            ).all()
            )

        return [{'student_name':result.name,'old_sum':result.old_budget,'new_budget':result.new_budget} for result in data]

 
#  get all the names of the students that are enrolled in the a specific  course


def get_students(course_id:uuid.UUID,session:Session):
    course = (
            session
            .query(Course)
            .options(selectinload(Course.students))
            .filter(Course.course_id==course_id)
            .first()
             
        )
    if not course:
        return None
    return [{'name':student.name} for student in course.students]

#  count how many students are enrolled in each course
#  in each course I have to count student_id
def number_of_students_per_course(session:Session):

    query = (session
            .query(Course.subject,func.coalesce(func.count(Student.student_id),0))
            .outerjoin(Course.students)
            .group_by(Course.course_id)
            .all()
            )
    data = [{'course':course,'students':students}for course,students in query]
    return data
 

# calculate each money gatered pe course
# total number of students * course price
def sum_per_course(session:Session):
    query = (
            session.query(
            (Course.subject).label('name_of_subject'),
            (func.count(Student.student_id) * Course.price).label('total_sum_per_course'),
            (func.coalesce(Student.budget,0)).label('student_money'),
            (func.count(Student.student_id)).label('number_of_students'))
            # we can filter how we want
            # .filter(Course.price > 400)
            # .filter(Course.subject == 'Mathematics')
            # .filter(Course.subject.ilike('%en%'))
            # filter the aggregated results using having() function
            # .having(func.count(Student.student_id) * Course.price < 700)
            .outerjoin(Course.students)
            .group_by(Course.course_id)
            .order_by(desc('total_sum_per_course'))
            .all()
            )

    stmt = [{'subject':data.name_of_subject, 
            'total_sum':float(data.total_sum_per_course),
            'student budget':float(data.student_money),
            'number of students':data.number_of_students} for data in query]
    return stmt
  
# get all the money the sudents have
def get_money(session:Session):
    stmt = (
            session.query(
            func.sum(Student.budget).label('total_amount'))
            .scalar()
            
          )
    print(stmt)
    return {'total_sum':stmt}


#  give us all the courese that the subject is math 
# and from that course give us the student's name


def students_per_course(
          subject:str,
        session:Session,
          ):
    students = (
        session.query(
            Course.course_id, 
            Student.name  # Get individual student names
        )
        .join(student_course_association, Course.course_id == student_course_association.c.course_id)
        .join(Student, student_course_association.c.student_id == Student.student_id)
        .filter(Course.subject.ilike(f"%{subject}%"))
        .all()
    )

    # Manually aggregate students per course
    result = defaultdict(list)
    for course_id, student_name in students:
        result[course_id].append(student_name)

    return dict(result)  # Convert defaultdict to regular dict

 


#  find the oldest student

def find_the_oldest_student(session:Session):
    subquery = select(func.min(Student.date_of_birth)).scalar_subquery()
    print(subquery)
    query =(session.query(Student.name)
            .filter(Student.date_of_birth.in_(subquery))
            .first()
        )
    return {'name':query[0]}





# 4. Find Students Born Before a Specific date


def students_born_before(born_date:date,session:Session):
    subquery = select(Student.student_id).filter(Student.date_of_birth > born_date).subquery()

    query = (session.query(
        Student.name,
        Student.budget
        )
        .filter(Student.student_id.in_(subquery))
        .all()
        )
    print(query)
    data = [{'name':name,'price':price} for name,price in query]
    return data



