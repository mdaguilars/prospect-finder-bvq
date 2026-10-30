import {
  BarChart3,
  Building2,
  CheckCircle2,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  ChevronUp,
  CircleAlert,
  Info,
  Layers3,
  MapPin,
  Search,
  Sparkles,
  Target,
  TrendingUp,
  Users,
  X,
} from 'lucide-react'

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

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
  IssuerReferenceFinancialProfile,
  ProspectDetailResponse,
  ProspectFilters,
  ProspectListItem,
  ProspectListResponse,
} from './types/prospect'


type ViewName =
  | 'prospects'
  | 'analytics'
  | 'guide'


type CommercialState = {
  label: string
  className: string
  description: string
}


type ComparisonMetric = {
  key: string
  label: string
  prospectValue: number | null
  comparableValue: number | null
  type:
    | 'currency'
    | 'number'
    | 'percentage'
    | 'decimal'
  difference: number | null
  closeness: string
  closenessClass: string
}


const INITIAL_FILTERS: ProspectFilters = {
  page: 1,
  page_size: 25,
}


/* ============================================================
   FORMATO
   ============================================================ */

function formatNumber(
  value: number | null | undefined,
  maximumFractionDigits = 0,
): string {
  if (
    value === null
    || value === undefined
  ) {
    return '—'
  }

  return new Intl.NumberFormat(
    'es-EC',
    {
      maximumFractionDigits,
    },
  ).format(value)
}


function formatCurrency(
  value: number | null | undefined,
): string {
  if (
    value === null
    || value === undefined
  ) {
    return '—'
  }

  return new Intl.NumberFormat(
    'es-EC',
    {
      style: 'currency',
      currency: 'USD',
      notation: 'compact',
      maximumFractionDigits: 1,
    },
  ).format(value)
}


function formatPercentage(
  value: number | null | undefined,
  digits = 1,
): string {
  if (
    value === null
    || value === undefined
  ) {
    return '—'
  }

  return `${
    new Intl.NumberFormat(
      'es-EC',
      {
        minimumFractionDigits: digits,
        maximumFractionDigits: digits,
      },
    ).format(value)
  }%`
}


function formatDecimalPercentage(
  value: number | null | undefined,
  digits = 1,
): string {
  if (
    value === null
    || value === undefined
  ) {
    return '—'
  }

  return formatPercentage(
    value * 100,
    digits,
  )
}


function formatDecimal(
  value: number | null | undefined,
  digits = 2,
): string {
  if (
    value === null
    || value === undefined
  ) {
    return '—'
  }

  return new Intl.NumberFormat(
    'es-EC',
    {
      minimumFractionDigits: digits,
      maximumFractionDigits: digits,
    },
  ).format(value)
}


function formatScore(
  value: number | null | undefined,
): string {
  if (
    value === null
    || value === undefined
  ) {
    return '—'
  }

  return value.toFixed(3)
}


function scoreWidth(
  value: number | null | undefined,
): string {
  const safeValue =
    value ?? 0

  return `${
    Math.max(
      0,
      Math.min(
        safeValue * 100,
        100,
      ),
    )
  }%`
}


function percentageWidth(
  value: number | null | undefined,
): string {
  const safeValue =
    value ?? 0

  return `${
    Math.max(
      0,
      Math.min(
        safeValue,
        100,
      ),
    )
  }%`
}


function shortLabel(
  value: string,
  length = 20,
): string {
  if (
    value.length <= length
  ) {
    return value
  }

  return `${
    value.slice(
      0,
      length - 1,
    )
  }…`
}


function normalizeText(
  value: string,
): string {
  return value
    .normalize('NFD')
    .replace(
      /[\u0300-\u036f]/g,
      '',
    )
    .toLowerCase()
}


/* ============================================================
   PRIORIDAD
   ============================================================ */

function getRankingBand(
  percentile: number | null | undefined,
) {
  if (
    percentile === null
    || percentile === undefined
  ) {
    return {
      label: 'Sin referencia',
      className: 'band-neutral',
    }
  }

  if (
    percentile >= 99
  ) {
    return {
      label: 'Top 1%',
      className: 'band-top',
    }
  }

  if (
    percentile >= 95
  ) {
    return {
      label: 'Top 5%',
      className: 'band-high',
    }
  }

  if (
    percentile >= 90
  ) {
    return {
      label: 'Top 10%',
      className: 'band-medium',
    }
  }

  return {
    label: 'Universo general',
    className: 'band-neutral',
  }
}


function getPriorityState(
  percentile: number | null | undefined,
): CommercialState {
  if (
    percentile === null
    || percentile === undefined
  ) {
    return {
      label: 'Por revisar',
      className: 'state-neutral',
      description:
        'No existe una referencia suficiente para clasificar su nivel de prioridad.',
    }
  }

  if (
    percentile >= 99
  ) {
    return {
      label: 'Muy alta',
      className: 'state-very-high',
      description:
        'Se encuentra dentro del grupo de empresas que conviene revisar primero.',
    }
  }

  if (
    percentile >= 95
  ) {
    return {
      label: 'Alta',
      className: 'state-high',
      description:
        'Se encuentra dentro de un grupo de alta prioridad de revisión.',
    }
  }

  if (
    percentile >= 90
  ) {
    return {
      label: 'Media alta',
      className: 'state-medium',
      description:
        'Presenta características que justifican una revisión comercial.',
    }
  }

  return {
    label: 'Media',
    className: 'state-neutral',
    description:
      'Forma parte del universo analizado y puede revisarse según el segmento comercial.',
  }
}


function getFinancialScale(
  activos: number | null | undefined,
  ventas: number | null | undefined,
): CommercialState {
  const assets =
    activos ?? 0

  const sales =
    ventas ?? 0

  if (
    assets >= 100000000
    || sales >= 50000000
  ) {
    return {
      label: 'Alta',
      className: 'state-very-high',
      description:
        'La empresa presenta una escala financiera relevante para una revisión comercial.',
    }
  }

  if (
    assets >= 25000000
    || sales >= 10000000
  ) {
    return {
      label: 'Media alta',
      className: 'state-high',
      description:
        'La empresa presenta un tamaño financiero que justifica profundizar su revisión.',
    }
  }

  if (
    assets >= 5000000
    || sales >= 3000000
  ) {
    return {
      label: 'Media',
      className: 'state-medium',
      description:
        'La empresa presenta una escala intermedia dentro de la lectura comercial.',
    }
  }

  return {
    label: 'Por validar',
    className: 'state-neutral',
    description:
      'Conviene complementar la información antes de interpretar su escala financiera.',
  }
}


function getQualityState(
  percentage: number | null | undefined,
): CommercialState {
  const value =
    percentage ?? 0

  if (
    value >= 85
  ) {
    return {
      label: 'Alta',
      className: 'state-very-high',
      description:
        'La información disponible permite realizar una revisión inicial con buen nivel de cobertura.',
    }
  }

  if (
    value >= 65
  ) {
    return {
      label: 'Media',
      className: 'state-medium',
      description:
        'Existe información suficiente para revisar la empresa, aunque conviene complementarla.',
    }
  }

  return {
    label: 'Limitada',
    className: 'state-low',
    description:
      'La información disponible debe complementarse antes de tomar una decisión comercial.',
  }
}


function getSimilarityState(
  similarity: number | null | undefined,
  available: boolean,
): CommercialState {
  if (
    !available
    || similarity === null
    || similarity === undefined
  ) {
    return {
      label: 'Sin referencia',
      className: 'state-neutral',
      description:
        'No se dispone de una referencia histórica suficientemente cercana.',
    }
  }

  if (
    similarity >= 90
  ) {
    return {
      label: 'Alta',
      className: 'state-very-high',
      description:
        'Existen emisores históricos con un perfil financiero muy cercano.',
    }
  }

  if (
    similarity >= 75
  ) {
    return {
      label: 'Media alta',
      className: 'state-high',
      description:
        'Existen emisores históricos con características similares.',
    }
  }

  return {
    label: 'Referencial',
    className: 'state-medium',
    description:
      'Los emisores encontrados pueden utilizarse como referencia complementaria.',
  }
}


/* ============================================================
   RAZONES DE PRIORIDAD
   ============================================================ */

function getReasonStrength(
  value: number,
  maximumMagnitude: number,
) {
  const magnitude =
    Math.abs(value)

  const relativeStrength =
    maximumMagnitude > 0
      ? (
        magnitude
        / maximumMagnitude
      ) * 100
      : 0

  let intensityText =
    'levemente'

  if (
    relativeStrength >= 75
  ) {
    intensityText =
      'de forma muy importante'
  } else if (
    relativeStrength >= 45
  ) {
    intensityText =
      'de forma importante'
  } else if (
    relativeStrength >= 20
  ) {
    intensityText =
      'de forma moderada'
  }

  let commercialLabel =
    'Influencia limitada'

  if (
    value > 0
  ) {
    if (
      relativeStrength >= 75
    ) {
      commercialLabel =
        'Muy favorable'
    } else if (
      relativeStrength >= 45
    ) {
      commercialLabel =
        'Favorable'
    } else if (
      relativeStrength >= 20
    ) {
      commercialLabel =
        'Moderadamente favorable'
    } else {
      commercialLabel =
        'Levemente favorable'
    }
  } else if (
    value < 0
  ) {
    if (
      relativeStrength >= 75
    ) {
      commercialLabel =
        'Muy desfavorable'
    } else if (
      relativeStrength >= 45
    ) {
      commercialLabel =
        'Desfavorable'
    } else if (
      relativeStrength >= 20
    ) {
      commercialLabel =
        'Moderadamente desfavorable'
    } else {
      commercialLabel =
        'Levemente desfavorable'
    }
  }

  return {
    relativeStrength,
    intensityText,
    commercialLabel,
  }
}


