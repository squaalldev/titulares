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


def generate_headlines(number_of_headlines, target_audience, product, temperature, selected_formula, selected_angle):
    # Incluir las instrucciones del sistema en el prompt principal
    system_prompt = """You are a world-class copywriter, with expertise in crafting hooks, headlines, and subject lines that immediately capture the reader's attention, prompting them to open the email or continue reading.

FORMAT RULES:
- Each headline must start with number and period
- One headline per line
- No explanations or categories
- Add a line break between each headline
- Avoid unnecessary : symbols
- Each headline must be a complete and intriguing sentence

IMPORTANT ANGLE INSTRUCTIONS:
- The selected angle MUST be applied to EVERY headline
- The angle modifies HOW the formula is expressed, not its structure
- Think of the angle as a "tone overlay" on the formula
- The formula provides the structure, the angle provides the style
- Both must work together seamlessly

FORMAT EXAMPLE:
1. Titular 1.

2. Titular 2.

3. Titular 3.

4. Titular 4.

5. Titular 5.

IMPORTANT:
- Each headline must be unique and memorable
- Avoid clichés and generalities
- Maintain an intriguing but credible tone
- Adapt speaking language from the audience
- Focus on transformative benefits
- Follow the selected angle style while maintaining formula structure"""

    # Iniciar el prompt con las instrucciones del sistema
    headlines_instruction = f"{system_prompt}\n\n"

    # Añadir instrucciones de ángulo solo si no es "NINGUNO"
    if selected_angle != "NINGUNO":
        headlines_instruction += f"""
ÁNGULO PRINCIPAL: {selected_angle}
INSTRUCCIONES DE ÁNGULO ESPECÍFICAS:
{angles[selected_angle]["instruction"]}

IMPORTANTE: El ángulo {selected_angle} debe aplicarse como una "capa de estilo" sobre la estructura de la fórmula:
1. Mantén la estructura base de la fórmula intacta
2. Aplica el tono y estilo del ángulo {selected_angle}
3. Asegura que cada elemento de la fórmula refleje el ángulo
4. El ángulo afecta al "cómo" se dice, no al "qué" se dice

EJEMPLOS EXITOSOS DEL ÁNGULO {selected_angle}:
"""
        for example in angles[selected_angle]["examples"]:
            headlines_instruction += f"- {example}\n"

    headlines_instruction += (
        f"\nTu tarea es crear {number_of_headlines} titulares irresistibles para {target_audience} "
        f"que capturen la atención instantáneamente y generen curiosidad sobre {product}. "
    )

    if selected_angle != "NINGUNO":
        headlines_instruction += (
            f"IMPORTANTE: Cada titular DEBE seguir el ángulo {selected_angle} de manera clara y consistente.\n\n"
        )

    headlines_instruction += (
        f"Evita menciones obvias de {product} y enfócate en despertar interés genuino"
    )

    if selected_angle != "NINGUNO":
        headlines_instruction += " usando el ángulo seleccionado"

    headlines_instruction += ".\n\n"

    headlines_instruction += (
        "IMPORTANTE: Estudia cuidadosamente estos ejemplos de la fórmula seleccionada. "
        "Cada ejemplo representa el estilo y estructura a seguir"
    )

    if selected_angle != "NINGUNO":
        headlines_instruction += f", adaptados al ángulo {selected_angle}"

    headlines_instruction += ":\n\n"

    # Agregar 5 ejemplos aleatorios de la fórmula
    random_examples = random.sample(
        selected_formula["examples"],
        min(5, len(selected_formula["examples"]))
    )

    headlines_instruction += "EJEMPLOS DE LA FÓRMULA A SEGUIR:\n"
    for i, example in enumerate(random_examples, 1):
        headlines_instruction += f"{i}. {example}\n"

    headlines_instruction += "\nINSTRUCCIONES ESPECÍFICAS:\n"
    headlines_instruction += "1. Mantén la misma estructura y longitud que los ejemplos anteriores\n"
    headlines_instruction += "2. Usa el mismo tono y estilo de escritura\n"
    headlines_instruction += "3. Replica los patrones de construcción de frases\n"
    headlines_instruction += "4. Conserva el nivel de especificidad y detalle\n"
    headlines_instruction += f"5. Adapta el contenido para {target_audience} manteniendo la esencia de los ejemplos\n\n"

    headlines_instruction += f"FÓRMULA A SEGUIR:\n{selected_formula['description']}\n\n"

    if selected_angle != "NINGUNO":
        headlines_instruction += f"""
RECORDATORIO FINAL:
1. Sigue la estructura de la fórmula seleccionada
2. Aplica el ángulo como una "capa de estilo"
3. Mantén la coherencia entre fórmula y ángulo
4. Asegura que cada titular refleje ambos elementos

GENERA AHORA:
Crea {number_of_headlines} titulares que sigan fielmente el estilo y estructura de los ejemplos mostrados.
"""
    else:
        headlines_instruction += f"""
GENERA AHORA:
Crea {number_of_headlines} titulares que sigan fielmente el estilo y estructura de los ejemplos mostrados.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=headlines_instruction + "\n\nGenera los titulares siguiendo exactamente el estilo de los ejemplos mostrados.",
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
                selected_formula,
                selected_angle
            )

            col2.markdown(
                f"""
                <div class="results-container">
                    <h4>Observa la magia en acción:</h4>
                    <p>{generated_headlines}</p>
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