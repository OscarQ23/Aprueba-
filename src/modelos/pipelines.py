"""Pipelines de scikit-learn: preprocesamiento + modelo.

La regresión logística y el MLP comparten el mismo preprocesamiento, así la
diferencia en las métricas se debe al modelo y no a la preparación de los datos
(ver docs/decisiones.md, decisiones 004 y 005). El gradiente boosting usa su
propia preparación porque los árboles no necesitan escalar y manejan nulos y
categorías de forma nativa.
"""

import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

from src import config


def construir_preprocesador() -> ColumnTransformer:
    """Imputa y escala las variables numéricas; codifica las categóricas.

    Además de imputar con la mediana, agrega una columna 0/1 por cada variable
    que tuvo nulos al ajustar: en el buró, que falte un dato suele ser
    informativo y la mediana lo taparía.

    Returns:
        ``ColumnTransformer`` sin ajustar. Las categorías nuevas que aparezcan
        al predecir se ignoran en lugar de fallar.
    """
    numericas = Pipeline(
        [
            ("imputar", SimpleImputer(strategy="median", add_indicator=True)),
            ("escalar", StandardScaler()),
        ]
    )
    categoricas = OneHotEncoder(handle_unknown="ignore")
    return ColumnTransformer(
        [
            ("num", numericas, config.VARIABLES_NUMERICAS),
            ("cat", categoricas, config.VARIABLES_CATEGORICAS),
        ]
    )


def construir_preprocesador_arboles() -> ColumnTransformer:
    """Deja las numéricas intactas (con sus nulos) y codifica las categóricas.

    Returns:
        ``ColumnTransformer`` sin ajustar. Las columnas numéricas van primero y
        las categóricas después, en el orden de ``config``. Una categoría nueva
        al predecir se trata como dato faltante.
    """
    categoricas = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=np.nan)
    return ColumnTransformer(
        [
            ("num", "passthrough", config.VARIABLES_NUMERICAS),
            ("cat", categoricas, config.VARIABLES_CATEGORICAS),
        ]
    )


def construir_regresion_logistica(semilla: int = 42) -> Pipeline:
    """Modelo de referencia lineal.

    Args:
        semilla: Semilla del optimizador.

    Returns:
        Pipeline sin ajustar.
    """
    return Pipeline(
        [
            ("preprocesador", construir_preprocesador()),
            ("modelo", LogisticRegression(max_iter=1000, random_state=semilla)),
        ]
    )


def construir_mlp(semilla: int = 42) -> Pipeline:
    """Red neuronal con early stopping y regularización L2 (decisión 005).

    Args:
        semilla: Semilla de los pesos iniciales y de la partición de validación.

    Returns:
        Pipeline sin ajustar.
    """
    mlp = MLPClassifier(
        hidden_layer_sizes=(64, 32),
        alpha=1e-3,
        early_stopping=True,
        validation_fraction=0.1,
        n_iter_no_change=10,
        max_iter=300,
        random_state=semilla,
    )
    return Pipeline([("preprocesador", construir_preprocesador()), ("modelo", mlp)])


def construir_gradient_boosting(semilla: int = 42) -> Pipeline:
    """Árboles con gradiente boosting, candidato principal en datos tabulares.

    Args:
        semilla: Semilla de la partición de validación del early stopping.

    Returns:
        Pipeline sin ajustar. El número de árboles lo decide el early stopping.
    """
    es_categorica = [False] * len(config.VARIABLES_NUMERICAS) + [True] * len(
        config.VARIABLES_CATEGORICAS
    )
    boosting = HistGradientBoostingClassifier(
        learning_rate=0.1,
        max_iter=300,
        max_leaf_nodes=15,
        l2_regularization=1.0,
        categorical_features=es_categorica,
        early_stopping=True,
        validation_fraction=0.1,
        n_iter_no_change=10,
        random_state=semilla,
    )
    return Pipeline([("preprocesador", construir_preprocesador_arboles()), ("modelo", boosting)])
