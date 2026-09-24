from pydantic import BaseModel
from typing import Optional


class SetupPinRequest(BaseModel):
    pin: str

    class Config:
        min_length = 6


class UnlockRequest(BaseModel):
    pin: str


class CreateNoteRequest(BaseModel):
    title: str
    body: str


class UpdateNoteRequest(BaseModel):
    title: str
    body: str


class NoteCreateResponse(BaseModel):
    id: str


class AuthResponse(BaseModel):
    token: str
    expires_in: int


class NoteListItem(BaseModel):
    id: str
    title: str
    updated_at: str


class Note(BaseModel):
    id: str
    title: str
    body: str
    created_at: str
    updated_at: str


class AesLog(BaseModel):
    block_index: int
    input_matrix: list[list[int]]
    rounds: list[dict]


class RoundKeys(BaseModel):
    round_keys: list[list[list[int]]]
    key_expansion_trace: list[dict]


class ErrorResponse(BaseModel):
    detail: str