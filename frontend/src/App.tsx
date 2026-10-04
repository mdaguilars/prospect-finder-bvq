import {
  BarChart3,
  Building2,
  ChevronLeft,
  ChevronRight,
  Database,
  MapPin,
  Search,
  Sparkles,
  Target,
  Users,
  X,
} from 'lucide-react'
import {
  useEffect,
  useMemo,
  useState,
} from 'react'

import './App.css'

import {
  getCatalogs,
  getProspectDetail,
  getProspectExplanation,
  getProspects,
} from './services/api'

import type {
  CatalogResponse,
} from './types/catalog'

import type {
  ProspectExplanationResponse,
} from './types/explainability'

import type {
  ProspectDetailResponse,
  ProspectFilters,
  ProspectListItem,
  ProspectListResponse,
} from './types/prospect'

const INITIAL_FILTERS: ProspectFilters = {
  page: 1,
  page_size: 25,
}

function formatNumber(
  value: number | null | undefined,
  maximumFractionDigits = 0,
): string {
  if (value === null || value === undefined) {
    return '—'
  }

  return new Intl.NumberFormat('es-EC', {
    maximumFractionDigits,
  }).format(value)
}

function formatCurrency(
  value: number | null | undefined,
): string {
  if (value === null || value === undefined) {
    return '—'
  }

  return new Intl.NumberFormat('es-EC', {
    style: 'currency',
    currency: 'USD',
    notation: 'compact',
    maximumFractionDigits: 1,
  }).format(value)
}

function formatPercentage(
  value: number | null | undefined,
  digits = 1,
): string {
  if (value === null || value === undefined) {
    return '—'
  }

  return `${new Intl.NumberFormat('es-EC', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(value)}%`
}

function formatScore(
  value: number | null | undefined,
): string {
  if (value === null || value === undefined) {
    return '—'
  }

  return value.toFixed(3)
}

