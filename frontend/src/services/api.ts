import type {
  ProspectDetailResponse,
  ProspectFilters,
  ProspectListResponse,
} from '../types/prospect'

import type {
  CatalogResponse,
} from '../types/catalog'

import type {
  GlobalShapResponse,
  ProspectExplanationResponse,
} from '../types/explainability'

const API_BASE_URL =
  import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000/api'

function buildProspectQuery(filters: ProspectFilters = {}): string {
  const params = new URLSearchParams()

  if (filters.page !== undefined) {
    params.set('page', String(filters.page))
  }

  if (filters.page_size !== undefined) {
    params.set('page_size', String(filters.page_size))
  }

  if (filters.search?.trim()) {
    params.set('search', filters.search.trim())
  }

  if (filters.provincia?.trim()) {
    params.set('provincia', filters.provincia.trim())
  }

  if (filters.tipo_compania?.trim()) {
    params.set('tipo_compania', filters.tipo_compania.trim())
  }

  if (filters.min_score !== undefined) {
    params.set('min_score', String(filters.min_score))
  }

  if (filters.min_similitud !== undefined) {
    params.set('min_similitud', String(filters.min_similitud))
  }

  if (filters.comparables_disponibles !== undefined) {
    params.set(
      'comparables_disponibles',
      String(filters.comparables_disponibles),
    )
  }

  const query = params.toString()

  return query ? `?${query}` : ''
}

async function request<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      Accept: 'application/json',
      ...options?.headers,
    },
  })

  if (!response.ok) {
    let message = `Error ${response.status}: ${response.statusText}`

    try {
      const payload = (await response.json()) as {
        detail?: string
      }

      if (payload.detail) {
        message = payload.detail
      }
    } catch {
      // Se conserva el mensaje HTTP cuando no existe JSON válido.
    }

    throw new Error(message)
  }

  return response.json() as Promise<T>
}

export async function getProspects(
  filters: ProspectFilters = {},
): Promise<ProspectListResponse> {
  return request<ProspectListResponse>(
    `/prospects${buildProspectQuery(filters)}`,
  )
}

export async function getProspectDetail(
  expedienteKey: number,
): Promise<ProspectDetailResponse> {
  return request<ProspectDetailResponse>(
    `/prospects/${expedienteKey}`,
  )
}

export async function getCatalogs(): Promise<CatalogResponse> {
  return request<CatalogResponse>(
    '/catalogs',
  )
}

export async function getGlobalShap(
  limit = 10,
): Promise<GlobalShapResponse> {
  return request<GlobalShapResponse>(
    `/explainability/global?limit=${limit}`,
  )
}

export async function getProspectExplanation(
  expedienteKey: number,
  topN = 10,
): Promise<ProspectExplanationResponse> {
  return request<ProspectExplanationResponse>(
    `/explainability/prospects/${expedienteKey}?top_n=${topN}`,
  )
}