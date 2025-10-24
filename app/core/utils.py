"""Utility functions for the application."""
from datetime import datetime, timezone
import uuid


def generate_session_id() -> str:
    """
    Generate a unique session ID for Bedrock Agent conversations.
    
    Format: sess_YYYY_MM_DDTHH_MM_SSZ_uuid
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y_%m_%dT%H_%M_%SZ")
    unique_id = uuid.uuid4().hex[:8]
    return f"sess_{timestamp}_{unique_id}"


def format_bedrock_prompt(
    message: str,
    columns: list[str],
    dtypes: dict[str, str],
    describe_numeric: dict | None,
    describe_non_numeric: dict | None,
    info_text: str,
) -> str:
    """
    Format the prompt to send to Bedrock Agent.
    
    Args:
        message: User's message/context
        columns: List of column names
        dtypes: Dictionary of column names to data types
        describe_numeric: Numeric summary from df.describe()
        describe_non_numeric: Non-numeric summary from df.describe()
        info_text: Output from df.info()
    
    Returns:
        Formatted prompt string
    """
    prompt_parts = [
        "User message:",
        message or "(No message provided)",
        "",
        "Dataset profile:",
        f"- Columns: {', '.join(columns)}",
        f"- Data types: {dtypes}",
        "",
    ]

    if describe_numeric:
        prompt_parts.extend(
            [
                "Numeric statistics (df.describe()):",
                str(describe_numeric),
                "",
            ]
        )

    if describe_non_numeric:
        prompt_parts.extend(
            [
                "Non-numeric statistics (df.describe()):",
                str(describe_non_numeric),
                "",
            ]
        )

    prompt_parts.extend(
        [
            "DataFrame info:",
            info_text,
            "",
            "INSTRUCCIONES CRÍTICAS:",
            "Debes responder ÚNICAMENTE con un objeto JSON válido (sin markdown, sin texto adicional) que contenga sugerencias de gráficos.",
            "",
            "Formato requerido:",
            '{',
            '  "version": "1.0",',
            '  "suggested_charts": [',
            '    {',
            '      "title": "Título del gráfico",',
            '      "chart_type": "line|bar|area|pie|donut|scatter|radar|radial",',
            '      "parameters": {',
            '        "x_axis": "nombre_columna",',
            '        "y_axis": "nombre_columna" | ["col1", "col2"],  // string o array para múltiples series',
            '        "aggregations": [{"column": "nombre", "func": "sum|mean|count|min|max|std|median"}],',
            '        "group_by": ["columna1"],',
            '        "sort": {"by": "columna", "order": "asc|desc"}',
            '      },',
            '      "insight": "Explicación breve del insight",',
            '      "priority": "high|medium|low"',
            '    }',
            '  ]',
            '}',
            "",
            "TIPOS DE GRÁFICOS SOPORTADOS:",
            "- line: series temporales, tendencias",
            "- bar: comparaciones categóricas",
            "- area: tendencias acumulativas",
            "- pie/donut: distribuciones, proporciones",
            "- scatter: correlaciones entre variables numéricas",
            "- radar: comparación multidimensional (múltiples métricas)",
            "- radial: KPIs, progreso circular",
            "",
            "IMPORTANTE:",
            "- Sugiere entre 2-4 gráficos",
            "- Usa nombres de columnas exactos del dataset",
            "- Para radar: usa múltiples columnas numéricas en 'series'",
            "- Para scatter: usa dos columnas numéricas (x_axis, y_axis)",
            "- Para donut/pie: usa una columna categórica y agrupa valores numéricos",
            "- Para gráficos multi-series (comparar varias columnas): usa y_axis como array [\"col1\", \"col2\"]",
            "- Para gráficos de una sola serie: usa y_axis como string \"columna\"",
            "- CRÍTICO: 'group_by' SIEMPRE debe ser un array, incluso con un solo elemento: [\"columna\"] NO \"columna\"",
            "- CRÍTICO: 'aggregations' SIEMPRE debe ser un array de objetos: [{...}] NO {...}",
            "- CRÍTICO: usa 'mean' para promedios, NO 'avg' o 'average'",
            "- Funciones válidas: sum, mean, count, min, max, std, median",
            "- NO uses tipos de gráficos no listados (ej: histogram, box, heatmap)",
            "- Responde SOLO JSON, sin explicaciones adicionales",
        ]
    )

    return "\n".join(prompt_parts)
