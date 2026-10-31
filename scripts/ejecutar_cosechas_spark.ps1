$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$drive = "P:"
$createdDrive = $false

try {
    if (-not (Test-Path "$drive\")) {
        subst $drive $projectRoot
        $createdDrive = $true
    }

    $env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot"
    $env:PATH = "$env:JAVA_HOME\bin;$env:PATH"
    $env:TEMP = "$drive\.tmp"
    $env:TMP = "$drive\.tmp"
    $env:SPARK_LOCAL_IP = "127.0.0.1"
    $env:SPARK_LOCAL_DIRS = "$drive\.tmp\spark"
    $basePython = & "$drive\.venv\Scripts\python.exe" -c "import sys; print(sys._base_executable)"
    $env:PYSPARK_PYTHON = $basePython.Trim()
    $env:PYSPARK_DRIVER_PYTHON = "$drive\.venv\Scripts\python.exe"

    & "$drive\.venv\Scripts\python.exe" -m src.analisis.mora_cosechas_spark @args
    if ($LASTEXITCODE -ne 0) {
        throw "El análisis Spark falló con código $LASTEXITCODE"
    }
}
finally {
    if ($createdDrive) {
        subst $drive /D
    }
}
