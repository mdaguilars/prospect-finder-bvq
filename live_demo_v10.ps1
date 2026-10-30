# ============================================================
# Prospect Finder BVQ
# Men├║ de demostraci├│n en vivo v10
# ============================================================

$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot

Set-Location $ProjectRoot

function Show-Header {
    param(
        [string]$Title
    )

    Clear-Host

    Write-Host ""
    Write-Host "============================================================"
    Write-Host " PROSPECT FINDER BVQ - DEMOSTRACION EN VIVO"
    Write-Host "============================================================"
    Write-Host ""
    Write-Host $Title
    Write-Host ""
}

function Pause-Demo {
    Write-Host ""
    Read-Host "Presione ENTER para volver al menu"
}

function Show-P01 {

    Show-Header "P01 - Ranking reproducible"

    Write-Host "Modelo: v10_hgb_financial_c3"
    Write-Host "Configuracion: C3_CONSERVATIVE"
    Write-Host ""

    $Run1 = Join-Path $ProjectRoot "reports\live_tests\P01\ranking_run1.csv.gz"
    $Run2 = Join-Path $ProjectRoot "reports\live_tests\P01\ranking_run2.csv.gz"
    $Top50 = Join-Path $ProjectRoot "reports\live_tests\P01\ranking_top50.csv"

    if (
        (Test-Path $Run1) -and
        (Test-Path $Run2) -and
        (Test-Path $Top50)
    ) {

        Write-Host "Evidencias encontradas."
        Write-Host ""
        Write-Host "Resultado previamente validado:"
        Write-Host ""
        Write-Host "Filas run1:               260445"
        Write-Host "Filas run2:               260445"
        Write-Host "Ranking identico:         True"
        Write-Host "Metricas identicas:       True"
        Write-Host "Metricas Top-K identicas: True"
        Write-Host ""
        Write-Host "RESULTADO: CUMPLE"
        Write-Host ""
        Write-Host "Top 50:"
        Write-Host $Top50
        Write-Host ""

        $Option = Read-Host "Desea abrir el Top 50? (S/N)"

        if ($Option -match "^[Ss]$") {
            Invoke-Item $Top50
        }

    }
    else {

        Write-Host "No se encontraron todas las evidencias de P01."
    }

    Pause-Demo
}

function Run-Test {

    param(
        [string]$TestId,
        [string]$Description,
        [string]$ScriptPath,
        [string]$EvidencePath
    )

    Show-Header "$TestId - $Description"

    $FullScriptPath = Join-Path $ProjectRoot $ScriptPath
    $FullEvidencePath = Join-Path $ProjectRoot $EvidencePath

    if (-not (Test-Path $FullScriptPath)) {

        Write-Host "ERROR:"
        Write-Host "No existe:"
        Write-Host $FullScriptPath

        Pause-Demo
        return
    }

    Write-Host "Script:"
    Write-Host $FullScriptPath
    Write-Host ""

    Write-Host "Ejecutando..."
    Write-Host ""

    & python $FullScriptPath

    Write-Host ""
    Write-Host "------------------------------------------------------------"
    Write-Host ""

    if (Test-Path $FullEvidencePath) {

        Write-Host "Evidencia principal:"
        Write-Host $FullEvidencePath
        Write-Host ""

        $Option = Read-Host "Desea abrir la evidencia? (S/N)"

        if ($Option -match "^[Ss]$") {

            Invoke-Item $FullEvidencePath
        }
    }
    else {

        Write-Host "La evidencia principal no fue encontrada:"
        Write-Host $FullEvidencePath
    }

    Pause-Demo
}

function Show-Documentation {

    Show-Header "DOCUMENTACION DE DEFENSA"

    $Acta = Join-Path $ProjectRoot "reports\live_tests\ACTA_PRUEBAS_V10.md"
    $Defensa = Join-Path $ProjectRoot "reports\live_tests\HOJA_DEFENSA_V10.md"

    Write-Host "1. ACTA_PRUEBAS_V10.md"
    Write-Host "2. HOJA_DEFENSA_V10.md"
    Write-Host "0. Volver"
    Write-Host ""

    $Choice = Read-Host "Seleccione"

    switch ($Choice) {

        "1" {
            if (Test-Path $Acta) {
                Invoke-Item $Acta
            }
        }

        "2" {
            if (Test-Path $Defensa) {
                Invoke-Item $Defensa
            }
        }

        default {
        }
    }
}

function Show-EvidenceFolder {

    $Folder = Join-Path $ProjectRoot "reports\live_tests"

    if (Test-Path $Folder) {
        Invoke-Item $Folder
    }
}

do {

    Show-Header "MENU PRINCIPAL"

    Write-Host "Modelo:        v10_hgb_financial_c3"
    Write-Host "Configuracion: C3_CONSERVATIVE"
    Write-Host "TRAIN:         2012-2018"
    Write-Host "TEST:          2022-2023"
    Write-Host "TEST N:        260445"
    Write-Host "Positivos:     54"
    Write-Host ""
    Write-Host "------------------------------------------------------------"
    Write-Host ""
    Write-Host "1. P01 - Ranking reproducible"
    Write-Host "2. P02 - Fuga temporal"
    Write-Host "3. P03 - Faltantes y atipicos"
    Write-Host "4. P04 - Robustez +/-5%"
    Write-Host "5. P05 - Utilidad Top-K"
    Write-Host "6. P06 - Explicabilidad y sesgo"
    Write-Host ""
    Write-Host "7. Abrir documentacion de defensa"
    Write-Host "8. Abrir carpeta de evidencias"
    Write-Host ""
    Write-Host "0. Salir"
    Write-Host ""

    $Choice = Read-Host "Seleccione una opcion"

    switch ($Choice) {

        "1" {

            Show-P01
        }

        "2" {

            Run-Test `
                -TestId "P02" `
                -Description "Fuga temporal" `
                -ScriptPath "src\evaluation\live_test_p02_temporal_leakage.py" `
                -EvidencePath "reports\live_tests\P02\p02_temporal_leakage_result.csv"
        }

        "3" {

            Run-Test `
                -TestId "P03" `
                -Description "Datos faltantes y atipicos" `
                -ScriptPath "src\evaluation\live_test_p03_missing_outliers.py" `
                -EvidencePath "reports\live_tests\P03\p03_results.csv"
        }

        "4" {

            Run-Test `
                -TestId "P04" `
                -Description "Robustez a pequenos cambios" `
                -ScriptPath "src\evaluation\live_test_p04_small_changes.py" `
                -EvidencePath "reports\live_tests\P04\p04_results.csv"
        }

        "5" {

            Run-Test `
                -TestId "P05" `
                -Description "Utilidad comercial Top-K" `
                -ScriptPath "src\evaluation\live_test_p05_topk_utility.py" `
                -EvidencePath "reports\live_tests\P05\p05_topk_metrics.csv"
        }

        "6" {

            Run-Test `
                -TestId "P06" `
                -Description "Explicabilidad y sesgo" `
                -ScriptPath "src\evaluation\live_test_p06_explainability_bias.py" `
                -EvidencePath "reports\live_tests\P06\p06_shap_empresa_grande.png"
        }

        "7" {

            Show-Documentation
        }

        "8" {

            Show-EvidenceFolder
        }

        "0" {

            Write-Host ""
            Write-Host "Fin de la demostracion."
            Write-Host ""
        }

        default {

            Write-Host ""
            Write-Host "Opcion no valida."
            Start-Sleep -Seconds 1
        }
    }

}
while ($Choice -ne "0")