function App() {
  const [prospects, setProspects] =
    useState<ProspectListResponse | null>(null)

  const [catalogs, setCatalogs] =
    useState<CatalogResponse | null>(null)

  const [filters, setFilters] =
    useState<ProspectFilters>(INITIAL_FILTERS)

  const [searchInput, setSearchInput] =
    useState('')

  const [loading, setLoading] =
    useState(true)

  const [error, setError] =
    useState<string | null>(null)

  const [selectedProspect, setSelectedProspect] =
    useState<ProspectListItem | null>(null)

  const [detail, setDetail] =
    useState<ProspectDetailResponse | null>(null)

  const [explanation, setExplanation] =
    useState<ProspectExplanationResponse | null>(null)

  const [detailLoading, setDetailLoading] =
    useState(false)

  const [explanationLoading, setExplanationLoading] =
    useState(false)

  useEffect(() => {
    async function loadCatalogs() {
      try {
        const response = await getCatalogs()
        setCatalogs(response)
      } catch (requestError) {
        console.error(requestError)
      }
    }

    void loadCatalogs()
  }, [])

  useEffect(() => {
    async function loadProspects() {
      setLoading(true)
      setError(null)

      try {
        const response = await getProspects(filters)
        setProspects(response)
      } catch (requestError) {
        setError(
          requestError instanceof Error
            ? requestError.message
            : 'No fue posible consultar el ranking.',
        )
      } finally {
        setLoading(false)
      }
    }

    void loadProspects()
  }, [filters])

  const totalRecords =
    prospects?.metadata.total_records ?? 0

  const currentPage =
    prospects?.metadata.page ?? 1

  const totalPages =
    prospects?.metadata.total_pages ?? 1

  const topScore = useMemo(() => {
    if (!prospects?.items.length) {
      return null
    }

    return prospects.items[0].score_afinidad
  }, [prospects])

  function applySearch() {
    setFilters((current) => ({
      ...current,
      page: 1,
      search: searchInput.trim() || undefined,
    }))
  }

  function clearFilters() {
    setSearchInput('')
    setFilters(INITIAL_FILTERS)
  }

  async function openProspect(
    prospect: ProspectListItem,
  ) {
    setSelectedProspect(prospect)
    setDetail(null)
    setExplanation(null)
    setDetailLoading(true)

    try {
      const response = await getProspectDetail(
        prospect.expediente_key,
      )

      setDetail(response)
    } catch (requestError) {
      console.error(requestError)
    } finally {
      setDetailLoading(false)
    }
  }

  async function loadExplanation() {
    if (!selectedProspect) {
      return
    }

    setExplanationLoading(true)

    try {
      const response = await getProspectExplanation(
        selectedProspect.expediente_key,
        10,
      )

      setExplanation(response)
    } catch (requestError) {
      console.error(requestError)
    } finally {
      setExplanationLoading(false)
    }
  }

  function closeDetail() {
    setSelectedProspect(null)
    setDetail(null)
    setExplanation(null)
  }

  function goToPage(page: number) {
    if (page < 1 || page > totalPages) {
      return
    }

    setFilters((current) => ({
      ...current,
      page,
    }))
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            PF
          </div>

          <div>
            <strong>Prospect Finder</strong>
            <span>BVQ</span>
          </div>
        </div>

        <nav className="sidebar-nav">
          <button className="nav-item active">
            <Target size={18} />
            Prospectos
          </button>

          <button className="nav-item">
            <BarChart3 size={18} />
            Analítica
          </button>

          <button className="nav-item">
            <Database size={18} />
            Modelo
          </button>
        </nav>

        <div className="sidebar-footer">
          <span>Modelo operativo</span>
          <strong>v10 · C3</strong>
          <small>Información financiera 2023</small>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="eyebrow">
              INTELIGENCIA COMERCIAL
            </p>

            <h1>
              Prioridad de prospectos
            </h1>

            <p className="subtitle">
              Identificación de empresas con mayor
              afinidad para el mercado de valores.
            </p>
          </div>

          <div className="decision-date">
            <span>Fecha de decisión</span>
            <strong>01 mayo 2024</strong>
          </div>
        </header>

        <section className="summary-grid">
          <article className="summary-card">
            <div className="summary-icon">
              <Building2 size={20} />
            </div>

            <div>
              <span>Universo prospectable</span>
              <strong>
                {formatNumber(totalRecords)}
              </strong>
              <small>empresas analizadas</small>
            </div>
          </article>

          <article className="summary-card">
            <div className="summary-icon">
              <Target size={20} />
            </div>

            <div>
              <span>Mayor afinidad visible</span>
              <strong>
                {topScore !== null
                  ? formatScore(topScore)
                  : '—'}
              </strong>
              <small>índice de priorización</small>
            </div>
          </article>

          <article className="summary-card">
            <div className="summary-icon">
              <MapPin size={20} />
            </div>

            <div>
              <span>Provincias</span>
              <strong>
                {catalogs?.metadata.total_provincias ?? '—'}
              </strong>
              <small>cobertura nacional</small>
            </div>
          </article>

          <article className="summary-card">
            <div className="summary-icon">
              <Users size={20} />
            </div>

            <div>
              <span>Tipos de compañía</span>
              <strong>
                {catalogs?.metadata.total_tipos_compania ?? '—'}
              </strong>
              <small>segmentos disponibles</small>
            </div>
          </article>
        </section>

        <section className="workspace-card">
          <div className="workspace-header">
            <div>
              <h2>Ranking operativo</h2>
              <p>
                Ordenado desde la empresa con mayor
                prioridad comercial.
              </p>
            </div>

            <span className="result-count">
              {formatNumber(totalRecords)} resultados
            </span>
          </div>

          <div className="filters">
            <div className="search-box">
              <Search size={18} />

              <input
                value={searchInput}
                onChange={(event) =>
                  setSearchInput(event.target.value)
                }
                onKeyDown={(event) => {
                  if (event.key === 'Enter') {
                    applySearch()
                  }
                }}
                placeholder="Buscar empresa, RUC o expediente"
              />

              <button
                onClick={applySearch}
                className="search-button"
              >
                Buscar
              </button>
            </div>

            <select
              value={filters.provincia ?? ''}
              onChange={(event) =>
                setFilters((current) => ({
                  ...current,
                  page: 1,
                  provincia:
                    event.target.value || undefined,
                }))
              }
            >
              <option value="">
                Todas las provincias
              </option>

              {catalogs?.provincias.map((item) => (
                <option
                  key={item.value}
                  value={item.value}
                >
                  {item.value} ({formatNumber(item.count)})
                </option>
              ))}
            </select>

            <select
              value={filters.tipo_compania ?? ''}
              onChange={(event) =>
                setFilters((current) => ({
                  ...current,
                  page: 1,
                  tipo_compania:
                    event.target.value || undefined,
                }))
              }
            >
              <option value="">
                Todos los tipos
              </option>

              {catalogs?.tipos_compania.map((item) => (
                <option
                  key={item.value}
                  value={item.value}
                >
                  {item.value} ({formatNumber(item.count)})
                </option>
              ))}
            </select>

            <button
              className="clear-button"
              onClick={clearFilters}
            >
              Limpiar
            </button>
          </div>

          {error && (
            <div className="error-box">
              {error}
            </div>
          )}

          <div className="table-wrapper">
            <table className="prospects-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Empresa</th>
                  <th>Provincia</th>
                  <th>Tipo</th>
                  <th>Afinidad</th>
                  <th>Percentil</th>
                  <th>Similitud emisor</th>
                  <th>Calidad</th>
                </tr>
              </thead>

              <tbody>
                {loading ? (
                  <tr>
                    <td
                      colSpan={8}
                      className="table-message"
                    >
                      Consultando ranking...
                    </td>
                  </tr>
                ) : prospects?.items.length ? (
                  prospects.items.map((prospect) => (
                    <tr
                      key={prospect.expediente_key}
                      onClick={() =>
                        void openProspect(prospect)
                      }
                    >
                      <td>
                        <span className="rank">
                          #{formatNumber(prospect.ranking)}
                        </span>
                      </td>

                      <td>
                        <div className="company-cell">
                          <strong>
                            {prospect.nombre ?? 'Sin nombre'}
                          </strong>

                          <span>
                            RUC {prospect.ruc ?? '—'}
                          </span>
                        </div>
                      </td>

                      <td>
                        {prospect.provincia ?? '—'}
                      </td>

                      <td>
                        {prospect.tipo_compania ?? '—'}
                      </td>

                      <td>
                        <div className="score-cell">
                          <strong>
                            {formatScore(
                              prospect.score_afinidad,
                            )}
                          </strong>

                          <div className="score-track">
                            <span
                              style={{
                                width:
                                  `${Math.min(
                                    prospect.score_afinidad * 100,
                                    100,
                                  )}%`,
                              }}
                            />
                          </div>
                        </div>
                      </td>

                      <td>
                        {formatPercentage(
                          prospect.percentil_ranking,
                          1,
                        )}
                      </td>

                      <td>
                        {prospect.similitud_emisores
                          .comparables_disponibles
                          ? formatPercentage(
                              prospect.similitud_emisores
                                .similitud_top1,
                              1,
                            )
                          : 'Sin comparable'}
                      </td>

                      <td>
                        {formatPercentage(
                          prospect.calidad_datos
                            .pct_features_disponibles,
                          0,
                        )}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td
                      colSpan={8}
                      className="table-message"
                    >
                      No existen empresas para los
                      filtros seleccionados.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <div className="pagination">
            <span>
              Página {formatNumber(currentPage)} de{' '}
              {formatNumber(totalPages)}
            </span>

            <div>
              <button
                disabled={currentPage <= 1}
                onClick={() =>
                  goToPage(currentPage - 1)
                }
              >
                <ChevronLeft size={17} />
              </button>

              <button
                disabled={currentPage >= totalPages}
                onClick={() =>
                  goToPage(currentPage + 1)
                }
              >
                <ChevronRight size={17} />
              </button>
            </div>
          </div>
        </section>
      </main>

      {selectedProspect && (
        <div className="detail-overlay">
          <button
            className="overlay-background"
            onClick={closeDetail}
            aria-label="Cerrar detalle"
          />

          <aside className="detail-panel">
            <div className="detail-header">
              <div>
                <span className="detail-label">
                  PROSPECTO #{selectedProspect.ranking}
                </span>

                <h2>
                  {selectedProspect.nombre}
                </h2>

                <p>
                  {selectedProspect.ruc} ·{' '}
                  {selectedProspect.provincia}
                </p>
              </div>

              <button
                className="close-button"
                onClick={closeDetail}
              >
                <X size={20} />
              </button>
            </div>

            {detailLoading ? (
              <div className="detail-loading">
                Consultando información financiera...
              </div>
            ) : detail ? (
              <div className="detail-content">
                <section className="priority-box">
                  <div>
                    <span>Índice de Afinidad Bursátil</span>
                    <strong>
                      {formatScore(
                        detail.priorizacion.score_afinidad,
                      )}
                    </strong>
                  </div>

                  <div>
                    <span>Percentil</span>
                    <strong>
                      {formatPercentage(
                        detail.priorizacion
                          .percentil_ranking,
                        1,
                      )}
                    </strong>
                  </div>

                  <div>
                    <span>Ranking</span>
                    <strong>
                      #{formatNumber(
                        detail.priorizacion.ranking,
                      )}
                    </strong>
                  </div>
                </section>

                <section className="detail-section">
                  <h3>Perfil financiero</h3>

                  <div className="financial-grid">
                    <div>
                      <span>Activos</span>
                      <strong>
                        {formatCurrency(
                          detail.indicadores_financieros
                            .activos,
                        )}
                      </strong>
                    </div>

                    <div>
                      <span>Patrimonio</span>
                      <strong>
                        {formatCurrency(
                          detail.indicadores_financieros
                            .patrimonio,
                        )}
                      </strong>
                    </div>

                    <div>
                      <span>Ventas</span>
                      <strong>
                        {formatCurrency(
                          detail.indicadores_financieros
                            .ingresos_ventas,
                        )}
                      </strong>
                    </div>

                    <div>
                      <span>Empleados</span>
                      <strong>
                        {formatNumber(
                          detail.indicadores_financieros
                            .numero_empleados,
                        )}
                      </strong>
                    </div>
                  </div>
                </section>

                <section className="detail-section">
                  <div className="section-title-row">
                    <div>
                      <h3>Factores de afinidad</h3>
                      <p>
                        Explicación individual mediante SHAP.
                      </p>
                    </div>

                    {!explanation && (
                      <button
                        className="explain-button"
                        disabled={explanationLoading}
                        onClick={() =>
                          void loadExplanation()
                        }
                      >
                        <Sparkles size={17} />

                        {explanationLoading
                          ? 'Analizando...'
                          : 'Analizar factores'}
                      </button>
                    )}
                  </div>

                  {explanation && (
                    <div className="factors-list">
                      {explanation.principales_factores
                        .slice(0, 6)
                        .map((factor) => (
                          <div
                            key={factor.feature}
                            className="factor-row"
                          >
                            <div>
                              <strong>
                                {factor.label}
                              </strong>

                              <span>
                                {factor.direction ===
                                'aumenta_afinidad'
                                  ? 'Aumenta afinidad'
                                  : factor.direction ===
                                      'reduce_afinidad'
                                    ? 'Reduce afinidad'
                                    : 'Sin impacto'}
                              </span>
                            </div>

                            <span
                              className={
                                factor.shap_value >= 0
                                  ? 'factor-value positive'
                                  : 'factor-value negative'
                              }
                            >
                              {factor.shap_value >= 0
                                ? '+'
                                : ''}
                              {factor.shap_value.toFixed(4)}
                            </span>
                          </div>
                        ))}
                    </div>
                  )}
                </section>

                <section className="detail-section">
                  <h3>Emisores comparables</h3>

                  {detail.similitud_emisores
                    .comparables_disponibles ? (
                    <div className="comparables-list">
                      {detail.similitud_emisores
                        .comparables.map((comparable) => (
                          <div
                            className="comparable-row"
                            key={`${comparable.orden}-${comparable.emisor.expediente_key}`}
                          >
                            <div>
                              <strong>
                                {comparable.emisor.nombre}
                              </strong>

                              <span>
                                {comparable.emisor.provincia ??
                                  'Provincia no disponible'}
                              </span>
                            </div>

                            <strong>
                              {formatPercentage(
                                comparable.similitud,
                                1,
                              )}
                            </strong>
                          </div>
                        ))}
                    </div>
                  ) : (
                    <p className="muted-text">
                      No existen comparables históricos
                      suficientes para esta empresa.
                    </p>
                  )}
                </section>

                <p className="method-note">
                  El Índice de Afinidad Bursátil es una
                  herramienta de priorización. No representa
                  una probabilidad calibrada ni sustituye el
                  criterio del equipo comercial.
                </p>
              </div>
            ) : (
              <div className="detail-loading">
                No fue posible cargar el detalle.
              </div>
            )}
          </aside>
        </div>
      )}
    </div>
  )
}

export default App