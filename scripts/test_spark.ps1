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
    if (-not (Test-Path "$env:JAVA_HOME\bin\java.exe")) {
        throw "No se encontró JDK 17 en $env:JAVA_HOME"
    }

    $env:PATH = "$env:JAVA_HOME\bin;$env:PATH"
    $env:TEMP = "$drive\.tmp"
    $env:TMP = "$drive\.tmp"
    $env:SPARK_LOCAL_IP = "127.0.0.1"
    $env:SPARK_LOCAL_DIRS = "$drive\.tmp\spark"
    $basePython = & "$drive\.venv\Scripts\python.exe" -c "import sys; print(sys._base_executable)"
    $env:PYSPARK_PYTHON = $basePython.Trim()
    $env:PYSPARK_DRIVER_PYTHON = "$drive\.venv\Scripts\python.exe"
    $env:RUN_SPARK_TESTS = "1"

    & "$drive\.venv\Scripts\python.exe" -m pytest "$drive\tests\test_mora_cosechas_spark.py" -q
    if ($LASTEXITCODE -ne 0) {
        throw "Las pruebas Spark fallaron con código $LASTEXITCODE"
    }
}
finally {
    if ($createdDrive) {
        subst $drive /D
    }
}
