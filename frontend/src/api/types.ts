export interface NoteListItem {
  id: string
  title: string
  updated_at: string
}

export interface Note {
  id: string
  title: string
  body: string
  created_at: string
  updated_at: string
}

export interface AesLog {
  block_index: number
  input_matrix: number[][]
  rounds: RoundTrace[]
}

export interface RoundTrace {
  round: number
  after_add_round_key: number[][]
  after_sub_bytes?: number[][]
  after_shift_rows?: number[][]
  after_mix_columns?: number[][]
  round_key_matrix: number[][]
}

export interface RoundKeys {
  round_keys: number[][][]
  key_expansion_trace: KeyExpansionTrace[]
}

export interface KeyExpansionTrace {
  word_index: number
  is_rotword: boolean
  is_subword: boolean
  is_rcon: boolean
  round_constant?: number
}

export interface CreateNoteRequest {
  title: string
  body: string
}

export interface UpdateNoteRequest {
  title: string
  body: string
}

export interface SetupPinRequest {
  pin: string
}

export interface UnlockRequest {
  pin: string
}

export interface AuthResponse {
  token: string
  expires_in: number
}

export interface ApiError {
  detail: string
}