function getCommercialReasonDescription(
  feature: string,
  label: string,
  value: number,
  intensityText: string,
): string {
  const text =
    normalizeText(
      `${feature} ${label}`,
    )

  const positive =
    value >= 0

  const action =
    positive
      ? `fortalece ${intensityText} su prioridad de revisión`
      : `reduce ${intensityText} su prioridad de revisión`

  if (
    text.includes('patrimonio')
    && (
      text.includes('anterior')
      || text.includes('menos')
      || text.includes('t-1')
    )
  ) {
    return positive
      ? (
        'La posición patrimonial del año anterior '
        + 'muestra una base financiera previa que '
        + action
        + '.'
      )
      : (
        'La posición patrimonial del año anterior '
        + 'presenta una señal que '
        + action
        + '.'
      )
  }

  if (
    text.includes('patrimonio')
    && text.includes('activo')
    && (
      text.includes('relacion')
      || text.includes('ratio')
    )
  ) {
    return (
      'La proporción de patrimonio frente a los activos '
      + action
      + '.'
    )
  }

  if (
    text.includes('activo')
    && !text.includes('roa')
  ) {
    return positive
      ? (
        'El nivel de activos refleja una escala financiera relevante y '
        + action
        + '.'
      )
      : (
        'El nivel de activos observado '
        + action
        + '.'
      )
  }

  if (
    text.includes('patrimonio')
  ) {
    return positive
      ? (
        'El patrimonio actual refleja respaldo financiero y '
        + action
        + '.'
      )
      : (
        'El nivel de patrimonio actual '
        + action
        + '.'
      )
  }

  if (
    text.includes('venta')
    || text.includes('ingreso')
  ) {
    return positive
      ? (
        'El nivel de ventas refleja una escala de operación que '
        + action
        + '.'
      )
      : (
        'El nivel de ventas observado '
        + action
        + '.'
      )
  }

  if (
    text.includes('empleado')
  ) {
    return positive
      ? (
        'El número de empleados aporta una referencia sobre la escala operativa y '
        + action
        + '.'
      )
      : (
        'La escala operativa aproximada por el número de empleados '
        + action
        + '.'
      )
  }

  if (
    text.includes('roa')
  ) {
    return positive
      ? (
        'La rentabilidad generada sobre los activos aporta una señal favorable y '
        + action
        + '.'
      )
      : (
        'La rentabilidad generada sobre los activos '
        + action
        + '.'
      )
  }

  if (
    text.includes('margen')
  ) {
    return positive
      ? (
        'El margen obtenido sobre las ventas aporta una señal favorable de desempeño y '
        + action
        + '.'
      )
      : (
        'El margen obtenido sobre las ventas '
        + action
        + '.'
      )
  }

  if (
    text.includes('roe')
  ) {
    return positive
      ? (
        'La rentabilidad generada sobre el patrimonio aporta una señal favorable y '
        + action
        + '.'
      )
      : (
        'La rentabilidad generada sobre el patrimonio '
        + action
        + '.'
      )
  }

  return positive
    ? (
      'Esta característica aporta una señal favorable y '
      + action
      + '.'
    )
    : (
      'Esta característica '
      + action
      + '.'
    )
}


/* ============================================================
   COMPARACIÓN DE EMISORES
   ============================================================ */

function calculateDifference(
  prospectValue: number | null | undefined,
  comparableValue: number | null | undefined,
): number | null {
  if (
    prospectValue === null
    || prospectValue === undefined
    || comparableValue === null
    || comparableValue === undefined
  ) {
    return null
  }

  if (
    prospectValue === 0
  ) {
    if (
      comparableValue === 0
    ) {
      return 0
    }

    return null
  }

  return (
    Math.abs(
      comparableValue
      - prospectValue,
    )
    /
    Math.abs(
      prospectValue,
    )
  ) * 100
}


function getCloseness(
  difference: number | null,
) {
  if (
    difference === null
  ) {
    return {
      label: 'Sin dato',
      className: 'closeness-neutral',
    }
  }

  if (
    difference <= 10
  ) {
    return {
      label: 'Muy cercano',
      className: 'closeness-very-high',
    }
  }

  if (
    difference <= 25
  ) {
    return {
      label: 'Cercano',
      className: 'closeness-high',
    }
  }

  if (
    difference <= 50
  ) {
    return {
      label: 'Diferencia moderada',
      className: 'closeness-medium',
    }
  }

  return {
    label: 'Diferente',
    className: 'closeness-low',
  }
}


function buildComparisonMetrics(
  prospectDetail: ProspectDetailResponse,
  profile: IssuerReferenceFinancialProfile,
): ComparisonMetric[] {
  const rawMetrics = [
    {
      key: 'activos',
      label: 'Activos',
      prospectValue:
        prospectDetail
          .indicadores_financieros
          .activos,
      comparableValue:
        profile.activos,
      type:
        'currency' as const,
    },
    {
      key: 'patrimonio',
      label: 'Patrimonio',
      prospectValue:
        prospectDetail
          .indicadores_financieros
          .patrimonio,
      comparableValue:
        profile.patrimonio,
      type:
        'currency' as const,
    },
    {
      key: 'ventas',
      label: 'Ventas',
      prospectValue:
        prospectDetail
          .indicadores_financieros
          .ingresos_ventas,
      comparableValue:
        profile.ingresos_ventas,
      type:
        'currency' as const,
    },
    {
      key: 'empleados',
      label: 'Empleados',
      prospectValue:
        prospectDetail
          .indicadores_financieros
          .numero_empleados,
      comparableValue:
        profile.numero_empleados,
      type:
        'number' as const,
    },
    {
      key: 'ratio_patrimonio_activos',
      label: 'Patrimonio / activos',
      prospectValue:
        prospectDetail
          .indicadores_financieros
          .ratio_patrimonio_activos,
      comparableValue:
        profile.ratio_patrimonio_activos,
      type:
        'percentage' as const,
    },
    {
      key: 'roa',
      label: 'ROA',
      prospectValue:
        prospectDetail
          .indicadores_financieros
          .roa,
      comparableValue:
        profile.roa,
      type:
        'percentage' as const,
    },
    {
      key: 'rotacion_activos',
      label: 'Rotación de activos',
      prospectValue:
        prospectDetail
          .indicadores_financieros
          .rotacion_activos,
      comparableValue:
        profile.rotacion_activos,
      type:
        'decimal' as const,
    },
  ]

  return rawMetrics.map(
    (
      metric,
    ) => {
      const difference =
        calculateDifference(
          metric.prospectValue,
          metric.comparableValue,
        )

      const closeness =
        getCloseness(
          difference,
        )

      return {
        ...metric,
        difference,
        closeness:
          closeness.label,
        closenessClass:
          closeness.className,
      }
    },
  )
}


function formatComparisonValue(
  value: number | null | undefined,
  type:
    | 'currency'
    | 'number'
    | 'percentage'
    | 'decimal',
): string {
  if (
    type === 'currency'
  ) {
    return formatCurrency(
      value,
    )
  }

  if (
    type === 'percentage'
  ) {
    return formatDecimalPercentage(
      value,
      1,
    )
  }

  if (
    type === 'decimal'
  ) {
    return formatDecimal(
      value,
      2,
    )
  }

  return formatNumber(
    value,
  )
}


function getComparableHighlights(
  metrics: ComparisonMetric[],
) {
  return metrics
    .filter(
      (
        metric,
      ) =>
        metric.difference !== null,
    )
    .sort(
      (
        a,
        b,
      ) =>
        (
          a.difference
          ?? Number.MAX_VALUE
        )
        -
        (
          b.difference
          ?? Number.MAX_VALUE
        ),
    )
    .slice(
      0,
      3,
    )
}


function getComparableInterpretation(
  metrics: ComparisonMetric[],
): string {
  const availableMetrics =
    metrics
      .filter(
        (
          metric,
        ) =>
          metric.difference !== null,
      )
      .sort(
        (
          a,
          b,
        ) =>
          (
            a.difference
            ?? Number.MAX_VALUE
          )
          -
          (
            b.difference
            ?? Number.MAX_VALUE
          ),
      )

  if (
    availableMetrics.length === 0
  ) {
    return (
      'No existe información suficiente para realizar '
      + 'una comparación directa de los indicadores.'
    )
  }

  const first =
    availableMetrics[0]

  const second =
    availableMetrics[1]

  const third =
    availableMetrics[2]

  if (
    first
    && second
    && third
  ) {
    return (
      `Las menores diferencias directas se observan en `
      + `${first.label.toLowerCase()}, `
      + `${second.label.toLowerCase()} y `
      + `${third.label.toLowerCase()}. `
      + 'Estos elementos ayudan a comprender visualmente '
      + 'la cercanía financiera entre ambas empresas.'
    )
  }

  if (
    first
    && second
  ) {
    return (
      `Las menores diferencias directas se observan en `
      + `${first.label.toLowerCase()} y `
      + `${second.label.toLowerCase()}.`
    )
  }

  return (
    `La menor diferencia directa se encuentra en `
    + `${first.label.toLowerCase()}.`
  )
}


