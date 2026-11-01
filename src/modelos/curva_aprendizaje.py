"""Curva de aprendizaje: cómo cambia la métrica según cuántos préstamos se usan.
Se encontró que la versión original de ingesta genera un unico archivo 1k de filas
que es insuficiente para determinar si el modelo funciona. 

Se decidio, con algo de ayuda, elaborar una forma de probar el rendimiento utilizando diferente
tamaños de muestra. Estadisticamente se está buscando el tamaño de la muestra que 
sea representativo del universo, pero se desconoce que mecanismo se utiliza en en modelos
para determinar dicho valor.

Uso:
    python -m src.modelos.curva_aprendizaje
    python -m src.modelos.curva_aprendizaje --datos data/processed/prestamos_terminados.parquet
    python -m src.modelos.curva_aprendizaje --tamanos 1000,10000,100000 --repeticiones 3

Diseño:
    * La prueba es **fuera de tiempo**: se entrena con las cosechas más antiguas
      y se evalúa con las más recientes, que es lo que haría la financiera en la
      práctica. Una partición aleatoria mezclaría épocas y daría métricas
      optimistas.
    * El conjunto de prueba es el mismo para todos los tamaños, así las
      métricas son comparables entre sí.
    * Para cada tamaño se entrena varias veces con submuestras aleatorias
      distintas; la desviación entre repeticiones indica cuánto del resultado
      es al azar.
"""

import argparse
import warnings

import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import accuracy_score, roc_auc_score

from src import config
from src.modelos.pipelines import (
    construir_gradient_boosting,
    construir_mlp,
    construir_regresion_logistica,
)

ORDEN_GRADOS = "ABCDEFG"
TAMANO_INICIAL = 100
RUTA_RESULTADOS = config.REPORTES / "curva_aprendizaje.csv"
MODELOS = {
    "logistica": construir_regresion_logistica,
    "mlp": construir_mlp,
    "boosting": construir_gradient_boosting,
}


def cargar_datos(ruta=None) -> pd.DataFrame:
    """Lee los préstamos limpios desde Parquet o CSV.

    Args:
        ruta: Archivo o carpeta Parquet, o CSV. Si es ``None`` usa el Parquet
            completo cuando existe y, si no, la muestra versionada en el repo.

    Returns:
        DataFrame con las variables del modelo, ``es_malo``, ``grade`` y
        ``cosecha``.
    """
    if ruta is None:
        ruta = config.PARQUET_PRESTAMOS if config.PARQUET_PRESTAMOS.exists() else (
            config.DATA_MUESTRA / "muestra_prestamos.csv"
        )
    if str(ruta).endswith(".csv"):
        return pd.read_csv(ruta)
    return pd.read_parquet(ruta)


def dividir_fuera_de_tiempo(df: pd.DataFrame, fraccion_prueba: float = 0.2):
    """Separa entrenamiento (cosechas antiguas) y prueba (cosechas recientes).
    
    Se parte así dado que datos recientes tiene bias contra prestamos que fueron
    pagados de inmediato o muy temprano en su vida, esencialmente outliers en la
    historia, se da mas peso a aquello que tiene ya tiempo.

    El corte cae en un cambio de mes, así que los préstamos de una misma
    cosecha nunca quedan en los dos lados.

    Args:
        df: Préstamos con la columna ``cosecha`` (``"YYYY-MM"``).
        fraccion_prueba: Fracción aproximada de filas para la prueba.

    Returns:
        Tupla ``(entrenamiento, prueba)``.

    Raises:
        ValueError: Si el corte deja vacío alguno de los dos conjuntos.
    """
    corte = df["cosecha"].sort_values().iloc[int(len(df) * (1 - fraccion_prueba))]
    entrenamiento = df[df["cosecha"] < corte]
    prueba = df[df["cosecha"] >= corte]
    if entrenamiento.empty or prueba.empty:
        raise ValueError(f"El corte por cosecha ({corte}) deja un conjunto vacío.")
    return entrenamiento, prueba


def tamanos_por_defecto(n_entrenamiento: int) -> list:
    """Tamaños que se duplican desde 100 hasta usar todo el entrenamiento.

    Args:
        n_entrenamiento: Filas disponibles para entrenar.

    Returns:
        Lista creciente que termina en ``n_entrenamiento``.
    """
    tamanos, n = [], TAMANO_INICIAL
    while n < n_entrenamiento:
        tamanos.append(n)
        n *= 2
    return tamanos + [n_entrenamiento]


def _variables(df: pd.DataFrame) -> pd.DataFrame:
    return df[config.VARIABLES_NUMERICAS + config.VARIABLES_CATEGORICAS]


