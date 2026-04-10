from dotenv import load_dotenv
import streamlit as st
import os
from google import genai
from google.genai import types
import random
from formulas import headline_formulas
from angles import angles

# Cargar las variables de entorno
load_dotenv()

# Configurar la API de Google
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def build_headline_context(selected_formula_key, selected_angle, target_audience, product):
    selected_formula = headline_formulas[selected_formula_key]

    formula_description = selected_formula.get("description", "").strip()
    formula_examples = selected_formula.get("examples", [])

    random_examples = random.sample(
        formula_examples,
        min(5, len(formula_examples))
    ) if formula_examples else []

    angle_instruction = ""
    angle_examples = []

    if selected_angle != "NINGUNO" and selected_angle in angles:
        angle_instruction = angles[selected_angle].get("instruction", "").strip()
        angle_examples = angles[selected_angle].get("examples", [])[:3]

    extra_guidance = [
        f"Escribe para {target_audience} como personas reales, no como una categoría genérica.",
        f"Piensa en qué desea ese público, qué le frustra, qué objeciones tiene y qué transformación busca en relación con {product}.",
        "No copies literalmente los ejemplos.",
        "Haz que cada titular sea claro, atractivo y creíble.",
        "No dependas de mencionar explícitamente el producto para generar interés."
    ]

    return {
        "formula_description": formula_description,
        "formula_examples": random_examples,
        "angle_instruction": angle_instruction,
        "angle_examples": angle_examples,
        "extra_guidance": extra_guidance
    }


