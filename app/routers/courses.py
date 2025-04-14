from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..database import get_db
from sqlalchemy.orm import Session
from ..models import schemas
from app.models.base.models import *

router = APIRouter(prefix="/courses", tags=["courses"])

@router.post("/", response_model=schemas.Course)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    # First create the course
    db_course = Course(
        name=course.name
    )
    db.add(db_course)
    db.flush()  # Add this line to get the course.id before committing
    
    # Then add all the holes
    for hole in course.holes:
        db_hole = Hole(
            course_id=db_course.id,  # Now db_course.id will have a value
            number=hole.number,
            par=hole.par,
            handicap=hole.handicap
        )
        db.add(db_hole)
    
    try:
        db.commit()
        db.refresh(db_course)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    return db_course

@router.get("/", response_model=List[schemas.Course])
def get_courses(db: Session = Depends(get_db)):
    courses = db.query(Course).all()
    for course in courses:
        course.holes = db.query(Hole).filter(
            Hole.course_id == course.id
        ).all()
    return courses

@router.get("/{course_id}", response_model=schemas.Course)
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    course.holes = db.query(Hole).filter(
        Hole.course_id == course_id
    ).order_by(Hole.number).all()
    
    return course

@router.put("/{course_id}", response_model=schemas.Course)
def update_course(course_id: int, course_update: schemas.CourseUpdate, db: Session = Depends(get_db)):
    # Check if course exists
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")

    try:
        # Update course name
        db.query(Course).filter(Course.id == course_id).update({"name": course_update.name})
        
        # Delete existing holes
        db.query(Hole).filter(Hole.course_id == course_id).delete()
        
        # Add updated holes
        for hole in course_update.holes:
            db_hole = Hole(
                course_id=course_id,
                number=hole.number,
                par=hole.par,
                handicap=hole.handicap
            )
            db.add(db_hole)
        
        db.commit()
        db.refresh(db_course)
        
        # Fetch updated holes
        db_course.holes = db.query(Hole).filter(
            Hole.course_id == course_id
        ).order_by(Hole.number).all()
        
        return db_course
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Delete holes first due to foreign key constraint
    db.query(Hole).filter(Hole.course_id == course_id).delete()
    db.delete(course)
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"message": "Course deleted successfully"}