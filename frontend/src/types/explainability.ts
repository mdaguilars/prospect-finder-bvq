export type ShapDirection =
  | 'aumenta_afinidad'
  | 'reduce_afinidad'
  | 'sin_impacto'

export type ShapRawValue =
  | string
  | number
  | boolean
  | null

export interface ShapFactor {
  feature: string
  label: string
  value: ShapRawValue
  shap_value: number
  abs_shap_value: number
  direction: ShapDirection
}

export interface ExplainabilityCompany {
  expediente_key: number
  ruc: string | null
  nombre: string | null
  anio: number
}

export interface ExplainabilityScore {
  modelo: number
  ranking_operativo: number | null
  diferencia: number | null
  nota: string
}

export interface ShapMetadata {
  base_value: number
  reconstructed_score: number
  local_error: number
  background_train_size: number
  max_evals: number
  method: string
  reference: string
}

export interface ExplainabilityMetadata {
  model_name: string
  config_id: string
  features_total: number
  top_n: number
  interpretation: string
}

export interface ProspectRankingInfo {
  posicion: number
  percentil: number
}

export interface ProspectExplanationResponse {
  empresa: ExplainabilityCompany
  score: ExplainabilityScore
  shap: ShapMetadata
  principales_factores: ShapFactor[]
  factores_que_aumentan_afinidad: ShapFactor[]
  factores_que_reducen_afinidad: ShapFactor[]
  metadata: ExplainabilityMetadata
  ranking: ProspectRankingInfo
}

export interface GlobalShapItem {
  rank: number
  feature: string
  label: string
  mean_abs_shap: number
}

export interface GlobalShapResponse {
  method: string
  scope: string
  reference: string
  items: GlobalShapItem[]
}