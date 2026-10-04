export interface CatalogItem {
  value: string
  count: number
}

export interface CatalogMetadata {
  total_provincias: number
  total_tipos_compania: number
}

export interface CatalogResponse {
  provincias: CatalogItem[]
  tipos_compania: CatalogItem[]
  metadata: CatalogMetadata
}