def generate_headlines(number_of_headlines, target_audience, product, temperature, selected_formula_key, selected_formula, selected_angle):
    context = build_headline_context(
        selected_formula_key=selected_formula_key,
        selected_angle=selected_angle,
        target_audience=target_audience,
        product=product
    )

    system_prompt = """You are a world-class copywriter specialized in writing headlines, hooks, and subject lines that capture attention fast and spark curiosity.

FORMAT RULES:
- Each headline must start with number and period
- One headline per line
- No explanations or categories
- Add a line break between each headline
- Avoid unnecessary : symbols
- Each headline must be a complete and intriguing sentence

IMPORTANT:
- Each headline must be unique and memorable
- Avoid clichés and generalities
- Maintain an intriguing but credible tone
- Adapt speaking language from the audience
- Focus on transformative benefits
"""

    headlines_instruction = f"{system_prompt}\n\n"

    if selected_angle != "NINGUNO":
        headlines_instruction += f"""
ÁNGULO PRINCIPAL: {selected_angle}
Aplica este ángulo como una capa de estilo sobre la fórmula, sin alterar su estructura base.

INSTRUCCIONES DE ÁNGULO ESPECÍFICAS:
{context["angle_instruction"]}

EJEMPLOS EXITOSOS DEL ÁNGULO {selected_angle}:
"""
        for example in context["angle_examples"]:
            headlines_instruction += f"- {example}\n"

    headlines_instruction += (
        f"\nTu tarea es crear {number_of_headlines} titulares irresistibles para {target_audience} "
        f"que capturen la atención instantáneamente y generen curiosidad sobre {product}. "
    )

    headlines_instruction += (
        f"Antes de escribir, determina quién es realmente {target_audience}: "
        f"qué desea, qué le frustra, qué objeciones tiene, qué transformación busca y cómo suele pensar o hablar sobre este problema. "
        f"Usa esa comprensión para que cada titular conecte con su situación de forma natural y relevante.\n\n"
    )

    if selected_angle != "NINGUNO":
        headlines_instruction += (
            f"IMPORTANTE: Cada titular DEBE seguir el ángulo {selected_angle} de manera clara y consistente.\n\n"
        )

    headlines_instruction += (
        f"No dependas de mencionar explícitamente {product} para generar interés genuino"
    )

    if selected_angle != "NINGUNO":
        headlines_instruction += " usando el ángulo seleccionado"

    headlines_instruction += ".\n\n"

    headlines_instruction += "GUÍA ADICIONAL:\n"
    for rule in context["extra_guidance"]:
        headlines_instruction += f"- {rule}\n"
    headlines_instruction += "\n"

    headlines_instruction += (
        "IMPORTANTE: Estudia cuidadosamente estos ejemplos de la fórmula seleccionada. "
        "Cada ejemplo representa el estilo y estructura a seguir"
    )

    if selected_angle != "NINGUNO":
        headlines_instruction += f", adaptados al ángulo {selected_angle}"

    headlines_instruction += ":\n\n"

    random_examples = context["formula_examples"]

    headlines_instruction += "EJEMPLOS DE LA FÓRMULA A SEGUIR:\n"
    for i, example in enumerate(random_examples, 1):
        headlines_instruction += f"{i}. {example}\n"

    headlines_instruction += "\nINSTRUCCIONES ESPECÍFICAS:\n"
    headlines_instruction += "1. Mantén una estructura y longitud similares a las de los ejemplos anteriores\n"
    headlines_instruction += "2. Conserva el nivel de especificidad y detalle\n"
    headlines_instruction += "3. Inspírate en los patrones de construcción sin copiarlos literalmente\n"
    headlines_instruction += "4. Haz que cada titular suene natural para el público objetivo\n"
    headlines_instruction += "5. Asegúrate de que cada titular sea claro, atractivo y creíble\n\n"

    headlines_instruction += f"FÓRMULA A SEGUIR:\n{context['formula_description']}\n\n"

    if selected_angle != "NINGUNO":
        headlines_instruction += f"""
RECORDATORIO FINAL:
1. Sigue la estructura de la fórmula seleccionada
2. Aplica el ángulo como una capa de estilo
3. Mantén la coherencia entre fórmula y ángulo
4. Asegura que cada titular refleje ambos elementos

GENERA AHORA:
Crea {number_of_headlines} titulares que sigan fielmente la estructura de la fórmula y mantengan la esencia de los ejemplos mostrados.
"""
    else:
        headlines_instruction += f"""
GENERA AHORA:
Crea {number_of_headlines} titulares que sigan fielmente la estructura de la fórmula y mantengan la esencia de los ejemplos mostrados.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=headlines_instruction + "\n\nGenera titulares originales que respeten la estructura de la fórmula seleccionada, apliquen el ángulo elegido y mantengan la esencia de los ejemplos sin copiarlos literalmente.",
        config=types.GenerateContentConfig(
            temperature=temperature,
            top_p=0.65,
            max_output_tokens=8196,
        ),
    )

    return response.text


# Configurar la interfaz de usuario con Streamlit
st.set_page_config(page_title="Enchanted Hooks", layout="wide")

# Leer el contenido del archivo manual.md
with open("manual.md", "r", encoding="utf-8") as file:
    manual_content = file.read()

# Mostrar el contenido del manual en el sidebar
st.sidebar.markdown(manual_content)

# Load CSS from file
with open("styles/main.css", "r", encoding="utf-8") as f:
    css = f.read()

# Apply the CSS
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Centrar el título y el subtítulo
st.markdown("<h1 style='text-align: center;'>Enchanted Hooks</h1>", unsafe_allow_html=True)
st.markdown(
    "<h4 style='text-align: center;'>Imagina poder conjurar títulos que no solo informan, sino que encantan. Esta app es tu varita mágica en el mundo del copywriting, transformando cada concepto en un titular cautivador que deja a todos deseando más.</h4>",
    unsafe_allow_html=True
)

# Crear columnas
col1, col2 = st.columns([1, 2])

# Columnas de entrada
with col1:
    target_audience = st.text_input(
        "¿Quién es tu público objetivo?",
        placeholder="Ejemplo: Estudiantes Universitarios"
    )
    product = st.text_input(
        "¿Qué producto tienes en mente?",
        placeholder="Ejemplo: Curso de Inglés"
    )
    number_of_headlines = st.selectbox(
        "Número de Titulares",
        options=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        index=4
    )

    # Crear un único acordeón para fórmula, creatividad y ángulo
    with st.expander("Personaliza tus titulares"):
        temperature = st.slider(
            "Creatividad",
            min_value=0.0,
            max_value=2.0,
            value=1.0,
            step=0.1
        )

        selected_formula_key = st.selectbox(
            "Selecciona una fórmula para tus titulares",
            options=list(headline_formulas.keys())
        )

        # Make sure "NINGUNO" appears first, then the rest alphabetically
        angle_keys = ["NINGUNO"] + sorted([key for key in angles.keys() if key != "NINGUNO"])
        selected_angle = st.selectbox(
            "Selecciona el ángulo para tus titulares",
            options=angle_keys
        )

    selected_formula = headline_formulas[selected_formula_key]

    # Botón de enviar
    submit = st.button("Generar Titulares")

# Mostrar los titulares generados
if submit:
    has_product = product.strip() != ""
    has_audience = target_audience.strip() != ""
    valid_inputs = has_product and has_audience

    if valid_inputs and selected_formula:
        try:
            generated_headlines = generate_headlines(
                number_of_headlines,
                target_audience,
                product,
                temperature,
                selected_formula_key,
                selected_formula,
                selected_angle
            )

            formatted_headlines = generated_headlines.replace("\n", "<br>")

            col2.markdown(
                f"""
                <div class="results-container">
                    <h4>Observa la magia en acción:</h4>
                    <div>{formatted_headlines}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        except Exception as e:
            col2.error(f"Error: {str(e)}")
    else:
        if not selected_formula:
            col2.error("Por favor, selecciona una fórmula.")
        else:
            col2.error("Por favor, proporciona el público objetivo y el producto.")
