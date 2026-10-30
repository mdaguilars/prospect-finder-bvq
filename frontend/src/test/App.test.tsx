import {
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from 'vitest'
import {
  render,
  screen,
  waitFor,
} from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import App from '../App'

import {
  getCatalogs,
  getProspectDetail,
  getProspectExplanation,
  getProspects,
} from '../services/api'

import type {
  CatalogResponse,
} from '../types/catalog'

import type {
  ProspectExplanationResponse,
} from '../types/explainability'

import type {
  ProspectDetailResponse,
  ProspectListResponse,
} from '../types/prospect'

vi.mock('../services/api', () => ({
  getCatalogs: vi.fn(),
  getProspects: vi.fn(),
  getProspectDetail: vi.fn(),
  getProspectExplanation: vi.fn(),
}))

const mockedGetCatalogs =
  vi.mocked(getCatalogs)

const mockedGetProspects =
  vi.mocked(getProspects)

const mockedGetProspectDetail =
  vi.mocked(getProspectDetail)

const mockedGetProspectExplanation =
  vi.mocked(getProspectExplanation)

const catalogsMock: CatalogResponse = {
  provincias: [
    {
      value: 'PICHINCHA',
      count: 43487,
    },
    {
      value: 'GUAYAS',
      count: 52560,
    },
  ],
  tipos_compania: [
    {
      value: 'ANÓNIMA',
      count: 65769,
    },
    {
      value: 'RESPONSABILIDAD LIMITADA',
      count: 28972,
    },
  ],
  metadata: {
    total_provincias: 24,
    total_tipos_compania: 9,
  },
}

const prospectsMock: ProspectListResponse = {
  metadata: {
    page: 1,
    page_size: 25,
    total_records: 137156,
    total_pages: 5487,
    sort: 'score_afinidad_desc',
    score_note:
      'Indicador relativo de priorización.',
    similarity_note:
      'Similitud financiera independiente del score.',
  },
  items: [
    {
      expediente_key: 1001,
      ruc: '0000000000000',
      nombre: 'EMPRESA PRUEBA A S.A.',
      anio: 2023,
      fecha_decision: '2024-05-01',
      tipo_compania: 'ANÓNIMA',
      provincia: 'PICHINCHA',
      ranking: 1,
      score_afinidad: 0.973694,
      percentil_ranking: 100,
      calidad_datos: {
        n_features_disponibles: 25,
        pct_features_disponibles: 100,
      },
      similitud_emisores: {
        comparables_disponibles: true,
        similitud_top1: 95.6,
        similitud_top5_promedio: 94.9,
        estado: 'disponible',
      },
    },
  ],
}

const detailMock: ProspectDetailResponse = {
  empresa: {
    expediente_key: 1001,
    ruc: '0000000000000',
    nombre: 'EMPRESA PRUEBA A S.A.',
    anio: 2023,
    fecha_decision: '2024-05-01',
    tipo_compania: 'ANÓNIMA',
    provincia: 'PICHINCHA',
  },
  priorizacion: {
    ranking: 1,
    score_afinidad: 0.973694,
    percentil_ranking: 100,
    nota:
      'Indicador relativo de priorización.',
  },
  calidad_datos: {
    n_features_disponibles: 25,
    pct_features_disponibles: 100,
  },
  indicadores_financieros: {
    activos: 143900000,
    patrimonio: 14200000,
    ingresos_ventas: 47600000,
    numero_empleados: 38,
    ratio_patrimonio_activos: 0.0987,
    roa: 0.041,
    margen_neto: 0.084,
    rotacion_activos: 0.331,
    roe: 0.415,
    crecimiento_activos: 0.21,
    crecimiento_patrimonio: 0.18,
    crecimiento_ventas: 0.14,
    crecimiento_empleados: 0.08,
  },
  similitud_emisores: {
    comparables_disponibles: true,
    similitud_top1: 95.6,
    similitud_top5_promedio: 94.9,
    distancia_top1: 0.12,
    n_emisores_comparados: 272,
    estado: 'disponible',
    metodologia:
      'Percentiles anuales y distancia euclidiana.',
    nota:
      'La similitud no modifica el score.',
    comparables: [
      {
        orden: 1,
        similitud: 95.6,
        distancia_percentiles: 0.12,
        mismo_tipo_compania: true,
        emisor: {
          expediente_key: 9001,
          ruc: '1790000000001',
          nombre: 'MOTDIS',
          anio_perfil: 2022,
          fecha_decision_perfil: '2023-05-01',
          fecha_primera_inscripcion: '2023-08-01',
          tipo_compania: 'ANÓNIMA',
          provincia: 'PICHINCHA',
        },
      },
    ],
  },
  modelo: {
    nombre: 'v10_hgb_financial_c3',
    configuracion: 'C3_CONSERVATIVE',
  },
}

const explanationMock:
  ProspectExplanationResponse = {
    empresa: {
      expediente_key: 1001,
      ruc: '0000000000000',
      nombre: 'EMPRESA PRUEBA A S.A.',
      anio: 2023,
    },
    score: {
      modelo: 0.973694,
      ranking_operativo: 0.973694,
      diferencia: 0,
      nota:
        'El score es un indicador de priorización.',
    },
    shap: {
      base_value: 0.178347,
      reconstructed_score: 0.973694,
      local_error: 0,
      background_train_size: 75,
      max_evals: 51,
      method: 'PermutationExplainer',
      reference: 'TRAIN',
    },
    principales_factores: [
      {
        feature: 'activos_final',
        label: 'Activos',
        value: 143900000,
        shap_value: 0.4194,
        abs_shap_value: 0.4194,
        direction: 'aumenta_afinidad',
      },
      {
        feature: 'tipo_compania',
        label: 'Tipo de compañía',
        value: 'ANÓNIMA',
        shap_value: -0.0392,
        abs_shap_value: 0.0392,
        direction: 'reduce_afinidad',
      },
    ],
    factores_que_aumentan_afinidad: [
      {
        feature: 'activos_final',
        label: 'Activos',
        value: 143900000,
        shap_value: 0.4194,
        abs_shap_value: 0.4194,
        direction: 'aumenta_afinidad',
      },
    ],
    factores_que_reducen_afinidad: [
      {
        feature: 'tipo_compania',
        label: 'Tipo de compañía',
        value: 'ANÓNIMA',
        shap_value: -0.0392,
        abs_shap_value: 0.0392,
        direction: 'reduce_afinidad',
      },
    ],
    metadata: {
      model_name: 'v10_hgb_financial_c3',
      config_id: 'C3_CONSERVATIVE',
      features_total: 25,
      top_n: 10,
      interpretation:
        'Las contribuciones explican el comportamiento del modelo.',
    },
    ranking: {
      posicion: 1,
      percentil: 100,
    },
  }

beforeEach(() => {
  vi.clearAllMocks()

  mockedGetCatalogs.mockResolvedValue(
    catalogsMock,
  )

  mockedGetProspects.mockResolvedValue(
    prospectsMock,
  )

  mockedGetProspectDetail.mockResolvedValue(
    detailMock,
  )

  mockedGetProspectExplanation.mockResolvedValue(
    explanationMock,
  )
})

describe('Prospect Finder BVQ', () => {
  it('carga el ranking y los catálogos iniciales', async () => {
    render(<App />)

    expect(
      await screen.findByText(
        'EMPRESA PRUEBA A S.A.',
      ),
    ).toBeInTheDocument()

    expect(
      screen.getByText('Empresas ordenadas por prioridad'),
    ).toBeInTheDocument()

    expect(
      screen.getAllByText('137.156')[0],
    ).toBeInTheDocument()

    expect(
      screen.getByText('24'),
    ).toBeInTheDocument()

    expect(
      screen.getByText('9'),
    ).toBeInTheDocument()

    expect(
      mockedGetCatalogs,
    ).toHaveBeenCalledTimes(1)

    expect(
      mockedGetProspects,
    ).toHaveBeenCalledWith({
      page: 1,
      page_size: 25,
    })
  })

  it('aplica una búsqueda desde el formulario', async () => {
    const user = userEvent.setup()

    render(<App />)

    await screen.findByText(
      'EMPRESA PRUEBA A S.A.',
    )

    const input = screen.getByPlaceholderText(
      'Buscar empresa, RUC o expediente',
    )

    await user.type(
      input,
      'cuyabeno',
    )

    await user.click(
      screen.getByRole('button', {
        name: 'Buscar',
      }),
    )

    await waitFor(() => {
      expect(
        mockedGetProspects,
      ).toHaveBeenLastCalledWith({
        page: 1,
        page_size: 25,
        search: 'cuyabeno',
      })
    })
  })

  it('abre el detalle financiero de una empresa', async () => {
    const user = userEvent.setup()

    render(<App />)

    const company =
      await screen.findByText(
        'EMPRESA PRUEBA A S.A.',
      )

    await user.click(company)

    expect(
      await screen.findByText(
        'Tamaño financiero',
      ),
    ).toBeInTheDocument()

    expect(
      mockedGetProspectDetail,
    ).toHaveBeenCalledWith(1001)

    expect(
      screen.getByText(
        'Prioridad comercial',
      ),
    ).toBeInTheDocument()

    expect(
      screen.getByText('MOTDIS'),
    ).toBeInTheDocument()
  })

  it('consulta y presenta factores SHAP positivos y negativos', async () => {
    const user = userEvent.setup()

    render(<App />)

    const company =
      await screen.findByText(
        'EMPRESA PRUEBA A S.A.',
      )

    await user.click(company)

    const analyzeButton =
      await screen.findByRole('button', {
        name: 'Ver razones',
      })

    await user.click(analyzeButton)

    await waitFor(() => {
      expect(
        mockedGetProspectExplanation,
      ).toHaveBeenCalledWith(
        1001,
        10,
      )
    })

    expect(
      await screen.findByText(/Muy favorable/),
    ).toBeInTheDocument()

    expect(
      screen.getByText(/Levemente desfavorable/),
    ).toBeInTheDocument()
  })
})
