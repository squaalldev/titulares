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
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Falta configurar GEMINI_API_KEY en el archivo .env o en los Secrets del Space.")
    st.stop()

client = genai.Client(api_key=api_key)


def build_headline_context(selected_formula_key, selected_angle, target_audience, product):
    selected_formula = headline_formulas[selected_formula_key]

    formula_description = selected_formula.get("description", "").strip()
    formula_description_short = " ".join(formula_description.split())[:420]
    formula_examples = selected_formula.get("examples", [])

    random_examples = random.sample(
        formula_examples,
        min(2, len(formula_examples))
    ) if formula_examples else []

    angle_instruction = ""
    angle_examples = []

    if selected_angle != "NINGUNO" and selected_angle in angles:
        angle_instruction = angles[selected_angle].get("instruction", "").strip()
        angle_examples = angles[selected_angle].get("examples", [])[:1]

    extra_guidance = [
        f"Escribe para {target_audience} como personas reales, no como una categoría genérica.",
        f"Piensa en qué desea ese público, qué le frustra, qué objeciones tiene y qué transformación busca en relación con {product}.",
        "No copies literalmente los ejemplos.",
        "Haz que cada titular sea claro, atractivo y creíble.",
        "No dependas de mencionar explícitamente el producto para generar interés."
    ]

    return {
        "formula_description": formula_description,
        "formula_description_short": formula_description_short,
        "formula_examples": random_examples,
        "angle_instruction": angle_instruction,
        "angle_examples": angle_examples,
        "extra_guidance": extra_guidance
    }


def generate_headlines(number_of_headlines, target_audience, product, temperature, selected_formula_key, selected_angle):
    context = build_headline_context(
        selected_formula_key=selected_formula_key,
        selected_angle=selected_angle,
        target_audience=target_audience,
        product=product
    )

    system_prompt = "\n".join([
        "Eres un copywriter de clase mundial especializado en escribir titulares, hooks y líneas de asunto que captan la atención rápidamente y despiertan una curiosidad genuina.",
        "",
        "OBJETIVO:",
        "Generar titulares atractivos, claros y creíbles para el público indicado.",
        "",
        "FORMATO OBLIGATORIO:",
        f"- Devuelve EXACTAMENTE {number_of_headlines} líneas.",
        "- Cada línea debe empezar con número y punto (ejemplo: 1. ...).",
        "- No agregues introducciones, notas, categorías ni cierre.",
        "- Una sola idea por línea.",
        "- Cada línea debe sonar como titular completo, no como viñeta o fragmento.",
        "",
        "CALIDAD:",
        "- Evita clichés y frases vacías.",
        "- Prioriza beneficio concreto + especificidad.",
        "- Mantén tono natural para el público objetivo.",
        "- No copies ejemplos literalmente.",
        "- Evita repetir estructuras entre líneas.",
        "- Enfatiza el beneficio del producto sin depender de nombrarlo de forma explícita en todos los titulares.",
        "",
        "PRINCIPIOS DE TITULACIÓN:",
        "- Abre con la promesa o ángulo principal en las primeras palabras.",
        "- Usa contraste, curiosidad o resultado específico para detener el scroll.",
        "- Evita formato tipo bullet (por ejemplo: 'Beneficio: detalle', listas fragmentadas o etiquetas).",
        "- Evita signos innecesarios, mayúsculas exageradas y relleno.",
        "- Longitud sugerida: entre 8 y 16 palabras por titular."
    ])

    headlines_instruction = (
        f"{system_prompt}\n\n"
        f"PÚBLICO: {target_audience}\n"
        f"PRODUCTO/SERVICIO (USAR COMO CONTEXTO, PRIORIZAR BENEFICIO): {product}\n"
        f"FÓRMULA: {selected_formula_key}\n"
        f"DESCRIPCIÓN CORTA DE LA FÓRMULA:\n{context['formula_description_short']}\n\n"
    )

    if selected_angle != "NINGUNO":
        headlines_instruction += (
            f"ÁNGULO: {selected_angle}\n"
            f"INSTRUCCIÓN DE ÁNGULO: {context['angle_instruction']}\n\n"
        )

    random_examples = context["formula_examples"]
    if random_examples:
        headlines_instruction += "EJEMPLOS DE REFERENCIA:\n"
        for i, example in enumerate(random_examples, 1):
            headlines_instruction += f"{i}. {example}\n"
        headlines_instruction += "\n"

    headlines_instruction += "GUÍA ADICIONAL:\n"
    for guidance in context["extra_guidance"]:
        headlines_instruction += f"- {guidance}\n"

    headlines_instruction += "\n"
    headlines_instruction += f"Genera ahora {number_of_headlines} titulares."

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=headlines_instruction + "\n\nEscribe los titulares ahora.",
        config=types.GenerateContentConfig(
            temperature=temperature,
            top_p=0.65,
            max_output_tokens=512,
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
            value=0.7,
            step=0.1
        )

        selected_formula_key = st.selectbox(
            "Selecciona una fórmula para tus titulares",
            options=list(headline_formulas.keys())
        )

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