def linea_base_grado(prueba: pd.DataFrame) -> dict:
    """Métricas de la regla por grado, sin entrenar nada.

    Args:
        prueba: Conjunto de prueba con ``grade`` y ``es_malo``.

    Returns:
        AUC usando el grado (A = menos riesgo) como puntaje, y la exactitud de
        decir siempre "pagará", que es la referencia para leer la exactitud.
    """
    puntaje = prueba["grade"].map(ORDEN_GRADOS.index)
    y = prueba[config.VARIABLE_OBJETIVO]
    return {
        "auc_grado": roc_auc_score(y, puntaje),
        "exactitud_todos_buenos": 1 - y.mean(),
    }


def curva_aprendizaje(
    entrenamiento: pd.DataFrame,
    prueba: pd.DataFrame,
    tamanos: list,
    repeticiones: int = 5,
    semilla: int = 42,
) -> pd.DataFrame:
    """Entrena cada modelo con submuestras de distinto tamaño y mide en la prueba.

    Args:
        entrenamiento: Préstamos disponibles para entrenar.
        prueba: Préstamos de evaluación, fijos para todos los tamaños.
        tamanos: Número de filas de cada submuestra. Los mayores que el
            entrenamiento se omiten.
        repeticiones: Submuestras aleatorias distintas por tamaño.
        semilla: Semilla base; la repetición ``i`` usa ``semilla + i``.

    Returns:
        Una fila por (tamaño, modelo, repetición) con ``auc`` y ``exactitud``
        (umbral 0.5).
    """
    X_prueba = _variables(prueba)
    y_prueba = prueba[config.VARIABLE_OBJETIVO]
    filas = []
    for n in tamanos:
        if n > len(entrenamiento):
            continue
        for i in range(repeticiones):
            muestra = entrenamiento.sample(n=n, random_state=semilla + i)
            X, y = _variables(muestra), muestra[config.VARIABLE_OBJETIVO]
            for nombre, constructor in MODELOS.items():
                modelo = constructor(semilla + i)
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", ConvergenceWarning)
                    modelo.fit(X, y)
                probabilidad = modelo.predict_proba(X_prueba)[:, 1]
                filas.append(
                    {
                        "n": n,
                        "modelo": nombre,
                        "repeticion": i,
                        "auc": roc_auc_score(y_prueba, probabilidad),
                        "exactitud": accuracy_score(y_prueba, probabilidad >= 0.5),
                    }
                )
    return pd.DataFrame(filas)


def resumir(resultados: pd.DataFrame) -> pd.DataFrame:
    """Promedio y desviación de las métricas por tamaño y modelo.

    Args:
        resultados: Salida de :func:`curva_aprendizaje`.

    Returns:
        Tabla con ``auc_media``, ``auc_desv``, ``exactitud_media`` y
        ``exactitud_desv``.
    """
    resumen = resultados.groupby(["n", "modelo"])[["auc", "exactitud"]].agg(["mean", "std"])
    resumen.columns = [f"{m}_{'media' if f == 'mean' else 'desv'}" for m, f in resumen.columns]
    return resumen.reset_index()


def main() -> None:
    """Corre la curva de aprendizaje y guarda los resultados en ``reports/``."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--datos", help="Parquet o CSV de préstamos limpios.")
    parser.add_argument("--tamanos", help="Tamaños separados por coma, ej. 1000,10000.")
    parser.add_argument("--repeticiones", type=int, default=5)
    parser.add_argument("--fraccion-prueba", type=float, default=0.2)
    parser.add_argument("--salida", default=str(RUTA_RESULTADOS))
    args = parser.parse_args()

    df = cargar_datos(args.datos)
    entrenamiento, prueba = dividir_fuera_de_tiempo(df, args.fraccion_prueba)
    tamanos = (
        [int(t) for t in args.tamanos.split(",")]
        if args.tamanos
        else tamanos_por_defecto(len(entrenamiento))
    )

    print(f"Entrenamiento: {len(entrenamiento):,} filas "
          f"({entrenamiento['cosecha'].min()} a {entrenamiento['cosecha'].max()})")
    print(f"Prueba:        {len(prueba):,} filas "
          f"({prueba['cosecha'].min()} a {prueba['cosecha'].max()}), "
          f"{int(prueba[config.VARIABLE_OBJETIVO].sum())} castigados")
    base = linea_base_grado(prueba)
    print(f"Línea base por grado: AUC {base['auc_grado']:.3f} | "
          f"exactitud de 'todos pagan': {base['exactitud_todos_buenos']:.3f}\n")

    resultados = curva_aprendizaje(entrenamiento, prueba, tamanos, args.repeticiones)
    resumen = resumir(resultados)
    resumen.to_csv(args.salida, index=False)
    print(resumen.round(3).to_string(index=False))
    print(f"\nGuardado en {args.salida}")


if __name__ == "__main__":
    main()
