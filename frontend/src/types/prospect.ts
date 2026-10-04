export interface DataQuality {
  n_features_disponibles: number | null
  pct_features_disponibles: number | null
}

export interface IssuerSimilaritySummary {
  comparables_disponibles: boolean | null
  similitud_top1: number | null
  similitud_top5_promedio: number | null
  estado: string | null
}

export interface ProspectListItem {
  expediente_key: number
  ruc: string | null
  nombre: string | null
  anio: number
  fecha_decision: string
  tipo_compania: string | null
  provincia: string | null
  ranking: number
  score_afinidad: number
  percentil_ranking: number
  calidad_datos: DataQuality
  similitud_emisores: IssuerSimilaritySummary
}

export interface ProspectListMetadata {
  page: number
  page_size: number
  total_records: number
  total_pages: number
  sort: string
  score_note: string
  similarity_note: string
}

export interface ProspectListResponse {
  metadata: ProspectListMetadata
  items: ProspectListItem[]
}

export interface CompanyIdentity {
  expediente_key: number
  ruc: string | null
  nombre: string | null
  anio: number
  fecha_decision: string
  tipo_compania: string | null
  provincia: string | null
}

export interface Prioritization {
  ranking: number
  score_afinidad: number
  percentil_ranking: number
  nota: string
}

export interface FinancialIndicators {
  activos: number | null
  patrimonio: number | null
  ingresos_ventas: number | null
  numero_empleados: number | null
  ratio_patrimonio_activos: number | null
  roa: number | null
  margen_neto: number | null
  rotacion_activos: number | null
  roe: number | null
  crecimiento_activos: number | null
  crecimiento_patrimonio: number | null
  crecimiento_ventas: number | null
  crecimiento_empleados: number | null
}

export interface ComparableIssuer {
  expediente_key: number
  ruc: string | null
  nombre: string | null
  anio_perfil: number | null
  fecha_decision_perfil: string | null
  fecha_primera_inscripcion: string | null
  tipo_compania: string | null
  provincia: string | null
}

export interface IssuerComparable {
  orden: number
  similitud: number
  distancia_percentiles: number
  mismo_tipo_compania: boolean | null
  emisor: ComparableIssuer
}

export interface IssuerSimilarityDetail {
  comparables_disponibles: boolean
  similitud_top1: number | null
  similitud_top5_promedio: number | null
  distancia_top1: number | null
  n_emisores_comparados: number | null
  estado: string | null
  metodologia: string | null
  nota: string
  comparables: IssuerComparable[]
}

export interface ModelInfo {
  nombre: string | null
  configuracion: string | null
}

export interface ProspectDetailResponse {
  empresa: CompanyIdentity
  priorizacion: Prioritization
  calidad_datos: DataQuality
  indicadores_financieros: FinancialIndicators
  similitud_emisores: IssuerSimilarityDetail
  modelo: ModelInfo
}

export interface ProspectFilters {
  page?: number
  page_size?: number
  search?: string
  provincia?: string
  tipo_compania?: string
  min_score?: number
  min_similitud?: number
  comparables_disponibles?: boolean
}