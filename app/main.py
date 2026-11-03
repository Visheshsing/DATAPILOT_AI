
from pathlib import Path
from io import BytesIO
import uuid

import pandas as pd

from fastapi import FastAPI, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import Base, engine, SessionLocal
from app.database.models import Dataset
from app.services.profiler import profile_dataset


UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 20 * 1024 * 1024

ALLOWED_EXTENSIONS = {".csv", ".xlsx"}

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DataPilot AI",
    description="Autonomous AI Data Scientist",
    version="0.1.0"
)


def load_dataframe(content, extension):

    buffer = BytesIO(content)

    try:
        if extension == ".csv":
            return pd.read_csv(buffer)

        if extension == ".xlsx":
            return pd.read_excel(buffer, engine="openpyxl")

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to read dataset: {error}"
        )

    raise HTTPException(
        status_code=400,
        detail="Unsupported file format"
    )


@app.get("/")
def home():

    return {
        "message": "Welcome to DataPilot AI",
        "status": "running",
        "version": "0.1.0"
    }


@app.get("/health")
def health():

    return {"status": "healthy"}


@app.post("/datasets/upload")
async def upload_dataset(
    file: UploadFile = File(...)
):

    filename = Path(file.filename or "").name
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only CSV and XLSX files are supported"
        )

    content = await file.read(MAX_FILE_SIZE + 1)

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Maximum file size is 20 MB"
        )

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )

    df = load_dataframe(content, extension)

    if df.empty or len(df.columns) == 0:
        raise HTTPException(
            status_code=400,
            detail="Dataset has no usable rows or columns"
        )

    if not df.columns.is_unique:
        raise HTTPException(
            status_code=400,
            detail="Duplicate column names are not supported"
        )

    schema, profile = profile_dataset(df)

    dataset_id = str(uuid.uuid4())

    stored_filename = f"{dataset_id}{extension}"
    file_path = UPLOAD_DIR / stored_filename

    file_path.write_bytes(content)

    db: Session = SessionLocal()

    try:

        dataset = Dataset(
            id=dataset_id,
            filename=filename,
            storage_path=str(file_path),
            row_count=len(df),
            column_count=len(df.columns),
            schema_info=schema,
            profile=profile
        )

        db.add(dataset)
        db.commit()
        db.refresh(dataset)

    except Exception:

        db.rollback()
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=500,
            detail="Could not save dataset metadata"
        )

    finally:
        db.close()

    return {
        "message": "Dataset uploaded successfully",
        "dataset_id": dataset_id,
        "filename": filename,
        "shape": {
            "rows": len(df),
            "columns": len(df.columns)
        },
        "schema": schema,
        "profile": profile
    }


@app.get("/datasets/{dataset_id}")
def get_dataset(dataset_id: str):

    db: Session = SessionLocal()

    try:

        dataset = db.get(Dataset, dataset_id)

        if dataset is None:
            raise HTTPException(
                status_code=404,
                detail="Dataset not found"
            )

        return {
            "id": dataset.id,
            "filename": dataset.filename,
            "row_count": dataset.row_count,
            "column_count": dataset.column_count,
            "schema": dataset.schema_info,
            "profile": dataset.profile
        }

    finally:
        db.close()
