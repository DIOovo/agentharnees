from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Run, RunLog
from app.schemas import RunLogRead, RunRead
from app.models import Run, RunLog, RunStep
from app.schemas import RunLogRead, RunRead, RunStepRead
router = APIRouter(
    prefix="/runs",
    tags=["runs"],
)

@router.get("", response_model=list[RunRead])
def list_runs(db: Session = Depends(get_db)):
    return db.query(Run).order_by(Run.id.desc()).all()

@router.get("/{run_id}", response_model=RunRead)
def get_run(run_id:int,
            db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run

@router.get("/{run_id}/logs", response_model=list[RunLogRead])
def get_run_log(run_id:int,
                db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return (
        db.query(RunLog)
        .filter(RunLog.run_id == run_id)
        .order_by(RunLog.id.asc())
        .all()
    )

@router.get("/{run_id}/steps", response_model=list[RunStepRead])
def get_run_steps(run_id:int,db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return (
        db.query(RunStep)
        .filter(RunStep.run_id == run_id)
        .order_by(RunStep.id.asc())
        .all()
    )