/* ============================================================
   COMPONENTE
   ============================================================ */

function App() {
  const [
    activeView,
    setActiveView,
  ] =
    useState<ViewName>(
      'prospects',
    )

  const [
    prospects,
    setProspects,
  ] =
    useState<
      ProspectListResponse
      | null
    >(
      null,
    )

  const [
    catalogs,
    setCatalogs,
  ] =
    useState<
      CatalogResponse
      | null
    >(
      null,
    )

  const [
    filters,
    setFilters,
  ] =
    useState<ProspectFilters>(
      INITIAL_FILTERS,
    )

  const [
    searchInput,
    setSearchInput,
  ] =
    useState('')

  const [
    loading,
    setLoading,
  ] =
    useState(true)

  const [
    error,
    setError,
  ] =
    useState<
      string
      | null
    >(
      null,
    )

  const [
    selectedProspect,
    setSelectedProspect,
  ] =
    useState<
      ProspectListItem
      | null
    >(
      null,
    )

  const [
    detail,
    setDetail,
  ] =
    useState<
      ProspectDetailResponse
      | null
    >(
      null,
    )

  const [
    explanation,
    setExplanation,
  ] =
    useState<
      ProspectExplanationResponse
      | null
    >(
      null,
    )

  const [
    detailLoading,
    setDetailLoading,
  ] =
    useState(false)

  const [
    explanationLoading,
    setExplanationLoading,
  ] =
    useState(false)

  const [
    universeTotal,
    setUniverseTotal,
  ] =
    useState(0)

  const [
    universeTopScore,
    setUniverseTopScore,
  ] =
    useState<
      number
      | null
    >(
      null,
    )

  const [
    expandedComparable,
    setExpandedComparable,
  ] =
    useState<
      string
      | null
    >(
      null,
    )


  /* ==========================================================
     CARGA
     ========================================================== */

  useEffect(
    () => {
      async function loadCatalogs() {
        try {
          const response =
            await getCatalogs()

          setCatalogs(
            response,
          )
        } catch (
          requestError
        ) {
          console.error(
            requestError,
          )
        }
      }

      void loadCatalogs()
    },
    [],
  )


  useEffect(
    () => {
      async function loadProspects() {
        setLoading(
          true,
        )

        setError(
          null,
        )

        try {
          const response =
            await getProspects(
              filters,
            )

          setProspects(
            response,
          )

          const isBaseUniverse =
            !filters.search
            && !filters.provincia
            && !filters.tipo_compania
            && (
              filters.page
              ?? 1
            ) === 1

          if (
            isBaseUniverse
          ) {
            setUniverseTotal(
              response
                .metadata
                .total_records,
            )

            setUniverseTopScore(
              response
                .items[0]
                ?.score_afinidad
              ?? null,
            )
          }
        } catch (
          requestError
        ) {
          setError(
            requestError instanceof Error
              ? requestError.message
              : 'No fue posible consultar la información.',
          )
        } finally {
          setLoading(
            false,
          )
        }
      }

      void loadProspects()
    },
    [
      filters,
    ],
  )


  /* ==========================================================
     DATOS DERIVADOS
     ========================================================== */

  const totalRecords =
    prospects
      ?.metadata
      .total_records
    ?? 0

  const currentPage =
    prospects
      ?.metadata
      .page
    ?? 1

  const totalPages =
    prospects
      ?.metadata
      .total_pages
    ?? 1

  const topScore =
    useMemo(
      () => {
        if (
          universeTopScore !== null
        ) {
          return universeTopScore
        }

        return (
          prospects
            ?.items[0]
            ?.score_afinidad
          ?? null
        )
      },
      [
        prospects,
        universeTopScore,
      ],
    )


  const topProvinces =
    useMemo(
      () => {
        if (
          !catalogs
        ) {
          return []
        }

        return [
          ...catalogs.provincias,
        ]
          .sort(
            (
              a,
              b,
            ) =>
              b.count
              - a.count,
          )
          .slice(
            0,
            8,
          )
          .map(
            (
              item,
            ) => ({
              name:
                shortLabel(
                  item.value,
                  18,
                ),
              count:
                item.count,
            }),
          )
      },
      [
        catalogs,
      ],
    )


  const topCompanyTypes =
    useMemo(
      () => {
        if (
          !catalogs
        ) {
          return []
        }

        return [
          ...catalogs
            .tipos_compania,
        ]
          .sort(
            (
              a,
              b,
            ) =>
              b.count
              - a.count,
          )
          .slice(
            0,
            8,
          )
          .map(
            (
              item,
            ) => ({
              name:
                shortLabel(
                  item.value,
                  20,
                ),
              count:
                item.count,
            }),
          )
      },
      [
        catalogs,
      ],
    )


  const topVisibleProspects =
    useMemo(
      () =>
        prospects
          ?.items
          .slice(
            0,
            5,
          )
        ?? [],
      [
        prospects,
      ],
    )


  /* ==========================================================
     ACCIONES
     ========================================================== */

  function closeDetail() {
    setSelectedProspect(
      null,
    )

    setDetail(
      null,
    )

    setExplanation(
      null,
    )

    setExpandedComparable(
      null,
    )
  }


  function changeView(
    view: ViewName,
  ) {
    closeDetail()

    setActiveView(
      view,
    )

    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    })
  }


  function applySearch() {
    setFilters(
      (
        current,
      ) => ({
        ...current,
        page: 1,
        search:
          searchInput.trim()
          || undefined,
      }),
    )
  }


  function clearFilters() {
    setSearchInput(
      '',
    )

    setFilters(
      INITIAL_FILTERS,
    )
  }


  function goToPage(
    page: number,
  ) {
    if (
      page < 1
      || page > totalPages
    ) {
      return
    }

    setFilters(
      (
        current,
      ) => ({
        ...current,
        page,
      }),
    )
  }


  async function openProspect(
    prospect: ProspectListItem,
  ) {
    setSelectedProspect(
      prospect,
    )

    setDetail(
      null,
    )

    setExplanation(
      null,
    )

    setExpandedComparable(
      null,
    )

    setDetailLoading(
      true,
    )

    try {
      const response =
        await getProspectDetail(
          prospect.expediente_key,
        )

      setDetail(
        response,
      )
    } catch (
      requestError
    ) {
      console.error(
        requestError,
      )
    } finally {
      setDetailLoading(
        false,
      )
    }
  }


  async function loadExplanation() {
    if (
      !selectedProspect
    ) {
      return
    }

    setExplanationLoading(
      true,
    )

    try {
      const response =
        await getProspectExplanation(
          selectedProspect
            .expediente_key,
          10,
        )

      setExplanation(
        response,
      )
    } catch (
      requestError
    ) {
      console.error(
        requestError,
      )
    } finally {
      setExplanationLoading(
        false,
      )
    }
  }


  function toggleComparable(
    expedienteKey: number,
  ) {
    const keyId =
      String(
        expedienteKey,
      )

    setExpandedComparable(
      (
        current,
      ) =>
        current === keyId
          ? null
          : keyId,
    )
  }


  /* ==========================================================
     SIDEBAR
     ========================================================== */

  function renderSidebar() {
    return (
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            PF
          </div>

          <div>
            <strong>
              Prospect Finder
            </strong>

            <span>
              Inteligencia comercial BVQ
            </span>
          </div>
        </div>


        <div className="sidebar-caption">
          HERRAMIENTAS
        </div>


        <nav className="sidebar-nav">
          <button
            className={
              activeView === 'prospects'
                ? 'nav-item active'
                : 'nav-item'
            }
            onClick={
              () =>
                changeView(
                  'prospects',
                )
            }
          >
            <Target size={20} />

            <span>
              <strong>
                Prospectos
              </strong>

              <small>
                Empresas prioritarias
              </small>
            </span>
          </button>


          <button
            className={
              activeView === 'analytics'
                ? 'nav-item active'
                : 'nav-item'
            }
            onClick={
              () =>
                changeView(
                  'analytics',
                )
            }
          >
            <BarChart3 size={20} />

            <span>
              <strong>
                Analítica
              </strong>

              <small>
                Visión general del universo
              </small>
            </span>
          </button>


          <button
            className={
              activeView === 'guide'
                ? 'nav-item active'
                : 'nav-item'
            }
            onClick={
              () =>
                changeView(
                  'guide',
                )
            }
          >
            <Info size={20} />

            <span>
              <strong>
                Cómo interpretar
              </strong>

              <small>
                Guía para usar los resultados
              </small>
            </span>
          </button>
        </nav>


        <div className="sidebar-spacer" />


        <div className="sidebar-status">
          <div className="status-dot" />

          <div>
            <span>
              INFORMACIÓN DISPONIBLE
            </span>

            <strong>
              Análisis actualizado
            </strong>
          </div>
        </div>


        <div className="sidebar-footer">
          <span>
            Información de referencia
          </span>

          <strong>
            Estados financieros 2023
          </strong>

          <small>
            Fecha de análisis:
            {' '}
            01 mayo 2024
          </small>
        </div>
      </aside>
    )
  }


  /* ==========================================================
     RESUMEN
     ========================================================== */

  function renderSummaryCards() {
    return (
      <section className="summary-grid">
        <article className="summary-card">
          <div className="summary-icon">
            <Building2 size={22} />
          </div>

          <div>
            <span>
              Empresas analizadas
            </span>

            <strong>
              {
                formatNumber(
                  universeTotal
                  || totalRecords,
                )
              }
            </strong>

            <small>
              universo disponible
            </small>
          </div>
        </article>


        <article className="summary-card">
          <div className="summary-icon">
            <Target size={22} />
          </div>

          <div>
            <span>
              Afinidad más alta
            </span>

            <strong>
              {
                formatScore(
                  topScore,
                )
              }
            </strong>

            <small>
              mayor prioridad relativa
            </small>
          </div>
        </article>


        <article className="summary-card">
          <div className="summary-icon">
            <MapPin size={22} />
          </div>

          <div>
            <span>
              Provincias
            </span>

            <strong>
              {
                catalogs
                  ?.metadata
                  .total_provincias
                ?? '—'
              }
            </strong>

            <small>
              cobertura nacional
            </small>
          </div>
        </article>


        <article className="summary-card">
          <div className="summary-icon">
            <Users size={22} />
          </div>

          <div>
            <span>
              Tipos de empresa
            </span>

            <strong>
              {
                catalogs
                  ?.metadata
                  .total_tipos_compania
                ?? '—'
              }
            </strong>

            <small>
              segmentos disponibles
            </small>
          </div>
        </article>
      </section>
    )
  }


  /* ==========================================================
     PROSPECTOS
     ========================================================== */

  function renderProspectsView() {
    return (
      <>
        <header className="page-header">
          <div>
            <p className="eyebrow">
              INTELIGENCIA COMERCIAL
            </p>

            <h1>
              Empresas prioritarias
            </h1>

            <p className="subtitle">
              Identifique qué empresas conviene revisar primero
              para enfocar mejor la gestión comercial.
            </p>
          </div>


          <div className="decision-date">
            <span>
              Información analizada
            </span>

            <strong>
              Estados financieros 2023
            </strong>

            <small>
              Referencia: 01 mayo 2024
            </small>
          </div>
        </header>


        {
          renderSummaryCards()
        }


        <section className="commercial-guide">
          <div className="guide-heading">
            <div className="guide-icon">
              <Sparkles size={22} />
            </div>

            <div>
              <span className="guide-kicker">
                ¿CÓMO USAR ESTA INFORMACIÓN?
              </span>

              <h2>
                De miles de empresas a una lista comercial manejable
              </h2>
            </div>
          </div>


          <div className="guide-steps">
            <div>
              <span>01</span>
              <strong>Seleccione</strong>

              <p>
                Busque una empresa o concentre
                el análisis por provincia y tipo.
              </p>
            </div>

            <div>
              <span>02</span>
              <strong>Revise</strong>

              <p>
                Observe su posición, tamaño
                financiero e información disponible.
              </p>
            </div>

            <div>
              <span>03</span>
              <strong>Comprenda</strong>

              <p>
                Revise qué características explican
                que la empresa tenga mayor prioridad.
              </p>
            </div>

            <div>
              <span>04</span>
              <strong>Gestione</strong>

              <p>
                Utilice su experiencia comercial
                para decidir si corresponde contactar.
              </p>
            </div>
          </div>
        </section>


        <section className="workspace-card">
          <div className="workspace-header">
            <div>
              <p className="section-kicker">
                LISTA DE OPORTUNIDADES
              </p>

              <h2>
                Empresas ordenadas por prioridad
              </h2>

              <p>
                Las primeras empresas son las que conviene revisar
                antes dentro del universo seleccionado.
              </p>
            </div>


            <div className="result-summary">
              <span>
                {
                  formatNumber(
                    totalRecords,
                  )
                }
              </span>

              <small>
                empresas encontradas
              </small>
            </div>
          </div>


          <div className="filters">
            <div className="search-box">
              <Search size={19} />

              <input
                value={
                  searchInput
                }
                onChange={
                  (
                    event,
                  ) =>
                    setSearchInput(
                      event.target.value,
                    )
                }
                onKeyDown={
                  (
                    event,
                  ) => {
                    if (
                      event.key === 'Enter'
                    ) {
                      applySearch()
                    }
                  }
                }
                placeholder="Buscar empresa, RUC o expediente"
              />

              <button
                className="search-button"
                onClick={
                  applySearch
                }
              >
                Buscar
              </button>
            </div>


            <select
              value={
                filters.provincia
                ?? ''
              }
              onChange={
                (
                  event,
                ) =>
                  setFilters(
                    (
                      current,
                    ) => ({
                      ...current,
                      page: 1,
                      provincia:
                        event.target.value
                        || undefined,
                    }),
                  )
              }
            >
              <option value="">
                Todas las provincias
              </option>

              {
                catalogs
                  ?.provincias
                  .map(
                    (
                      item,
                    ) => (
                      <option
                        key={
                          item.value
                        }
                        value={
                          item.value
                        }
                      >
                        {
                          item.value
                        }
                      </option>
                    ),
                  )
              }
            </select>


            <select
              value={
                filters.tipo_compania
                ?? ''
              }
              onChange={
                (
                  event,
                ) =>
                  setFilters(
                    (
                      current,
                    ) => ({
                      ...current,
                      page: 1,
                      tipo_compania:
                        event.target.value
                        || undefined,
                    }),
                  )
              }
            >
              <option value="">
                Todos los tipos
              </option>

              {
                catalogs
                  ?.tipos_compania
                  .map(
                    (
                      item,
                    ) => (
                      <option
                        key={
                          item.value
                        }
                        value={
                          item.value
                        }
                      >
                        {
                          item.value
                        }
                      </option>
                    ),
                  )
              }
            </select>


            <button
              className="clear-button"
              onClick={
                clearFilters
              }
            >
              Limpiar
            </button>
          </div>


          <div className="table-help">
            <Info size={18} />

            <span>
              La afinidad permite ordenar empresas y decidir
              cuáles revisar primero. Un valor alto no significa
              que necesariamente vaya a convertirse en emisor.
            </span>
          </div>


          {
            error
            && (
              <div className="error-box">
                {
                  error
                }
              </div>
            )
          }


          <div className="table-wrapper">
            <table className="prospects-table">
              <thead>
                <tr>
                  <th>Prioridad</th>
                  <th>Empresa</th>
                  <th>Provincia</th>
                  <th>Tipo</th>
                  <th>Afinidad</th>
                  <th>Nivel</th>
                  <th>Emisor similar</th>
                  <th>Información</th>
                </tr>
              </thead>


              <tbody>
                {
                  loading
                  ? (
                    <tr>
                      <td
                        colSpan={8}
                        className="table-message"
                      >
                        Consultando empresas...
                      </td>
                    </tr>
                  )
                  : prospects
                    ?.items
                    .length
                    ? prospects
                        .items
                        .map(
                          (
                            prospect,
                          ) => {
                            const band =
                              getRankingBand(
                                prospect
                                  .percentil_ranking,
                              )

                            return (
                              <tr
                                key={
                                  prospect
                                    .expediente_key
                                }
                                onClick={
                                  () =>
                                    void openProspect(
                                      prospect,
                                    )
                                }
                              >
                                <td>
                                  <div className="rank-cell">
                                    <span className="rank">
                                      #
                                      {
                                        formatNumber(
                                          prospect
                                            .ranking,
                                        )
                                      }
                                    </span>

                                    <span
                                      className={
                                        `ranking-band ${band.className}`
                                      }
                                    >
                                      {
                                        band.label
                                      }
                                    </span>
                                  </div>
                                </td>


                                <td>
                                  <div className="company-cell">
                                    <strong>
                                      {
                                        prospect.nombre
                                        ?? 'Sin nombre'
                                      }
                                    </strong>

                                    <span>
                                      RUC
                                      {' '}
                                      {
                                        prospect.ruc
                                        ?? '—'
                                      }
                                    </span>
                                  </div>
                                </td>


                                <td>
                                  {
                                    prospect.provincia
                                    ?? '—'
                                  }
                                </td>


                                <td>
                                  {
                                    prospect.tipo_compania
                                    ?? '—'
                                  }
                                </td>


                                <td>
                                  <div className="score-cell">
                                    <strong>
                                      {
                                        formatScore(
                                          prospect
                                            .score_afinidad,
                                        )
                                      }
                                    </strong>

                                    <div className="score-track">
                                      <span
                                        style={{
                                          width:
                                            scoreWidth(
                                              prospect
                                                .score_afinidad,
                                            ),
                                        }}
                                      />
                                    </div>
                                  </div>
                                </td>


                                <td>
                                  <span
                                    className={
                                      `ranking-band ${band.className}`
                                    }
                                  >
                                    {
                                      band.label
                                    }
                                  </span>
                                </td>


                                <td>
                                  {
                                    prospect
                                      .similitud_emisores
                                      .comparables_disponibles
                                    ? (
                                      <div className="similarity-cell">
                                        <strong>
                                          {
                                            formatPercentage(
                                              prospect
                                                .similitud_emisores
                                                .similitud_top1,
                                              1,
                                            )
                                          }
                                        </strong>

                                        <span>
                                          similitud máxima
                                        </span>
                                      </div>
                                    )
                                    : (
                                      <span className="muted-inline">
                                        Sin referencia
                                      </span>
                                    )
                                  }
                                </td>


                                <td>
                                  <div className="quality-cell">
                                    <strong>
                                      {
                                        formatPercentage(
                                          prospect
                                            .calidad_datos
                                            .pct_features_disponibles,
                                          0,
                                        )
                                      }
                                    </strong>

                                    <span>
                                      disponible
                                    </span>
                                  </div>
                                </td>
                              </tr>
                            )
                          },
                        )
                    : (
                      <tr>
                        <td
                          colSpan={8}
                          className="table-message"
                        >
                          No existen empresas para los filtros seleccionados.
                        </td>
                      </tr>
                    )
                }
              </tbody>
            </table>
          </div>


          <div className="pagination">
            <span>
              Página
              {' '}
              {
                formatNumber(
                  currentPage,
                )
              }
              {' '}
              de
              {' '}
              {
                formatNumber(
                  totalPages,
                )
              }
            </span>

            <div>
              <button
                disabled={
                  currentPage <= 1
                }
                onClick={
                  () =>
                    goToPage(
                      currentPage - 1,
                    )
                }
              >
                <ChevronLeft size={18} />
                Anterior
              </button>

              <button
                disabled={
                  currentPage >= totalPages
                }
                onClick={
                  () =>
                    goToPage(
                      currentPage + 1,
                    )
                }
              >
                Siguiente
                <ChevronRight size={18} />
              </button>
            </div>
          </div>
        </section>
      </>
    )
  }


  /* ==========================================================
     ANALÍTICA
     ========================================================== */

  function renderAnalyticsView() {
    return (
      <>
        <header className="page-header">
          <div>
            <p className="eyebrow">
              VISIÓN COMERCIAL
            </p>

            <h1>
              Radiografía de las empresas
            </h1>

            <p className="subtitle">
              Conozca cómo está distribuido el universo de empresas
              para definir segmentos y preparar acciones comerciales.
            </p>
          </div>


          <div className="decision-date">
            <span>
              Universo disponible
            </span>

            <strong>
              {
                formatNumber(
                  universeTotal
                  || totalRecords,
                )
              }
              {' '}
              empresas
            </strong>

            <small>
              cobertura nacional
            </small>
          </div>
        </header>


        {
          renderSummaryCards()
        }


        <section className="analytics-grid">
          <article className="analytics-card">
            <div className="card-heading">
              <div>
                <p className="section-kicker">
                  UBICACIÓN
                </p>

                <h2>
                  ¿Dónde están las empresas?
                </h2>

                <p>
                  Provincias con mayor número de empresas
                  dentro del universo disponible.
                </p>
              </div>

              <MapPin size={22} />
            </div>


            <div className="chart-shell">
              <ResponsiveContainer
                width="100%"
                height={330}
              >
                <BarChart
                  data={
                    topProvinces
                  }
                  layout="vertical"
                >
                  <CartesianGrid
                    strokeDasharray="3 3"
                    horizontal={false}
                  />

                  <XAxis
                    type="number"
                    tickLine={false}
                    axisLine={false}
                  />

                  <YAxis
                    dataKey="name"
                    type="category"
                    width={125}
                    tickLine={false}
                    axisLine={false}
                  />

                  <Tooltip />

                  <Bar
                    dataKey="count"
                    name="Empresas"
                    fill="#0f6fae"
                    radius={[
                      0,
                      6,
                      6,
                      0,
                    ]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </article>


          <article className="analytics-card">
            <div className="card-heading">
              <div>
                <p className="section-kicker">
                  SEGMENTOS
                </p>

                <h2>
                  Tipos de empresa
                </h2>

                <p>
                  Principales grupos disponibles
                  para organizar la prospección.
                </p>
              </div>

              <Layers3 size={22} />
            </div>


            <div className="chart-shell">
              <ResponsiveContainer
                width="100%"
                height={330}
              >
                <BarChart
                  data={
                    topCompanyTypes
                  }
                  layout="vertical"
                >
                  <CartesianGrid
                    strokeDasharray="3 3"
                    horizontal={false}
                  />

                  <XAxis
                    type="number"
                    tickLine={false}
                    axisLine={false}
                  />

                  <YAxis
                    dataKey="name"
                    type="category"
                    width={145}
                    tickLine={false}
                    axisLine={false}
                  />

                  <Tooltip />

                  <Bar
                    dataKey="count"
                    name="Empresas"
                    fill="#d9a90c"
                    radius={[
                      0,
                      6,
                      6,
                      0,
                    ]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </article>
        </section>


        <section className="analytics-grid">
          <article className="analytics-card">
            <div className="card-heading">
              <div>
                <p className="section-kicker">
                  PRIORIDADES
                </p>

                <h2>
                  Empresas para revisar primero
                </h2>
              </div>

              <Target size={22} />
            </div>


            <div className="mini-ranking">
              {
                topVisibleProspects
                  .map(
                    (
                      prospect,
                    ) => (
                      <button
                        key={
                          prospect
                            .expediente_key
                        }
                        onClick={
                          () =>
                            void openProspect(
                              prospect,
                            )
                        }
                      >
                        <span className="mini-rank">
                          #
                          {
                            prospect.ranking
                          }
                        </span>

                        <div>
                          <strong>
                            {
                              prospect.nombre
                            }
                          </strong>

                          <span>
                            {
                              prospect.provincia
                              ?? '—'
                            }
                            {' · '}
                            {
                              prospect.tipo_compania
                              ?? '—'
                            }
                          </span>
                        </div>

                        <span className="mini-score">
                          {
                            formatScore(
                              prospect
                                .score_afinidad,
                            )
                          }
                        </span>
                      </button>
                    ),
                  )
              }
            </div>
          </article>


          <article className="analytics-card">
            <div className="card-heading">
              <div>
                <p className="section-kicker">
                  USO COMERCIAL
                </p>

                <h2>
                  ¿Qué puedo hacer con esta información?
                </h2>
              </div>

              <TrendingUp size={22} />
            </div>


            <div className="insight-list">
              <div>
                <MapPin size={20} />

                <p>
                  <strong>
                    Defina zonas de interés.
                  </strong>
                  {' '}
                  Identifique dónde se concentra el mayor número
                  de posibles prospectos.
                </p>
              </div>

              <div>
                <Layers3 size={20} />

                <p>
                  <strong>
                    Organice campañas.
                  </strong>
                  {' '}
                  Trabaje grupos de empresas con características similares.
                </p>
              </div>

              <div>
                <Target size={20} />

                <p>
                  <strong>
                    Priorice su tiempo.
                  </strong>
                  {' '}
                  Empiece por las empresas ubicadas en las primeras posiciones.
                </p>
              </div>

              <div>
                <Info size={20} />

                <p>
                  <strong>
                    Complemente con su experiencia.
                  </strong>
                  {' '}
                  La herramienta ayuda a enfocar,
                  pero la decisión final corresponde al asesor.
                </p>
              </div>
            </div>
          </article>
        </section>
      </>
    )
  }


  /* ==========================================================
     GUÍA
     ========================================================== */

  function renderGuideView() {
    return (
      <>
        <header className="page-header">
          <div>
            <p className="eyebrow">
              GUÍA COMERCIAL
            </p>

            <h1>
              Cómo interpretar los resultados
            </h1>

            <p className="subtitle">
              Una guía sencilla para entender qué significa cada
              resultado antes de utilizarlo en una gestión comercial.
            </p>
          </div>
        </header>


        <section className="model-explainer">
          <article>
            <div className="explainer-icon">
              <Target size={23} />
            </div>

            <div>
              <span>PRIORIDAD</span>

              <h3>
                Afinidad de la empresa
              </h3>

              <p>
                Permite ordenar las empresas y reconocer cuáles
                justifican una revisión más temprana.
              </p>

              <strong>
                Mayor afinidad = mayor prioridad de revisión.
              </strong>
            </div>
          </article>


          <article>
            <div className="explainer-icon">
              <Sparkles size={23} />
            </div>

            <div>
              <span>RAZONES</span>

              <h3>
                ¿Por qué aparece priorizada?
              </h3>

              <p>
                La ficha muestra qué características ayudaron
                o redujeron la prioridad.
              </p>

              <strong>
                También muestra qué tan fuerte es cada razón.
              </strong>
            </div>
          </article>


          <article>
            <div className="explainer-icon">
              <Users size={23} />
            </div>

            <div>
              <span>REFERENCIAS</span>

              <h3>
                Emisores similares
              </h3>

              <p>
                Presenta emisores históricos con perfiles
                financieros parecidos al prospecto.
              </p>

              <strong>
                La comparación utiliza siete indicadores financieros.
              </strong>
            </div>
          </article>
        </section>


        <section className="flow-card">
          <div className="card-heading">
            <div>
              <p className="section-kicker">
                PROCESO RECOMENDADO
              </p>

              <h2>
                De la lista a una gestión comercial
              </h2>
            </div>
          </div>


          <div className="commercial-flow">
            <div>
              <span>01</span>
              <strong>Seleccione</strong>
              <small>
                Defina un segmento o busque una empresa.
              </small>
            </div>

            <div>
              <span>02</span>
              <strong>Priorice</strong>
              <small>
                Comience por las empresas mejor posicionadas.
              </small>
            </div>

            <div>
              <span>03</span>
              <strong>Revise</strong>
              <small>
                Analice tamaño, información y referencias.
              </small>
            </div>

            <div>
              <span>04</span>
              <strong>Compare</strong>
              <small>
                Revise las siete características frente a emisores históricos.
              </small>
            </div>

            <div className="human-step">
              <span>05</span>
              <strong>Decida</strong>
              <small>
                Determine si corresponde iniciar una gestión.
              </small>
            </div>
          </div>
        </section>
      </>
    )
  }


  /* ==========================================================
     DETALLE
     ========================================================== */

  function renderDetailPanel() {
    if (
      !selectedProspect
    ) {
      return null
    }


    const band =
      getRankingBand(
        detail
          ?.priorizacion
          .percentil_ranking
        ?? selectedProspect
          .percentil_ranking,
      )


    const qualityPercentage =
      detail
        ?.calidad_datos
        .pct_features_disponibles
      ?? 0


    const qualityFeatures =
      detail
        ?.calidad_datos
        .n_features_disponibles
      ?? 0


    const visibleReasons =
      [
        ...(
          explanation
            ?.principales_factores
          ?? []
        ),
      ]
        .sort(
          (
            a,
            b,
          ) =>
            Math.abs(
              b.shap_value,
            )
            -
            Math.abs(
              a.shap_value,
            ),
        )
        .slice(
          0,
          8,
        )


    const maximumReasonMagnitude =
      visibleReasons.reduce(
        (
          maximum,
          factor,
        ) =>
          Math.max(
            maximum,
            Math.abs(
              factor.shap_value,
            ),
          ),
        0,
      )


    if (
      !detail
      && !detailLoading
    ) {
      return null
    }


    const activos =
      detail
        ?.indicadores_financieros
        .activos
      ?? null

    const patrimonio =
      detail
        ?.indicadores_financieros
        .patrimonio
      ?? null

    const ventas =
      detail
        ?.indicadores_financieros
        .ingresos_ventas
      ?? null

    const empleados =
      detail
        ?.indicadores_financieros
        .numero_empleados
      ?? null


    const similarityAvailable =
      detail
        ?.similitud_emisores
        .comparables_disponibles
      ?? false


    const similarityTop =
      detail
        ?.similitud_emisores
        .similitud_top1
      ?? null


    const priorityState =
      getPriorityState(
        detail
          ?.priorizacion
          .percentil_ranking
        ?? selectedProspect
          .percentil_ranking,
      )


    const financialScale =
      getFinancialScale(
        activos,
        ventas,
      )


    const qualityState =
      getQualityState(
        qualityPercentage,
      )


    const similarityState =
      getSimilarityState(
        similarityTop,
        similarityAvailable,
      )


    const strengths: string[] =
      []


    if (
      (
        activos
        ?? 0
      ) >= 25000000
    ) {
      strengths.push(
        'Presenta una escala de activos relevante para profundizar su revisión.',
      )
    }


    if (
      (
        patrimonio
        ?? 0
      ) >= 10000000
    ) {
      strengths.push(
        'Cuenta con una base patrimonial relevante dentro de su perfil financiero.',
      )
    }


    if (
      (
        ventas
        ?? 0
      ) >= 10000000
    ) {
      strengths.push(
        'Su volumen de ventas evidencia una operación comercial de escala relevante.',
      )
    }


    if (
      (
        empleados
        ?? 0
      ) >= 50
    ) {
      strengths.push(
        'Su número de empleados refleja una estructura operativa de tamaño relevante.',
      )
    }


    if (
      similarityAvailable
      && (
        similarityTop
        ?? 0
      ) >= 85
    ) {
      strengths.push(
        'Presenta una alta cercanía con perfiles de emisores históricos.',
      )
    }


    if (
      qualityPercentage >= 85
    ) {
      strengths.push(
        'La información disponible tiene una cobertura suficiente para una primera revisión.',
      )
    }


    if (
      strengths.length === 0
    ) {
      strengths.push(
        'La empresa forma parte del universo priorizado y merece una revisión individual.',
      )
    }


    const validationItems: string[] = [
      'Confirmar que la información financiera utilizada continúa vigente.',
      'Identificar si la empresa tiene necesidades actuales de financiamiento.',
      'Investigar planes de expansión, inversión o crecimiento que puedan requerir recursos.',
      'Validar el interés de sus accionistas o administración en alternativas del mercado de valores.',
    ]


    if (
      qualityPercentage < 85
    ) {
      validationItems.push(
        'Completar o validar la información faltante antes de avanzar con el contacto.',
      )
    }


    let recommendedAction =
      'Revisar antes de definir una acción comercial.'


    if (
      priorityState.label === 'Muy alta'
      && qualityPercentage >= 65
    ) {
      recommendedAction =
        'Revisar para posible contacto comercial.'
    } else if (
      priorityState.label === 'Alta'
      && qualityPercentage >= 65
    ) {
      recommendedAction =
        'Profundizar la revisión y evaluar un posible contacto.'
    } else if (
      qualityPercentage < 65
    ) {
      recommendedAction =
        'Complementar información antes de evaluar un contacto.'
    }


    const opportunitySummary =
      `La empresa se encuentra en un nivel de prioridad ${priorityState.label.toLowerCase()} `
      + `dentro del universo analizado. Su escala financiera se considera ${financialScale.label.toLowerCase()} `
      + `para efectos de esta lectura comercial. `
      + (
        similarityAvailable
          ? `Además, presenta una similitud de ${formatPercentage(similarityTop, 1)} con su referencia histórica más cercana. `
          : ''
      )
      + `La información disponible tiene un nivel ${qualityState.label.toLowerCase()}. `
      + 'Estos elementos sirven como punto de partida para decidir si corresponde profundizar la gestión.'


    return (
      <div className="detail-overlay">
        <button
          className="overlay-background"
          onClick={
            closeDetail
          }
          aria-label="Cerrar detalle"
        />


        <aside className="detail-panel">
          <div className="detail-header">
            <div>
              <div className="detail-heading-row">
                <span className="detail-label">
                  PRIORIDAD
                  {' '}
                  #
                  {
                    selectedProspect
                      .ranking
                  }
                </span>

                <span
                  className={
                    `ranking-band ${band.className}`
                  }
                >
                  {
                    band.label
                  }
                </span>
              </div>


              <h2>
                {
                  selectedProspect
                    .nombre
                }
              </h2>


              <p>
                RUC
                {' '}
                {
                  selectedProspect.ruc
                  ?? '—'
                }
                {' · '}
                {
                  selectedProspect.provincia
                  ?? '—'
                }
              </p>
            </div>


            <button
              className="close-button"
              onClick={
                closeDetail
              }
              aria-label="Cerrar"
            >
              <X size={22} />
            </button>
          </div>


          {
            detailLoading
            ? (
              <div className="detail-loading">
                Consultando información...
              </div>
            )
            : detail
              ? (
                <div className="detail-content">

                  {/* ==================================================
                      RESUMEN
                      ================================================== */}

                  <section className="opportunity-summary">
                    <div className="opportunity-summary-title">
                      <div className="opportunity-summary-icon">
                        <Sparkles size={22} />
                      </div>

                      <div>
                        <span>
                          RESUMEN DE OPORTUNIDAD
                        </span>

                        <h3>
                          Lectura comercial de la empresa
                        </h3>
                      </div>
                    </div>


                    <p>
                      {
                        opportunitySummary
                      }
                    </p>


                    <div className="opportunity-action">
                      <span>
                        ACCIÓN SUGERIDA
                      </span>

                      <strong>
                        {
                          recommendedAction
                        }
                      </strong>
                    </div>
                  </section>


                  {/* ==================================================
                      LECTURA COMERCIAL
                      ================================================== */}

                  <section className="detail-section">
                    <div className="section-title-row">
                      <div>
                        <h3>
                          Lectura comercial rápida
                        </h3>

                        <p>
                          Una visión resumida para saber
                          dónde conviene profundizar la revisión.
                        </p>
                      </div>
                    </div>


                    <div className="commercial-pulse-grid">
                      <article className="pulse-card">
                        <span>
                          Prioridad comercial
                        </span>

                        <strong
                          className={
                            `pulse-status ${priorityState.className}`
                          }
                        >
                          {
                            priorityState.label
                          }
                        </strong>

                        <p>
                          {
                            priorityState.description
                          }
                        </p>
                      </article>


                      <article className="pulse-card">
                        <span>
                          Escala financiera
                        </span>

                        <strong
                          className={
                            `pulse-status ${financialScale.className}`
                          }
                        >
                          {
                            financialScale.label
                          }
                        </strong>

                        <p>
                          {
                            financialScale.description
                          }
                        </p>
                      </article>


                      <article className="pulse-card">
                        <span>
                          Cercanía con emisores
                        </span>

                        <strong
                          className={
                            `pulse-status ${similarityState.className}`
                          }
                        >
                          {
                            similarityState.label
                          }
                        </strong>

                        <p>
                          {
                            similarityState.description
                          }
                        </p>
                      </article>


                      <article className="pulse-card">
                        <span>
                          Información disponible
                        </span>

                        <strong
                          className={
                            `pulse-status ${qualityState.className}`
                          }
                        >
                          {
                            qualityState.label
                          }
                        </strong>

                        <p>
                          {
                            qualityState.description
                          }
                        </p>
                      </article>
                    </div>


                    <p className="orientation-note">
                      Esta lectura es orientativa y sirve para
                      facilitar la revisión comercial. No constituye
                      una decisión automática sobre la empresa.
                    </p>
                  </section>


                  {/* ==================================================
                      FORTALEZAS
                      ================================================== */}

                  <section className="detail-section">
                    <div className="section-title-row">
                      <div>
                        <h3>
                          Fortalezas y aspectos a validar
                        </h3>

                        <p>
                          Un resumen práctico para preparar
                          la revisión antes de un posible contacto.
                        </p>
                      </div>
                    </div>


                    <div className="strengths-grid">
                      <article className="strength-card">
                        <div className="strength-card-title positive-title">
                          <CheckCircle2 size={20} />

                          <strong>
                            Fortalezas observadas
                          </strong>
                        </div>

                        <ul>
                          {
                            strengths.map(
                              (
                                item,
                              ) => (
                                <li key={item}>
                                  {
                                    item
                                  }
                                </li>
                              ),
                            )
                          }
                        </ul>
                      </article>


                      <article className="strength-card">
                        <div className="strength-card-title warning-title">
                          <CircleAlert size={20} />

                          <strong>
                            Aspectos a validar
                          </strong>
                        </div>

                        <ul>
                          {
                            validationItems.map(
                              (
                                item,
                              ) => (
                                <li key={item}>
                                  {
                                    item
                                  }
                                </li>
                              ),
                            )
                          }
                        </ul>
                      </article>
                    </div>
                  </section>


                  {/* ==================================================
                      TAMAÑO FINANCIERO
                      ================================================== */}

                  <section className="detail-section">
                    <div className="section-title-row">
                      <div>
                        <h3>
                          Tamaño financiero
                        </h3>

                        <p>
                          Información principal para una
                          primera evaluación comercial.
                        </p>
                      </div>
                    </div>


                    <div className="financial-grid">
                      <div>
                        <span>
                          Activos
                        </span>

                        <strong>
                          {
                            formatCurrency(
                              detail
                                .indicadores_financieros
                                .activos,
                            )
                          }
                        </strong>
                      </div>


                      <div>
                        <span>
                          Patrimonio
                        </span>

                        <strong>
                          {
                            formatCurrency(
                              detail
                                .indicadores_financieros
                                .patrimonio,
                            )
                          }
                        </strong>
                      </div>


                      <div>
                        <span>
                          Ventas
                        </span>

                        <strong>
                          {
                            formatCurrency(
                              detail
                                .indicadores_financieros
                                .ingresos_ventas,
                            )
                          }
                        </strong>
                      </div>


                      <div>
                        <span>
                          Empleados
                        </span>

                        <strong>
                          {
                            formatNumber(
                              detail
                                .indicadores_financieros
                                .numero_empleados,
                            )
                          }
                        </strong>
                      </div>
                    </div>
                  </section>


                  {/* ==================================================
                      RAZONES
                      ================================================== */}

                  <section className="detail-section">
                    <div className="section-title-row">
                      <div>
                        <h3>
                          ¿Qué explica su prioridad?
                        </h3>

                        <p>
                          Cada razón muestra si favorece o reduce la
                          prioridad y qué tan fuerte es su influencia.
                        </p>
                      </div>


                      {
                        !explanation
                        && (
                          <button
                            className="explain-button"
                            disabled={
                              explanationLoading
                            }
                            onClick={
                              () =>
                                void loadExplanation()
                            }
                          >
                            <Sparkles size={19} />

                            {
                              explanationLoading
                              ? 'Analizando...'
                              : 'Ver razones'
                            }
                          </button>
                        )
                      }
                    </div>


                    {
                      !explanation
                      && (
                        <div className="explanation-placeholder">
                          <Sparkles size={24} />

                          <div>
                            <strong>
                              Conozca las razones principales
                            </strong>

                            <p>
                              Podrá ver qué aspectos financieros
                              tienen mayor influencia en la posición
                              de esta empresa.
                            </p>
                          </div>
                        </div>
                      )
                    }


                    {
                      explanation
                      && (
                        <>
                          <div className="factors-list">
                            {
                              visibleReasons.map(
                                (
                                  factor,
                                ) => {
                                  const strength =
                                    getReasonStrength(
                                      factor.shap_value,
                                      maximumReasonMagnitude,
                                    )

                                  const description =
                                    getCommercialReasonDescription(
                                      factor.feature,
                                      factor.label,
                                      factor.shap_value,
                                      strength.intensityText,
                                    )

                                  return (
                                    <div
                                      key={
                                        factor.feature
                                      }
                                      className="factor-row"
                                    >
                                      <div>
                                        <strong>
                                          {
                                            factor.label
                                          }
                                        </strong>

                                        <span>
                                          {
                                            description
                                          }
                                        </span>
                                      </div>


                                      <span
                                        className={
                                          factor.shap_value >= 0
                                            ? 'factor-value positive'
                                            : 'factor-value negative'
                                        }
                                      >
                                        {
                                          strength
                                            .commercialLabel
                                        }
                                        {' · '}
                                        {
                                          formatPercentage(
                                            strength
                                              .relativeStrength,
                                            0,
                                          )
                                        }
                                      </span>
                                    </div>
                                  )
                                },
                              )
                            }
                          </div>


                          <div className="shap-note">
                            <Info size={18} />

                            <p>
                              <strong>
                                ¿Cómo leer los porcentajes?
                              </strong>
                              {' '}
                              100% identifica la razón con mayor
                              influencia dentro de esta empresa.
                              Las demás se comparan contra ella.
                              No representa la probabilidad de
                              convertirse en emisor.
                            </p>
                          </div>
                        </>
                      )
                    }
                  </section>


                  {/* ==================================================
                      EMISORES SIMILARES
                      ================================================== */}

                  <section className="detail-section">
                    <div className="section-title-row">
                      <div>
                        <h3>
                          Emisores similares
                        </h3>

                        <p>
                          Empresas que ya participaron en el mercado de
                          valores y presentan perfiles financieros parecidos.
                        </p>
                      </div>
                    </div>


                    {
                      detail
                        .similitud_emisores
                        .comparables_disponibles
                      ? (
                        <>
                          <div className="comparables-summary">
                            <div>
                              <span>
                                Referencias encontradas
                              </span>

                              <strong>
                                {
                                  detail
                                    .similitud_emisores
                                    .comparables
                                    .length
                                }
                              </strong>
                            </div>


                            <div>
                              <span>
                                Mayor similitud
                              </span>

                              <strong>
                                {
                                  formatPercentage(
                                    detail
                                      .similitud_emisores
                                      .similitud_top1,
                                    1,
                                  )
                                }
                              </strong>
                            </div>


                            <div>
                              <span>
                                Indicadores comparados
                              </span>

                              <strong>
                                7 financieros
                              </strong>
                            </div>
                          </div>


                          <div className="comparables-detailed-list">
                            {
                              detail
                                .similitud_emisores
                                .comparables
                                .map(
                                  (
                                    comparable,
                                  ) => {
                                    const keyId =
                                      String(
                                        comparable
                                          .emisor
                                          .expediente_key,
                                      )

                                    const profile =
                                      comparable
                                        .emisor
                                        .perfil_financiero

                                    const isExpanded =
                                      expandedComparable
                                      === keyId

                                    const metrics =
                                      profile
                                      ? buildComparisonMetrics(
                                          detail,
                                          profile,
                                        )
                                      : []

                                    const highlights =
                                      getComparableHighlights(
                                        metrics,
                                      )

                                    const interpretation =
                                      getComparableInterpretation(
                                        metrics,
                                      )

                                    return (
                                      <article
                                        className="comparable-card"
                                        key={
                                          `${
                                            comparable.orden
                                          }-${keyId}`
                                        }
                                      >
                                        <div className="comparable-card-main">
                                          <div className="comparable-order">
                                            {
                                              comparable.orden
                                            }
                                          </div>


                                          <div className="comparable-main-info">
                                            <strong>
                                              {
                                                comparable
                                                  .emisor
                                                  .nombre
                                              }
                                            </strong>

                                            <span>
                                              {
                                                comparable
                                                  .emisor
                                                  .provincia
                                                ?? 'Provincia no disponible'
                                              }
                                              {' · '}
                                              Perfil financiero
                                              {' '}
                                              {
                                                comparable
                                                  .emisor
                                                  .anio_perfil
                                              }
                                            </span>


                                            <div className="comparable-highlights">
                                              {
                                                comparable
                                                  .mismo_tipo_compania
                                                && (
                                                  <span className="closeness-very-high">
                                                    Mismo tipo de compañía
                                                  </span>
                                                )
                                              }

                                              {
                                                highlights.map(
                                                  (
                                                    metric,
                                                  ) => (
                                                    <span
                                                      key={
                                                        metric.key
                                                      }
                                                      className={
                                                        metric
                                                          .closenessClass
                                                      }
                                                    >
                                                      {
                                                        metric.label
                                                      }
                                                      {' · '}
                                                      {
                                                        metric.closeness
                                                      }
                                                    </span>
                                                  ),
                                                )
                                              }
                                            </div>
                                          </div>


                                          <div className="comparable-actions">
                                            <div className="comparable-score">
                                              <strong>
                                                {
                                                  formatPercentage(
                                                    comparable
                                                      .similitud,
                                                    1,
                                                  )
                                                }
                                              </strong>

                                              <span>
                                                similitud general
                                              </span>
                                            </div>


                                            <button
                                              className="comparable-expand-button"
                                              onClick={
                                                () =>
                                                  toggleComparable(
                                                    comparable
                                                      .emisor
                                                      .expediente_key,
                                                  )
                                              }
                                            >
                                              {
                                                isExpanded
                                                ? (
                                                  <>
                                                    Ocultar
                                                    <ChevronUp size={16} />
                                                  </>
                                                )
                                                : (
                                                  <>
                                                    Ver comparación
                                                    <ChevronDown size={16} />
                                                  </>
                                                )
                                              }
                                            </button>
                                          </div>
                                        </div>


                                        {
                                          isExpanded
                                          && (
                                            <div className="comparable-detail">
                                              {
                                                profile
                                                ? (
                                                  <>
                                                    <div className="comparison-title">
                                                      <div>
                                                        <span>
                                                          ¿POR QUÉ ES SIMILAR?
                                                        </span>

                                                        <h4>
                                                          Comparación financiera directa
                                                        </h4>
                                                      </div>


                                                      {
                                                        highlights[0]
                                                        && (
                                                          <div className="main-match">
                                                            <span>
                                                              Menor diferencia directa
                                                            </span>

                                                            <strong>
                                                              {
                                                                highlights[0]
                                                                  .label
                                                              }
                                                            </strong>
                                                          </div>
                                                        )
                                                      }
                                                    </div>


                                                    <div className="comparison-table">
                                                      <div className="comparison-table-header">
                                                        <span>
                                                          Indicador
                                                        </span>

                                                        <span>
                                                          Prospecto
                                                        </span>

                                                        <span>
                                                          Emisor histórico
                                                        </span>

                                                        <span>
                                                          Diferencia
                                                        </span>
                                                      </div>


                                                      {
                                                        metrics.map(
                                                          (
                                                            metric,
                                                          ) => (
                                                            <div
                                                              className="comparison-table-row"
                                                              key={
                                                                metric.key
                                                              }
                                                            >
                                                              <div>
                                                                <strong>
                                                                  {
                                                                    metric.label
                                                                  }
                                                                </strong>

                                                                <span
                                                                  className={
                                                                    `closeness-label ${
                                                                      metric.closenessClass
                                                                    }`
                                                                  }
                                                                >
                                                                  {
                                                                    metric.closeness
                                                                  }
                                                                </span>
                                                              </div>


                                                              <span>
                                                                {
                                                                  formatComparisonValue(
                                                                    metric.prospectValue,
                                                                    metric.type,
                                                                  )
                                                                }
                                                              </span>


                                                              <span>
                                                                {
                                                                  formatComparisonValue(
                                                                    metric.comparableValue,
                                                                    metric.type,
                                                                  )
                                                                }
                                                              </span>


                                                              <strong>
                                                                {
                                                                  metric.difference
                                                                  === null
                                                                    ? '—'
                                                                    : formatPercentage(
                                                                        metric.difference,
                                                                        0,
                                                                      )
                                                                }
                                                              </strong>
                                                            </div>
                                                          ),
                                                        )
                                                      }
                                                    </div>


                                                    <div className="commercial-comparison-reading">
                                                      <Sparkles size={19} />

                                                      <div>
                                                        <span>
                                                          LECTURA COMERCIAL
                                                        </span>

                                                        <p>
                                                          {
                                                            interpretation
                                                          }
                                                          {' '}
                                                          El emisor histórico puede utilizarse
                                                          como referencia para comprender qué
                                                          empresas con características financieras
                                                          similares ya tuvieron presencia en el
                                                          mercado de valores.
                                                        </p>
                                                      </div>
                                                    </div>


                                                    <div className="difference-note">
                                                      <Info size={17} />

                                                      <p>
                                                        <strong>
                                                          Importante:
                                                        </strong>
                                                        {' '}
                                                        la similitud general de
                                                        {' '}
                                                        {
                                                          formatPercentage(
                                                            comparable.similitud,
                                                            1,
                                                          )
                                                        }
                                                        {' '}
                                                        fue calculada por Prospect Finder
                                                        utilizando percentiles anuales de los
                                                        siete indicadores y distancia entre
                                                        perfiles. Las diferencias de esta tabla
                                                        comparan los valores financieros originales
                                                        y sirven para facilitar su interpretación;
                                                        no constituyen una descomposición matemática
                                                        del porcentaje de similitud.
                                                      </p>
                                                    </div>
                                                  </>
                                                )
                                                : (
                                                  <div className="comparable-detail-message">
                                                    <Info size={19} />

                                                    <p>
                                                      El emisor fue identificado como comparable,
                                                      pero su perfil financiero histórico no está
                                                      disponible para esta consulta.
                                                    </p>
                                                  </div>
                                                )
                                              }
                                            </div>
                                          )
                                        }
                                      </article>
                                    )
                                  },
                                )
                            }
                          </div>


                          <div className="comparison-note">
                            <Info size={18} />

                            <p>
                              Los emisores similares se comparan utilizando
                              activos, patrimonio, ventas, empleados,
                              patrimonio frente a activos, ROA y rotación
                              de activos. Funcionan como referencias
                              históricas y no como garantía de que el
                              prospecto vaya a convertirse en emisor.
                            </p>
                          </div>
                        </>
                      )
                      : (
                        <p className="muted-text">
                          No existen referencias suficientes para esta empresa.
                        </p>
                      )
                    }
                  </section>


                  {/* ==================================================
                      CALIDAD
                      ================================================== */}

                  <section className="detail-section">
                    <div className="section-title-row">
                      <div>
                        <h3>
                          Información disponible
                        </h3>

                        <p>
                          Indica qué tan completa está la información
                          utilizada para revisar esta empresa.
                        </p>
                      </div>


                      <strong className="quality-score">
                        {
                          formatPercentage(
                            qualityPercentage,
                            0,
                          )
                        }
                      </strong>
                    </div>


                    <div className="quality-track">
                      <span
                        style={{
                          width:
                            percentageWidth(
                              qualityPercentage,
                            ),
                        }}
                      />
                    </div>


                    <p className="quality-caption">
                      {
                        formatNumber(
                          qualityFeatures,
                        )
                      }
                      {' '}
                      datos disponibles para realizar el análisis.
                    </p>
                  </section>


                  {/* ==================================================
                      PRÓXIMO PASO
                      ================================================== */}

                  <section className="next-step-card">
                    <div>
                      <span>
                        PRÓXIMO PASO COMERCIAL
                      </span>

                      <h3>
                        {
                          recommendedAction
                        }
                      </h3>
                    </div>


                    <ul>
                      <li>
                        Confirmar que la información financiera continúa vigente.
                      </li>

                      <li>
                        Investigar posibles necesidades actuales de financiamiento.
                      </li>

                      <li>
                        Revisar los emisores similares para preparar referencias.
                      </li>

                      <li>
                        Aplicar el criterio del asesor antes de iniciar la gestión.
                      </li>
                    </ul>
                  </section>


                  <p className="method-note">
                    Prospect Finder ayuda a priorizar y organizar
                    el trabajo comercial. Las clasificaciones presentadas
                    son orientativas y no sustituyen el criterio del especialista.
                  </p>
                </div>
              )
              : (
                <div className="detail-loading">
                  No fue posible cargar la información.
                </div>
              )
          }
        </aside>
      </div>
    )
  }


  /* ==========================================================
     APP
     ========================================================== */

  return (
    <div className="app-shell">
      {
        renderSidebar()
      }

      <main className="main-content">
        <div className="content-inner">
          {
            activeView === 'prospects'
              ? renderProspectsView()
              : activeView === 'analytics'
                ? renderAnalyticsView()
                : renderGuideView()
          }
        </div>
      </main>

      {
        renderDetailPanel()
      }
    </div>
  )
}


export default App