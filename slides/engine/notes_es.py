#!/usr/bin/env python3
"""Spanish speaker notes for the full four-hour deck, keyed by slide id.

parts/*.html stays the English source of truth. build.py pairs each note with
its entry here and emits <div data-lang="en"> / <div data-lang="es"> inside the
same <aside class="notes">; deck.js switches between them with L or the EN/ES
button, and falls back to English for any slide not yet translated.

Write the Spanish the way the English is written: newlines separate paragraphs,
and builds are marked "Paso 2: ..." so notes_build.cues() turns them into the
same highlighted blocks. Keep the timecode in <b> first.

Translation conventions
-----------------------
Field vocabulary that Spanish-speaking ML people say in English is kept in
English (residual stream, logit lens, probe, patching, embedding, softmax,
token, head, feature, SAE, prompt). Everything explanatory is Spanish. Numbers,
citations, file paths and TODOs are preserved exactly.
"""

ES = {

# ========================================================== PART 1 · Miguel

"p1-title": """
    <b>0:00 (1 min) · Miguel.</b> Bienvenida. Presenta a los tres en una frase cada uno: Miguel (los primeros 30 min, luego tiene que irse a otra sesión), Salvador (métodos, 0:30–2:10), Víctor (auditoría de jueces LLM, 2:10–3:00). Menciona al asistente que ayudará con Colab. Pide a la gente que abra el portátil ya: las siguientes slides ponen en marcha NB0.
""",

"p1-goals": """
    <b>0:01 (1 min).</b> Tres objetivos, pásalos uno a uno. Insiste en la segunda mitad del objetivo 1: la mitad de hoy trata de lo que estos métodos <i>no</i> muestran. Presenta el ritual: antes de cada experimento se escribe una predicción; equivocarse es justamente el punto. Mantén el ritmo ágil.
""",

"p1-agenda": """
    <b>0:02 (1 min).</b> El arco es una sola historia: primero <i>observamos</i> (correlación), luego <i>intervenimos</i> (causalidad), después buscamos las <i>unidades</i> (features), luego los <i>circuitos</i>, y al final lo aplicamos a un problema real (auditar un juez LLM). Los colores del pie indican quién presenta. Yo me voy a las 0:30 a otra sesión; Salvador toma el relevo a mitad de la historia. Descanso a la 1:00: ahí se cambia el runtime a T4.
""",

"p1-nb0": """
    <b>0:03 (1 min, y se deja corriendo).</b> TODO antes del evento: sustituir <code>bit.ly/micai-mi-nb0</code> por el enlace corto real y probarlo. Recorre los 4 pasos despacio. Token: huggingface.co → Settings → Access tokens → token de tipo "Read"; en Colab, el icono de la llave en la barra lateral izquierda → añadir el secreto <code>HF_TOKEN</code> y habilitar el acceso desde el notebook. Licencia: abrir <code>huggingface.co/google/gemma-3-1b-it</code> y pulsar "Agree" (necesario para NB3). Opcional, en el mismo clic: <code>google/gemma-2-2b</code> (la vía opcional de NB4) y <code>google/gemma-3-4b-it</code> (solo para la vía en vivo de NB5; NB5 normalmente usa una caché) (puede tardar un minuto en concederse, y por eso lo hacemos ahora: necesitamos Gemma a la 1:10). NB0 solo comprueba el entorno. El asistente circula por la sala; sigue con el gancho mientras corre.
""",

"p1-hook": """
    <b>0:04–0:06:30 (2 min 30 s).</b> Paso 0: así es como evaluamos normalmente un modelo: entra un prompt, sale una respuesta. Benchmarks, red-teaming, evals: todo es conductual. Paso 1 (→): la caja no es magia, es un cómputo que podemos registrar. Paso 2 (→): algunas direcciones internas se comportan como <i>conceptos</i>: una "feature" que se activa cuando el texto habla, por ejemplo, de monumentos de París. (La etiqueta de la figura es ilustrativa.)<br>
    <b>Demo en vivo (sin código, ~90 s):</b> abre <a href="https://www.neuronpedia.org">neuronpedia.org</a>, elige un modelo Gemma, busca una feature conceptual (p. ej. "Eiffel Tower" / "Paris", o una del tipo "Golden Gate Bridge") y usa el panel de <i>steering</i>: mismo prompt, con steering apagado y encendido. Enseña que subir una sola feature interna cambia lo que el modelo escribe. Mensaje: acabamos de cambiar el comportamiento editando una variable interna, y eso solo funciona si la variable significa algo.<br>
    <b>Plan B si falla el Wi-Fi:</b> describe el "Golden Gate Claude" de Anthropic (mayo de 2024): fijar una sola feature de SAE hizo que Claude sacara el puente Golden Gate en cada respuesta. Ten una grabación de pantalla del steering en Neuronpedia guardada en el escritorio del portátil (TODO: grabarla).
""",

"p1-poll": """
    <b>0:06:30–0:07:15 (45 s).</b> Que levanten la mano por A, B, C y D; cuenta por encima y di el reparto en voz alta. NO reveles la respuesta. (Para ti: el logit lens de NB1 muestra que "&nbsp;Paris" aparece solo hacia los bloques 8–9 de 12, lo que apoya C como <i>observación</i>; el Bloque 2 comprueba si esas capas son causales. La D es una trampa que vale la pena discutir luego: "estadística" y "una asociación almacenada y localizable" no se excluyen.)
""",

"p1-why-now": """
    <b>0:07:15–0:08 (45 s).</b> Sin hype: tres hechos, una frase cada uno. (1) Ya es lo bastante mainstream como para estar en la lista de 2026 del MIT Technology Review. (2) Hace dos años este tutorial habría necesitado herramientas privadas; hoy corre en Colab gratuito, con SAEs y transcoders abiertos para Gemma 3 (Gemma Scope 2) y circuit tracing abierto (circuit-tracer + Neuronpedia). (3) La propia revisión del campo (Sharkey et al., 2025) enumera decenas de problemas abiertos, y hoy nos cruzaremos con varios (en el Bloque 3 los SAEs no le ganan a un probe sencillo). Transición: empecemos simplemente por <i>mirar</i>.
""",

"p1-block1": """
    <b>0:08 (unos segundos).</b> El Bloque 1 abre con un primer de 4 minutos (tokens, direcciones, logits, el mapa y tres verbos), luego un modelo mental (el residual stream) y una herramienta (el logit lens). Para las 0:30 todo el mundo habrá decodificado por su cuenta las capas intermedias de GPT-2.
""",

"p1-pr-tokens": """
    <b>0:08–0:08:45 (45 s).</b> En palabras llanas: un modelo nunca ve letras, solo números.<br>
    Paso 1: el tokenizador corta el texto en piezas de una lista fija de 50.257. Las palabras comunes son un solo token; las raras se parten: "Eiffel" son tres tokens (·E, iff, el). El punto significa "empieza con espacio". Cada pieza tiene un número de id.<br>
    Paso 2: el id no es más que un número de fila en una tabla grande, la matriz de embeddings (50.257 filas × 768 columnas). Los tokens comunes tienen ids pequeños, así que están todos cerca de arriba.<br>
    Paso 3: esa fila es el vector del token: 768 números. Mostramos los 8 primeros, valores reales de GPT-2; dibujamos los vectores de pie, como columnas. GPT-2 además suma un vector de posición (otros 768 números) para que el modelo sepa el orden de las palabras. De aquí en adelante, "un token" dentro del modelo significa "una columna de 768 números".<br>
    Si preguntan: TransformerLens también antepone un token &lt;|endoftext|&gt; en la posición 0; lo omitimos por espacio. Valores de <code>scratch/primer/primer_extra.py</code> (pesos crudos de GPT-2; la carga por defecto de TransformerLens los centra, lo que cambia el tercer decimal).
""",

"p1-pr-direction": """
    <b>0:08:45–0:09:45 (1 min).</b> Todo lo que hay en esta slide es <i>ilustrativo</i>: 2 de 768 dimensiones, números inventados, y "lo francés" es una etiqueta didáctica, no una feature medida.<br>
    Paso 0: una activación es una lista de números; geométricamente es una flecha. Paso 1: elige una dirección d (una flecha de longitud 1). Paso 2: el producto punto x · d es la longitud de la sombra que x proyecta sobre d: "cuánto de d hay en x". Esta es la única operación que hay que recordar. Panel derecho: el logit lens hace el producto punto de x con el vector de unembedding de cada token; un probe lo hace con un vector de pesos aprendido (más un sesgo); la activación de una feature de SAE es x por su dirección <i>encoder</i>, más un sesgo, y luego una (Jump)ReLU. El steering es lo contrario: <i>escribe</i> a lo largo de una dirección (suma α·d a x); Salvador lo enseña en el Bloque 3, donde d es la dirección <i>decoder</i> de una feature.<br>
    Paso 3: un prompt distinto da una flecha distinta; la sombra se encoge y aquí se vuelve ligeramente negativa (−0,4).<br>
    Matiz honesto para más adelante: que una dirección se lea bien no prueba que el modelo la <i>use</i> (Bloques 2 y 3).
""",

"p1-pr-logits": """
    <b>0:09:45–0:11 (1 min 15 s).</b> Números reales, GPT-2 small, prompt "The Eiffel Tower is in the French city of".<br>
    Paso 0: en la última posición el modelo tiene un vector final x (después del último LayerNorm). Compara x con cada palabra de su vocabulario mediante un producto punto: una puntuación por token, llamada <b>logit</b>. (En GPT-2 los vectores de unembedding son otra vez las filas de embedding: pesos atados.)<br>
    Paso 1: los logits son números reales cualesquiera; cerca de la mitad de los 50.257 son negativos ("·banana": −1,34). Arriba: ·Paris 18,06; ·Nice 17,68; ·Lyon 17,29; ·Marse (primer trozo de "Marseille") 16,80; ·L 15,91; ·Saint 15,80; ·London está solo en el puesto 176.<br>
    Paso 2: softmax = exponenciar cada logit y dividir por el total. Ahora son probabilidades: Paris 0,207; Nice 0,141; Lyon 0,096… y los otros 50.249 tokens juntos todavía suman 0,45. Exponenciar implica que solo importan las <i>diferencias</i> entre logits: Hugging Face reporta estos mismos logits desplazados en −116,4 (TransformerLens los centra) y las probabilidades son idénticas.<br>
    Paso 3: así comparamos dos candidatos directamente: la <b>diferencia de logits</b>, aquí 0,77 = ln(0,207/0,096). Es una función lineal de x: si sumas un vector v a x, la diferencia se mueve exactamente v · (u<sub>Paris</sub> − u<sub>Lyon</sub>). Una probabilidad depende de los 50.257 logits a la vez, así que no lo es. Por eso la métrica de patching de Salvador en el Bloque 2 es una diferencia de logits (Mary contra John). Letra pequeña si preguntan: x se toma después del LayerNorm final, cuyo reescalado es el único paso no lineal entre el residual stream y los logits.
""",

"p1-pr-map": """
    <b>0:11–0:11:30 (30 s).</b> Este es el mapa de toda la jornada; la siguiente slide hace zoom. Lee el vocabulario, una palabra por clic.<br>
    Paso 0: embed abajo, unembed arriba, y el <b>residual stream</b> en medio: un vector por posición del que cada parte lee y al que cada parte suma. Paso 1: la <b>atención</b> es la única parte que mueve información <i>entre</i> posiciones; cada capa tiene 12 <b>heads</b> trabajando en paralelo (el Bloque 2 encuentra heads concretos como L9H9 = capa 9, head 9). Paso 2: el <b>MLP</b> trabaja en cada posición por separado. Paso 3: atención + MLP = una <b>capa</b>; GPT-2 small apila 12 (numeradas de 0 a 11). Paso 4: una <b>activación</b> es el vector de números en una capa y una posición, p. ej. el stream después de la capa 6 en "·of". (Las salidas de atención y MLP también son activaciones; hoy normalmente nos referimos al stream.) Todos los métodos de hoy toman una activación y le hacen algo.
""",

"p1-pr-verbs": """
    <b>0:11:30–0:12 (30 s).</b> Toda la sesión en tres verbos. <b>Leer</b>: decodificar qué hay en una activación (mi logit lens dentro de un minuto; los probes de Salvador; los probes de Víctor sobre un juez LLM). Paso 1, <b>Editar</b>: cambiar una activación y mirar la salida; así es como probamos causa (Salvador, Bloques 2–3). Paso 2, <b>Descomponer</b>: partir una activación en una suma de direcciones interpretables (SAEs) y trazar cómo se conectan (grafos de atribución, Bloque 4). Los colores de los puntos indican el presentador. El Bloque 1 es todo lectura: tenlo presente para la slide de límites al final de mi parte.
""",

"p1-residual-bus": """
    <b>0:12–0:14:30 (2 min 30 s).</b> El primer ya nombró las piezas; aquí se ven funcionando. Una línea vertical por posición de token = el residual stream en esa posición (en GPT-2 small, un vector de 768 dimensiones). Fíjate en la tokenización real: "Eiffel" son tres tokens.<br>
    Paso 1: los embeddings se escriben sobre los streams. Paso 2: la atención es el <i>único</i> componente que mueve información <i>entre</i> posiciones; aquí "of" lee de "Tower", "French" y "city" y <i>suma</i> el resultado a su propio stream. Paso 3: el MLP trabaja en una posición a la vez; lee el stream y le suma un vector de vuelta (los MLP parecen ser donde viven muchas asociaciones almacenadas). Paso 4: esto se repite durante 12 capas; al final, el unembedding lee el stream final en la última posición y da las probabilidades del siguiente token.<br>
    Frase clave: <b>el residual stream es una suma acumulada: nada lo sobrescribe, cada componente le suma.</b> Eso es lo que hace posible el logit lens en 3 minutos. El panel de la derecha = el stream en "of" creciendo como suma (los tamaños de los segmentos son esquemáticos).<br>
    Nota de precisión por si preguntan: en el recuerdo factual real (Meng et al. 2022; Geva et al. 2023) los MLP de las capas intermedias-tempranas enriquecen el token <i>sujeto</i> ("Tower") y la atención copia después el atributo al último token; la figura comprime esa historia en un paso de atención y uno de MLP.
""",

"p1-explainer": """
    <b>0:14:30–0:15:30 (1 min, límite estricto).</b> El primer ya mostró embeddings y probabilidades, así que enseña solo (2), la vista de atención; sáltate la demo entera si vas retrasado. Abre <a href="https://poloclub.github.io/transformer-explainer/">https://poloclub.github.io/transformer-explainer/</a>. Escribe "The Eiffel Tower is in the French city of". Muestra (1) el embedding y la pila de bloques, y relaciónalo con el bus que acabamos de ver; (2) expande un bloque de atención y pasa el cursor por el último token para ver sus pesos de atención; (3) las barras de probabilidad del siguiente token y el deslizador de temperatura. No expliques softmax ni QKV en detalle: el bloque de Salvador no lo necesita. Si falla el Wi-Fi: sáltalo, di "está en la lista de recursos" y ve directo al logit lens.
""",

"p1-logit-lens": """
    <b>0:15:30–0:17:30 (2 min).</b> El método en una frase: toma el residual stream en la última posición después del bloque ℓ, aplícale el LayerNorm final y el unembedding del propio modelo, y léelo como si el modelo se hubiera detenido ahí (nostalgebraist, 2020). Funciona porque el stream es una suma acumulada escrita (aproximadamente) en la misma base que lee la salida.<br>
    Estos son <b>números reales</b>, GPT-2 small, prompt "The Eiffel Tower is in the French city of", calculados con TransformerLens (scratch/p1/logit_lens.py). Paso 1: las capas tempranas predicen un genérico " the"; P(Paris)≈0. Paso 2: los bloques 4–7 derivan hacia tokens de lugar (" La", " Man", " Rome"). Paso 3: el bloque 8 salta a "&nbsp;Paris" (0,75), hace pico en el bloque 9 (0,96) y luego los últimos bloques la <i>bajan</i> a 0,21 en la salida, aunque sigue siendo top-1 (las capas finales reparten masa hacia otras ciudades — " Nice", " Lyon" —, un efecto conocido parecido a la calibración). Paso 4: resalta. Señala la columna de rango: del puesto ~24.000 al 1.<br>
    No digas "el bloque 8 almacena el dato": eso es justo la advertencia de la siguiente slide y el bloque de Salvador.
""",

"p1-predict": """
    <b>0:17:30–0:18 (30 s).</b> Da 20 segundos de silencio; insiste en que escriban un número (o "nunca"). No des pistas.<br>
    Solo para ti (números reales de GPT-2 small): sin "French", la respuesta final de GPT-2 small es " London" (P≈0,08); "&nbsp;Paris" sube a <b>rango 2</b> en el bloque 9 (P≈0,20) y nunca llega a ser top-1. La secuencia de top-1 es " the" (bloques 0–4) → " England" → " Ing" → " Chicago" (bloque 8) → " London" (9–11). Un modelo pequeño, un dato frágil. Esto prepara la respuesta de la encuesta: la información emerge en capas concretas intermedias-tardías <i>y</i> compite con otras ciudades.
""",

"p1-nb1": """
    <b>0:18–0:28 (10 min).</b> Recorre la sala con el asistente. Orden de NB1: §1–2 correr el lens sobre el prompt de la Torre Eiffel y sobre el prompt sin "French" (≈3 min); §3 <b>Tu turno</b>: completar las 3 líneas TODO de <code>logit_lens_probs</code> (apilar los residuales en la última posición, <code>model.ln_final</code> con una dimensión de posición ficticia, <code>model.unembed</code> + softmax); una celda lo comprueba contra la librería, y hay un respaldo que corre si se lo saltan (≈5 min); luego sus propios prompts. §4 <b>Ampliación</b> (≈3 min, opcional): puntuación de inducción sobre tokens aleatorios repetidos; los principales induction heads de GPT-2 small son L5H5, L6H9 y L7H10 (≈0,9), luego L5H1 y L7H2. Los induction heads vuelven en el Bloque 2 (IOI). Buenos prompts que sugerir: "The capital of Japan is" (dato), "English: cat — French:" (traducción), "2 + 2 =" (aritmética; los modelos pequeños suelen fallar, y está bien: lo interesante es <i>dónde</i> falla). A las 0:26 avisa de que quedan 2 minutos. A las 0:27 pregunta a 2 o 3 personas: "¿Cuándo llegó Paris a ser top-1 sin 'French'?" y revela: nunca; gana London, y Paris llega al rango 2 en el bloque 9. Luego pregunta: "¿Entonces el bloque 9 <i>causó</i> la respuesta?" → siguiente slide.
""",

"p1-limits": """
    <b>0:28–0:29 (1 min).</b> Todo el Bloque 1 ha sido <i>leer</i>. Un termómetro que marca que sube la temperatura no te dice qué calienta la habitación. Dos matices técnicos: (1) los pesos de atención ≠ importancia; un head puede mirar un token y no escribir nada útil; (2) el logit lens está sesgado hacia las capas tardías porque las representaciones tempranas no están en la base del unembedding; el tuned lens (Belrose et al.) lo corrige con un mapa afín aprendido por capa. Para afirmar causa hay que <i>intervenir</i>: cambiar la activación y mirar la salida. Ese es el bloque de Salvador.
""",

"p1-handoff": """
    <b>0:29–0:30.</b> Lee la pregunta en voz alta y déjala en pantalla. Agradece a la sala; Miguel cede el turno a Salvador a las 0:30 en punto y se va a su otra sesión. Salvador arranca el Bloque 2 con esta misma pregunta.
""",

# ======================================================= PART 2 · Salvador

"p2-sec2": """
    <b>0:30.</b> Toma el relevo de Miguel. Repite su pregunta en voz alta: "¿Esa capa lo causa?". Respuesta corta: mirando no podemos saberlo. Hay que intervenir. Los próximos 100 minutos son una sola historia en tres actos: causa, unidades, circuitos.
""",

"p2-arc": """
    <b>0:31.</b> Una slide de mapa. El patching nos dice <i>dónde</i>. Eso deja la pregunta de <i>qué</i>: las unidades. Las unidades dejan la pregunta de <i>cómo se combinan</i>: los circuitos. Cada bloque tiene una predicción y un notebook. No te pases de un minuto.
""",

"p2-corr": """
    <b>0:32.</b> Responde directamente a la pregunta de Miguel. Un probe o el logit lens muestran que la información es decodificable; eso es correlación. Ejemplo que dar: un probe puede decodificar la posición de una palabra desde casi cualquier capa, y eso no significa que el modelo calcule ahí el siguiente token a partir de ella. Intervención: sobrescribir una activación, volver a correr y medir. Pregunta a la sala: "¿Y <i>con qué</i> la sobrescribirían?". Enlaza con la siguiente slide: con la activación de un prompt distinto.
""",

"p2-transplant": """
    <b>0:33–0:37.</b> Paso 0: dos prompts. Limpio: "When Mary and John went to the store, John gave a drink to" → Mary. Corrupto: cambia el nombre repetido ("…, Mary gave a drink to"), así que la respuesta se invierte a John. Solo difiere un token (S2); misma longitud, mismas posiciones. Son los 8 prompts de NB2; la slide muestra el primero.<br>Paso 1: corre los dos hacia delante y cachea todas las activaciones (capas × posiciones).<br>Paso 2: copia UNA activación, el residual stream que entra a la capa 9 en la última posición, del run limpio al corrupto.<br>Paso 3: deja que el run corrupto continúe. Su respuesta vuelve hacia Mary: un 0,99 del camino (calculado, GPT-2 small, media sobre los 8 prompts de NB2).<br>Paso 4: repítelo para cada par (capa, posición): 12 capas × 15 posiciones = 180 runs en NB2 (la columna BOS siempre es 0, así que la slide la oculta). Un heatmap: la rejilla real de NB2; termina en 0,98 para la capa 11. Las rejillas azul-gris son activaciones esquemáticas; el turquesa está reservado para la puntuación restaurada. Pregunta: "¿Qué celdas esperan que se enciendan?". No respondas todavía.
""",

"p2-metric": """
    <b>0:37–0:39.</b> Por qué una diferencia de logits y no accuracy: es continua y cancela todo lo que los dos nombres comparten. Normalizar da 0 = se comporta como el run corrupto, 1 = restaurado del todo al limpio. Son posibles valores por encima de 1 o por debajo de 0; veremos algunos. Estos son los números reales del lote de 8 prompts de NB2, así que coincidirán con el notebook.
""",

"p2-ioi": """
    <b>0:39–0:41.</b> Un adelanto, no una clase. Tres grupos de heads, del más temprano al más tardío. (1) Los duplicate-token heads en el segundo "John" atienden de vuelta al primer John y detectan la repetición. Los induction heads hacen un trabajo emparentado (atienden al token que sigue al primer John); el arco los omite por claridad, pero te cruzarás con dos de ellos (L5H5, L6H9) en el ranking. (2) Los S-inhibition heads (L7H3, L7H9, L8H6, L8H10) llevan el mensaje "John es el duplicado, no digas John" hasta la posición final. (3) Los name mover heads (L9H9, L9H6, L10H0), en la posición final, atienden al nombre que queda, Mary, y lo copian a la salida. Intentarán encontrar los name movers ustedes mismos en el notebook.
""",

"p2-predict-resid": """
    <b>0:41.</b> Un minuto, en silencio. Insiste en que lo escriban. Una equivocación típica: "la posición de Mary, en todas las capas". Lo interesante es la banda que se desplaza. Luego abre NB2.
""",

"p2-nb2": """
    <b>0:41–0:55.</b> En NB2 los prompts y la métrica de diferencia de logits vienen dados; el único ejercicio de código es el hook de patching sobre el residual (hay un hook de referencia que toma el relevo si se lo saltan). El paso 5 es el fallo productivo de NB2: graficar, para cada head, su atención desde el token final hacia el nombre IO contra su efecto causal. Casi todo el mundo espera una relación positiva fuerte; sobre los 144 heads sale r ≈ −0,16. Recorre la sala. A las 0:48 comprueba que la mayoría tiene ya el heatmap. Si alguien termina pronto: ejercicio de ampliación, hacer patching por separado de las salidas de atención y las de MLP. A las 0:54 avisa de que queda un minuto. No enseñes la siguiente slide hasta las 0:55.
""",

"p2-heatmap": """
    <b>0:55–0:57.</b> Números reales, la misma rejilla que produce NB2: GPT-2 small, residual stream entrando a cada capa, media sobre los 8 prompts del notebook (script scratch/p2/ioi_patching_nb2.py). Lo primero: toda posición anterior a S2 es exactamente 0, porque esos tokens son idénticos en el prompt limpio y en el corrupto y la atención es causal. Paso 1: hasta la capa 7 todo el efecto está en S2, el único token que difiere (≈ 1,0; 0,95 en L7). Paso 2: el traspaso ocurre en las capas 7–8: S2 cae a 0,75 en L8 y a 0,05 en L9, mientras el token final sube de 0,03 (L7) a 0,39 (L8) y a 0,99 (L9). Paso 3: de la capa 9 en adelante, todo está en el token final. O sea: los heads de atención de las capas 7–8 mueven la información de S2 al final, y ahí es donde viven los S-inhibition heads. Hay un rastro tenue (≈ 0,04) en " gave", real pero pequeño. Compáralo con tu predicción.
""",

"p2-heads": """
    <b>0:57–0:59.</b> Los mismos números que NB2. Ningún head suelto restaura más de la mitad: el circuito está distribuido. La cabeza del ranking encaja con las clases de Wang et al.: L5H5 (0,45) y L6H9 son induction heads que alimentan la señal de "John está repetido"; L8H6, L8H10, L7H9 y L7H3 son S-inhibition heads, lo que cuadra con el traspaso en las capas 7–8 de la slide anterior; L9H9 y L10H0 son name movers; L3H0 es un duplicate-token head. Pregunta: ¿por qué L9H6, un name mover publicado, se queda en 0,03? El patching de un head aislado mide lo que ese head aporta mientras todos los demás siguen corruptos; los heads redundantes y de respaldo parecen débiles por sí solos. Un número pequeño no prueba que un head sea irrelevante. Los heads que empujan en contra: L10H7 (−0,51) y L11H10 (−0,22) son negative name movers: restaurarlos empuja contra la respuesta correcta. Haz aquí el debrief de NB2 §5: L10H7 es además uno de los heads que más atiende a Mary (≈ 0,78) y aun así su efecto es negativo; sobre los 144 heads, la atención al IO frente al efecto causal da r ≈ −0,16. La atención no es explicación; la intervención sí.
""",

"p2-where": """
    <b>0:59–1:00.</b> Además: el patching depende de la corrupción que elijas; otro contrafactual puede encender celdas distintas. Puente al Bloque 3: para decir <i>qué</i>, hay que descomponer el vector en unidades. Luego anuncia el descanso.
""",

"p2-break": """
    <b>1:00.</b> Lee los tres pasos en voz alta. NB3 usa Gemma 3 1B IT; las descargas tardan varios minutos con el Wi-Fi de un congreso, y por eso se empiezan ahora. Menciona la línea opcional solo de pasada: la vía por defecto del Bloque 4 corre en Neuronpedia desde el navegador, así que nadie necesita la descarga de 18 GB de Gemma 2 2B de NB4. El runtime propio de NB4 usa versiones de librerías más antiguas y rompería el stack de NB3 en el mismo runtime, y el Colab gratuito da una T4 por cuenta, que NB3 necesita de 1:10 a 1:40. Así que solo deberían arrancarlo quienes vayan a correr NB3 en el respaldo por CPU, o tengan una segunda cuenta. Volvemos a la 1:10 en punto.
""",

"p2-sec3": """
    <b>1:10.</b> Comprueba que NB3 está cargando en la mayoría de las máquinas (que levanten la mano). Luego: "Ya sabemos dónde. La idea obvia es mirar neuronas individuales. Veamos por qué eso falla."
""",

"p2-poly": """
    <b>1:11–1:13.</b> Polisemanticidad: una neurona, con sus activaciones más altas en cuatro contextos sin relación entre sí. Si las neuronas fueran las unidades, podríamos etiquetarlas. No son unidades limpias. Pregunta: "¿Por qué el entrenamiento haría esto?". La respuesta está en la siguiente slide: hay más cosas que representar que neuronas.
""",

"p2-super": """
    <b>1:13–1:16.</b> Modelo de juguete (Elhage et al. 2022): 5 features, un espacio oculto de 2 dimensiones, y luego reconstruir. Paso 1: empaqueta 5 direcciones en 2D. Activa la feature 1 y lee todas las direcciones: las demás recogen parte de ella. Esa fuga es la interferencia. Paso 2: si las features son densas (suelen estar activas a la vez), las fugas se acumulan en cada entrada, así que el modelo se queda con 2 features ortogonales y descarta 3. Paso 3: a medida que las features se vuelven dispersas, rara vez coinciden; la ReLU corta casi toda la fuga, así que el modelo empaqueta las 5 como un pentágono. Paso 4: más features que dimensiones, pagado con interferencia. Una matización honesta: la superposición vuelve polisemánticas a las <i>neuronas</i> individuales solo cuando la base de neuronas es privilegiada, es decir, cuando hay una no linealidad que actúa neurona a neurona, como en un MLP. Esta capa oculta de juguete es lineal, así que aquí lo que se ve son features compartiendo direcciones, no neuronas como tales.
""",

"p2-sae": """
    <b>1:16–1:19.</b> Paso 0: un vector residual, denso, con todas las entradas un poco activas. Paso 1: el encoder lo lleva a un vector mucho más ancho donde solo unos pocos latentes son distintos de cero (penalización de dispersión). Gemma Scope 2 usa JumpReLU: una ReLU con un umbral aprendido, así que un latente es exactamente 0 salvo que su preactivación supere el umbral. En la configuración de NB3 verán 'jumprelu'. Cada latente puede recibir una etiqueta humana a partir de los textos que lo activan. Las etiquetas de aquí son ilustrativas. Paso 2: el decoder vuelve a sumar las direcciones de esos latentes (W_dec·f + b_dec, es decir, Σ latente × dirección más un sesgo): una reconstrucción. Paso 3: la reconstrucción es imperfecta. Lo que sobra, el término de error, es cómputo real que el diccionario no explica. Número concreto de NB3: insertar la reconstrucción del SAE de vuelta en Gemma 3 1B IT (capa 17) sube la pérdida del siguiente token en +0,37 nats. El Bloque 4 dibujará ese sobrante como nodos de error.
""",

"p2-gscope": """
    <b>1:19–1:21.</b> Gemma Scope 2: pesos abiertos de SAEs y transcoders para toda la familia Gemma 3; transcoders entre capas para los modelos de 270M y 1B (usamos esas ideas en el Bloque 4). En NB3 todo el mundo usa Gemma 3 1B IT, capa 17 de 26, y el latente #3440 "Mexico and Argentina locations" (Neuronpedia: gemma-3-1b-it / 17-gemmascope-2-res-16k). Fórmula de steering del notebook: x ← x + α · r̄ · d, con d la dirección decoder unitaria del latente y r̄ la norma residual media del prompt en esa capa (una sola constante, no la norma de cada token), de modo que α es una fracción de un vector residual típico. (El ejemplo de steering del primer usaba un paso absoluto; aquí α es relativo, lo que hace comparables los números entre modelos.) Con α = 0,25 cambia el tema sin perder fluidez; con α = 1,0 degenera en repetición. El notebook incluye un control con una dirección aleatoria del mismo tamaño: córrelo siempre.
""",

"p2-predict-probe": """
    <b>1:21.</b> Que levanten la mano por cada opción y apunta el conteo en la pizarra; volveremos a él. La mayoría elige "gana el probe de SAE": ese es justamente el objetivo del fallo productivo.
""",

"p2-nb3": """
    <b>1:22–1:35.</b> El latente sugerido es el #3440 "Mexico and Argentina locations"; el que sale primero en el ranking suele ser más amplio ("países sudamericanos"), así que leer las etiquetas es parte del ejercicio. Casi todo el tiempo se va en los pasos 3 y 4. Si el steering produce galimatías, α es demasiado grande (1,0 lo rompe). En el respaldo con GPT-2, fíjate en el latente top #14944: es un latente de "palabras en español" que también se dispara con Simón Bolívar y Buenos Aires, un atajo del que su etiqueta no avisaba. A la 1:33 pide a todo el mundo que corra la celda del probe aunque se hayan saltado el steering.
""",

"p2-reveal": """
    <b>1:35–1:37.</b> Vuelve al conteo de manos. Luego pregunta quién vio cada resultado: en nuestras corridas de prueba la carrera salió mixta. Gemma 3 1B IT: probe simple 90 % IID / 95 % OOD frente a 88 % / 87 % para los 16 latentes principales del SAE (gana el simple, y más claramente fuera de distribución). Respaldo con GPT-2: ganó el probe sobre los 16 latentes del SAE, 89 % frente a 78 % IID. Ambos son legítimos. El titular es la literatura, no nuestra anécdota: en 113 conjuntos de datos los probes sobre SAE no fueron mejores de forma fiable, y DeepMind los encontró peores fuera de distribución en intención dañina. Por qué los probes simples son duros de batir: un probe ve todas las direcciones y se entrena para esta etiqueta; los latentes de un SAE descartan el error de reconstrucción y no se entrenaron para ella. Los probes lineales son lo que está desplegado, por ejemplo para detección de mal uso en Gemini.
""",

"p2-usefor": """
    <b>1:37–1:38.</b> El encuadre honesto: los SAEs fallaron una prueba para la que no fueron diseñados. Su valor es el descubrimiento: encontraste un latente "mexicano" en NB3 antes de escribir una sola etiqueta. Pero una etiqueta es una hipótesis: el latente de "palabras en español" de GPT-2 parecía de México y se disparaba con Simón Bolívar. Valídalo con un probe o con una intervención.
""",

"p2-nonid": """
    <b>1:38–1:40.</b> Fuente: Venkatesh y Kurapath, un póster del workshop de Representational Alignment de ICLR 2026, no de la conferencia principal. La cifra de 95–100 % viene del cuerpo del artículo (arXiv v3, contribuciones: "orthogonal perturbations achieving 95–100% of the original steering efficacy across multiple models and traits"); el resumen dice "near-equivalent efficacy". Muchas direcciones hacen el mismo trabajo. El steering es una prueba de existencia de un efecto, no evidencia de una representación única. Combínalo con pruebas de necesidad (ablación, patching). Esto prepara el Bloque 4: queremos validar explicaciones completas mediante intervención.
""",

"p2-sec4": """
    <b>1:40.</b> Ya tenemos lugares (patching) y unidades (features). Ahora conectamos las unidades en un cómputo para un prompt concreto.
""",

"p2-graph": """
    <b>1:41–1:45.</b> Paso 0: los tokens de entrada. Paso 1: "Dallas" activa una feature de Texas; "capital" y "state" activan una feature de "di una capital". Paso 2: las dos se combinan en "di Austin". El grosor = la fuerza del efecto directo. Paso 3: esa feature empuja el logit de Austin. Paso 4: los nodos grises son nodos de error: la parte de la salida de cada capa que el modelo de reemplazo no puede explicar. El artículo encuentra además un atajo directo más débil desde Dallas; es la arista fina. La idea: dos saltos, con un intermedio inspeccionable. En el grafo destacado de Neuronpedia que abrirán en NB4 (Gemma 2 2B), el supernodo de Texas incluye la capa 16 #25 "Texas" y la capa 14 #2268.
""",

"p2-howbuilt": """
    <b>1:45–1:47.</b> Un transcoder lee la entrada del MLP y predice su salida a través de una capa dispersa. Congelar los patrones de atención y la normalización hace que el reemplazo sea lineal en las features, de modo que los pesos de las aristas son efectos directos exactos para este prompt concreto. La poda deja un subgrafo legible, muchas veces de menos de cien nodos.
""",

"p2-validate": """
    <b>1:47–1:49.</b> Todos los números están medidos en la vía por defecto de NB4: Gemma 2 2B, el grafo destacado de Dallas, intervenciones enviadas por la API de steering de Neuronpedia. Paso 0: P(Austin) = 0,44. Paso 1: dirige las seis features de Texas en el token de Dallas. Ablacionarlas (0×) baja Austin a 0,18 (aparecen Oklahoma y Sacramento); llevarlas a −1× empuja Austin a ≈ 0,00 (aparece Albany, igual que en el propio recorrido de Neuronpedia). El control importa: aplicar −1× a otras seis features activas en Dallas deja Austin en 0,38. Paso 2: Texas a −1× más una feature de California a +0,5× pone Sacramento arriba, empatado, en 0,135. El intercambio es la evidencia más fuerte: el intermedio se usa, y se usa como un estado. Esto replica el experimento del artículo de Biology. Matiz honesto: escribir un concepto dentro es más difícil que apagar uno; con +1,0× California se pasa de rosca y acaba en otras ciudades californianas. La misma lógica que el patching del Bloque 2, ahora a nivel de features.
""",

"p2-nb4": """
    <b>1:49–2:03.</b> La vía por defecto para la sala es "neuronpedia": sin modelo, corre en cualquier sitio. Paso 1: el prompt de grafo propio por defecto de NB4 es un guiño local a Chihuahua: "Fact: the capital of the state containing Ciudad Juárez is" → Chihuahua. Créalo con + New Graph en https://www.neuronpedia.org/gemma-2-2b/graph y mira las features en " Juárez" (México, ubicaciones latinoamericanas). En nuestra prueba, llevar sus features principales a −1× bajó P(Chihuahua) de 0,20 a 0,00. Pasos 2–3: el grafo destacado es https://www.neuronpedia.org/gemma-2-2b/graph?slug=gemma-fact-dallas-austin; entre las features de Texas están la capa 16 #25 "Texas" y la capa 14 #2268. Fija el supernodo de Texas, pulsa Steer, pon −1× y corre: Austin cae (aparece Albany). Opcional: circuit-tracer sobre Gemma 2 2B necesita su propio runtime con GPU recién creado (versiones de librerías antiguas, ≈ 18 GB de descarga), así que solo para quien no haya usado su T4 en NB3 o tenga una segunda cuenta; la vía ligera por CPU (Gemma 3 270M) no puede hacer dos saltos y traza "the capital of the state of Texas" en su lugar. A las 2:01, aviso de un minuto.
""",

"p2-limits": """
    <b>2:03–2:05.</b> Los propios autores de Anthropic subrayan que el método da una comprensión satisfactoria solo en una parte de los prompts que prueban; no cites una cifra. Todo lo de aquí aplica al Bloque 5: una auditoría necesita explicaciones que se puedan poner a prueba.
""",

"p2-recap": """
    <b>2:05–2:08.</b> Recapitula de un tirón, una frase por fila. Luego la regla: la intervención es la prueba. Es exactamente lo que Víctor va a aplicar a un juez LLM.
""",

"p2-handoff": """
    <b>2:08–2:10.</b> Lee la frase literalmente y luego presenta a Víctor: va a usar exactamente estas dos herramientas, un probe y el patching, para preguntarse si podemos confiar en un juez LLM.
""",

# ========================================================= PART 3 · Víctor

"p3-section": """
    <b>2:10:00 → 2:10:15.</b> No hace falta decir nada más allá del título. "Bloque 5. Una pregunta: cuando un LLM juzga, ¿en cuáles de sus veredictos confiamos?"
""",

"p3-open": """
    <b>2:10:15 → 2:11:15.</b> Retoma la última frase de Salvador palabra por palabra (está en pantalla).
    "Esas dos frases son todo el instrumental de los próximos 40 minutos. Las apuntamos a un tipo distinto de salida del modelo: un veredicto de un LLM actuando como juez."
    Paso 1: el probe se convierte en una señal de confianza. "No la confianza que el juez dice, sino la que lleva su estado oculto." Es un correlato aprendido, no un detector de mentiras: puede equivocarse, y lo verán fallar bajo cambio de distribución.
    Paso 2: la idea del Bloque 2 — intervenir y mirar la salida — se convierte en una comprobación de fundamento. "¿El veredicto se apoyó en la evidencia que importa?" Hoy intervenimos sobre el texto de entrada (quitar o sustituir evidencia), que es su forma más simple; hacer patching de los estados ocultos de esos tokens es el paso natural siguiente.
""",

"p3-grid": """
    <b>2:11:15 → 2:12:15.</b> Dos cuerpos de texto: un conjunto de reglas (filas) y un corpus auditable (columnas: planes, actas, bitácoras de cambios, commits).
    Paso 1: el juez rellena cada celda con un veredicto. "Rápido, barato e incansable."
    Paso 2: "Nadie revisa todos estos. Así que la pregunta real no es '¿es el juez preciso en promedio?', sino qué veredictos necesitan a una persona."
    Pregunta: "¿Cómo decidirían qué celdas revisar?". Recoge una o dos respuestas (muestra aleatoria, las de baja confianza…).
""",

"p3-iso": """
    <b>2:12:15 → 2:13:00.</b> Sé breve; la norma es contexto, no contenido.
    ISO/IEC 29110 está dirigida a organizaciones de hasta 25 personas; el informe técnico 29110-3-1 da las guías de evaluación de procesos.
    Los equipos pequeños no pueden permitirse un auditor a tiempo completo, y eso es exactamente lo que hace atractiva la asistencia de un LLM, y también lo que hace que la confianza importe.
    Dilo explícitamente: "No vamos a citar la norma; su texto tiene licencia. Nuestra regla es inventada, escrita en su estilo."
""",

"p3-rule": """
    <b>2:13:00 → 2:13:45.</b> Lee la regla y el acta en voz alta, despacio.
    Pregunta a la sala: "Levanten la mano: ¿conforme? ¿no conforme?". Deja que se comprometan antes de revelar.
    Paso 1: la regla tiene tres cláusulas: registrado; impacto en calendario y costo evaluado; aprobación del cliente antes de empezar. "Tengan presentes estas tres."
""",

"p3-verdict": """
    <b>2:13:45 → 2:14:45.</b> El razonamiento del juez suena correcto: verifica la cláusula 1 y la mitad de la 2.
    Paso 1: la etiqueta de oro del auditor humano. El costo nunca se evaluó; el trabajo se programó sin aprobación del cliente.
    Paso 2: "Este es el caso peligroso: un veredicto seguro de sí mismo, fluido y equivocado. Si enrutamos según el 90 % que declara el propio juez, este nunca se revisa."
""",

"p3-probe": """
    <b>2:14:45 → 2:15:30.</b> El probe es una lectura lineal sobre el residual stream del juez en la posición de la respuesta — el último token del prompt, donde el siguiente token será Yes o No (que es lo que cachea NB5) — entrenada para predecir "¿es correcto este veredicto?". La herramienta del Bloque 3, con un objetivo nuevo.
    Paso 1: la aguja se queda en P(correcto) ≈ 0,4. El juez dijo 0,9. Umbral de aceptación automática: 0,7 (ilustrativo).
    Paso 2: por debajo del umbral → se enruta a un auditor humano. "Las palabras del modelo decían 90 %; su estado oculto, no."
""",

"p3-ground": """
    <b>2:15:30 → 2:16:45.</b> La idea del Bloque 2 aplicada al texto de entrada: cambia una pieza de evidencia, deja todo lo demás igual y mira el veredicto. Es una intervención a nivel de texto, exactamente lo que hace NB5 (sustituir el extracto por texto genérico irrelevante, o quitar un segmento; está precalculado para que corra sin GPU). Hacer patching de los estados ocultos de esos tokens es el paso natural siguiente (la herramienta del Bloque 2) y localizaría dónde se lee la pista; hoy no lo hacemos.
    Paso 1: quita "3 extra days" → el veredicto cambia a no conforme. Esa frase es la que carga la decisión.
    Paso 2: restitúyela y añade "The customer rejected the change." → sigue siendo conforme. Un rechazo del cliente debería volverlo no conforme de inmediato.
    Paso 3: "La estimación de calendario es evidencia relevante, para la cláusula 2. El problema es que el veredicto depende solo de ella e ignora la cláusula 3, la aprobación. Un auditor jamás aceptaría un veredicto fundamentado así."
""",

"p3-why": """
    <b>2:16:45 → 2:17:30.</b> La historia de R-PM-07 es inventada; este resultado no.
    Radharapu et al. entrenan probes lineales sobre los estados ocultos de jueces con razonamiento, con una pérdida de Brier. Comparados con la confianza verbalizada y con métodos de múltiples generaciones: mejor calibración, ≈10× más baratos, y en sus experimentos generalizó a dominios de evaluación no vistos. No vendas la transferencia como un hecho general: en nuestra propia corrida de prueba (el juez de respaldo de NB5) el probe NO transfirió a las aserciones reservadas; adelántalo: "van a comprobar si transfiere". Su matiz honesto: los probes son conservadores y rinden peor en conjuntos fáciles, lo que encaja con entornos críticos que priorizan pocos falsos positivos. Las auditorías son uno de esos entornos.
    Probabilidad del token: para un juez de Yes/No, P(Yes) de los logits de salida es gratis y suele ordenar bien; en NB5 es la línea base a batir, junto con la confianza verbalizada. Un probe solo es interesante si lleva información más allá de la probabilidad de salida (mayor AUROC, ya que recalibrar arregla el ECE pero no el orden).
    Semantic entropy probes (Kossen, Han et al.) hacen el mismo truco para alucinaciones: predecir la incertidumbre con una sola pasada en vez de muchas muestras.
""",

"p3-a10": """
    <b>2:17:30 → 2:19:30.</b> Pieza central. Datos sintéticos (dilo): 3.000 veredictos simulados, precisión del juez ≈ 74 %. Nada de esta slide está medido.
    Izquierda = diagrama de fiabilidad: x = confianza declarada, y = con qué frecuencia el veredicto es realmente correcto; la diagonal es calibración perfecta.
    Paso 0: la confianza verbalizada se amontona entre 0,8 y 1,0 pero la precisión se queda cerca de 0,75 → barras muy por debajo de la diagonal = exceso de confianza.
    Paso 1: las barras del probe se pegan a la diagonal.
    Paso 2: derecha = riesgo-cobertura. Acepta automáticamente todo veredicto cuya puntuación del probe sea ≥ τ. Cobertura = proporción aceptada automáticamente; el eje y = tasa de error entre los aceptados. Con el umbral bajo: aceptas casi todo y se escapa cada error.
    Pasos 3 y 4: sube τ. Menos aceptaciones automáticas, muchísimos menos errores escapados. Lee en voz alta la línea bajo la gráfica: 'errores escapados' = veredictos que son erróneos Y aceptados automáticamente, como proporción de todos los veredictos (la definición de NB5, y la tasa de escape de la siguiente slide). La línea discontinua es el objetivo de enrutamiento de NB5: como mucho 10 % de error entre los veredictos aceptados automáticamente. En los datos sintéticos la curva del probe alcanza el objetivo del 10 % hacia un 38–40 % de cobertura (paso 4, τ = 0,83: acepta automáticamente el 38 %, error entre aceptados ≈ 9,9 %, errores escapados 3,8 % del total). Enrutar por confianza verbalizada solo baja del 10 % con una cobertura mínima (por debajo del ~8 %), porque sus puntuaciones apenas separan lo correcto de lo incorrecto. El paso 3 (τ = 0,62): 74 % de cobertura pero ≈ 18 % de error entre los aceptados, por encima del objetivo.
    Señala la curva gris: "Con la misma cobertura, enrutar por confianza verbalizada deja pasar más errores."
    El deslizador se puede arrastrar con el ratón si alguien pregunta "¿y con el 90 %?"; hacer clic en la gráfica no avanza las slides.
""",

"p3-conformal": """
    <b>2:19:30 → 2:20:15.</b> Dilo con claridad: "Esto es una dirección de investigación — mi línea de tesis, auditorías asistidas por LLM de calidad y seguridad de proyectos de software — no un resultado publicado."
    Paso 1: un conjunto de calibración con etiquetas de oro: n = 60 veredictos sintéticos, colocados por puntuación del probe. Gris = el juez acertó, rojo = se equivocó. Casi todos los rojos están en puntuaciones bajas, pero no todos.
    Paso 2: un escape es un veredicto erróneo Y aceptado automáticamente (puntuación ≥ τ); la tasa de escape son los escapes sobre TODOS los veredictos (la definición de NB5, la misma que la lectura de A10). La regla, exactamente el crc_threshold de NB5: recorre los umbrales de menor a mayor y toma el primero (el más bajo) con (n/(n+1))·escape_cal(τ) + 1/(n+1) ≤ α. El término 1/(n+1) es el precio por muestra finita; con n = 60 ya consume 1,6 de los 10 puntos, así que el presupuesto empírico de escape queda en torno al 8,5 %. Lee la línea bajo el eje: cuántos puntos rojos quedan rodeados (escape), la cota, y cuántos veredictos se aceptan automáticamente. Esto es control conforme del riesgo con la puntuación del probe: si los veredictos nuevos son intercambiables con los de calibración, la tasa de escape ESPERADA en los nuevos es ≤ α (en esperanza sobre conjuntos de calibración, no para cada auditoría).  La misma receta que la ampliación opcional del final de NB5.
    Nota para expertos: esto acota los escapes sobre todos los veredictos, no la proporción de errores que escapan (una tasa de omisión). Con un juez con ~74 % de precisión, un α = 10 % de todos los veredictos puede seguir siendo una fracción grande de los errores; elige α con el auditor.
    Paso 3: la garantía necesita intercambiabilidad. Un proceso 29110 nuevo, o una aserción reservada en NB5, es justo donde puede fallar. Esa es la prueba de cambio de distribución que van a correr.
""",

"p3-legal": """
    <b>2:20:15 → 2:21:00.</b> No podemos compartir registros de auditoría reales, así que usamos un análogo público con la misma forma.
    LegalBench tiene 14 tareas contract_nli_* (CC BY 4.0), cada una una aserción de ContractNLI aplicada a cláusulas de acuerdos de confidencialidad, p. ej. "la Parte Receptora puede compartir cierta Información Confidencial con algunos terceros"; las etiquetas de oro vienen de las anotaciones de ContractNLI (binarizadas por LegalBench).
    Prompt exacto: sistema "You are a compliance auditor."; usuario "Contract clause: {excerpt} — Does this clause state that {assertion}? Answer Yes or No." El veredicto se lee de los logits del siguiente token Yes/No (lo que también da la línea base de probabilidad del token); la confianza verbalizada viene de una pregunta de seguimiento que pide un 0–100.
    Particiones: 11 aserciones repartidas por documento en train / cal / test (ningún NDA de test se vio en entrenamiento). 3 aserciones se reservan por completo — aviso sobre divulgación obligada, devolución de información confidencial y supervivencia de obligaciones — como sustituto de un proceso 29110 nuevo.
    El juez es Gemma 3 4B IT; sus veredictos y activaciones del residual stream (en el último token del prompt) están cacheados, así que NB5 corre en un runtime de CPU. COMPROBAR ANTES DE LA SESIÓN: si la caché de Gemma no está publicada, NB5 cae a Qwen2.5-0.5B; en ese caso dilo y cambia esta fila.
    AQUÍ ES DONDE SE LES DICE QUE ABRAN NB5, con esta slide en pantalla: "Abran <code>bit.ly/micai-mi-nb5</code> (o NB5 desde el enlace de materiales) y corran la primera celda; Entorno de ejecución &gt; CPU basta, no hace falta GPU, y descarga la caché mientras termino esta slide." TODO antes del evento: crear ese enlace corto y probarlo. El asistente ayuda a quien no lo tenga abierto; con una laptop por pareja alcanza.
""",

"p3-predict": """
    <b>2:21:00 → 2:21:30.</b> Que levanten la mano por A, B, C y D. Apunta los conteos en la pizarra; volvemos a ellos en el debrief.
    A estas alturas todos deberían tener NB5 abierto (se los dijiste en la slide de LegalBench); si alguien no, dales 20 segundos y empareja: <code>bit.ly/micai-mi-nb5</code>.
    Pídeles que escriban su propia predicción en la celda Predict del notebook antes de correr nada.
    Las opciones C y D importan: la probabilidad del token es gratis y a menudo fuerte; un probe que solo la empata añade costo, no información.
""",

"p3-nb5": """
    <b>2:21:30 → 2:43:30 (22 min).</b> Si la sala está en pleno flujo, toma 2 o 3 minutos más del debrief, no del cierre.
    Repite el enlace y deja esta slide en pantalla: <code>bit.ly/micai-mi-nb5</code>; es el único lugar donde el enlace de NB5 aparece proyectado (también <code>notebooks/student/NB5_judge_confidence.ipynb</code> en los materiales). Para este nadie necesita GPU ni haber hecho NB0.
    En parejas: una persona conduce, la otra lee las celdas y predice. Los pasos 1–4 son el núcleo; el 5 es el resultado clave; el 6 es la comprobación de fundamento; el umbral conforme es una ampliación opcional.
    Tres señales de confianza, comparadas en la partición de test: la verbalizada 0–100, la probabilidad del token Yes/No (confianza en la respuesta elegida) y el probe (ajustado en train, con la capa elegida y calibrado por Platt en cal). Insiste en que la probabilidad del token es la línea base fuerte y barata; recalibrar arregla el ECE pero no puede cambiar el AUROC, así que el AUROC es donde el probe tiene que ganar.
    El objetivo de enrutamiento es 10 % de error entre los veredictos aceptados automáticamente (con el 5 % casi no quedaba cobertura con el juez pequeño de prueba; con la caché de Gemma pueden intentar 0,05).
    El paso 6 es a nivel de texto: la evidencia se sustituye por texto genérico irrelevante o se quita un segmento (precalculado). Hacer patching de estados ocultos sería el paso siguiente, no hoy.
    Circula por la sala. Tropiezo común: el objetivo es "¿es erróneo el veredicto?", no "¿la respuesta es Yes?"; la confianza tiene que ser la de la respuesta elegida, max(P(Yes), P(No)).
    Controles de tiempo a las 2:30 (deberían ir por el paso 3) y a las 2:37 (paso 5).
""",

"p3-debrief": """
    <b>2:43:30 → 2:48:00.</b> Vuelve a los conteos de A/B/C/D. Pide a dos parejas sus números de AUROC/ECE a partir de la caché (Gemma 3 4B si está publicada; si no, el respaldo de Qwen: di cuál); esos son los números reales de la sesión.
    Lo que vimos en nuestras pruebas (juez de respaldo Qwen2.5-0.5B, NO el Gemma 3 4B de la sesión; di "en nuestra corrida de prueba", nunca lo presentes como un resultado): precisión del juez 75 % en test, 64 % en las aserciones reservadas. AUROC para detectar veredictos erróneos en test: verbalizada 0,43 (peor que el azar: solo respondía 75, 80, 85 o 95), probabilidad del token 0,63, probe 0,71. En las aserciones reservadas el probe NO transfirió: con su umbral de cal se escapó el 17,5 % de los veredictos, frente al 8 % de la probabilidad del token. Fundamento: de los 40 veredictos Yes más seguros, el 70 % siguió siendo Yes cuando la evidencia se sustituyó por texto genérico irrelevante, aunque esos veredictos eran correctos.
    Lecciones que hay que sacar: (1) las palabras no sirven como filtro, la probabilidad del token sí es una línea base real; (2) un probe puede ganar dentro de distribución y fallar con una regla nueva: puede estar aprendiendo "qué reglas son difíciles" en vez de la incertidumbre del juez; (3) un veredicto correcto puede estar igualmente infundado, y ni la precisión ni una puntuación de confianza lo revelan.
    Cierra con la pregunta del auditor: una puntuación calibrada por sí sola no es evidencia; un umbral con una cota de escape declarada, más una comprobación de fundamento sobre una muestra de veredictos, empieza a parecerse a algo que un evaluador podría firmar.
""",

"p3-map": """
    <b>2:48:00 → 2:49:30.</b> Todo el tutorial en una tabla. Las filas aparecen una por cada →.
    Fila 1, probe (Bloques 3 y 5): valida con particiones reservadas y fuera de distribución, como acaban de hacer. Fila 2, patching (Bloque 2): comprueba que el efecto sobrevive a otras corrupciones, y usa path patching para separar rutas directas de indirectas. Fila 3, SAEs (Bloque 3): si un probe simple lo iguala, el SAE no aportó nada (Kantamneni et al., ICML 2025). Fila 4, grafos de atribución (Bloque 4): un grafo es una hipótesis hasta que intervienes. Fila 5, steering: un artículo de workshop de 2026 (workshop de Representational Alignment de ICLR 2026, arXiv 2602.06801) reporta que las direcciones de steering no son identificables: perturbaciones ortogonales pueden alcanzar buena parte del efecto, así que pruébalas.
    Paso 6: resalta. "El Bloque 5 usó solo las dos primeras filas, y la segunda solo en su forma más simple: intervenimos sobre el texto de entrada, no sobre estados ocultos. Las herramientas más sencillas hicieron el trabajo de auditoría; el patching de estados ocultos es el siguiente paso evidente."
""",

"p3-transfer": """
    <b>2:49:30 → 2:51:30.</b> Reparte el lienzo de transferencia impreso (printables/transfer_canvas.pdf).
    Dos minutos, en parejas: cada persona rellena las casillas 1–3 para su propio trabajo; si da tiempo, de la 4 a la 6. Ejemplos para desatascar: bots de revisión de código, rúbricas de calificación, triaje de notas clínicas, jueces de relevancia en recuperación.
    Recoge un ejemplo de la sala antes de seguir.
""",

"p3-field": """
    <b>2:51:30 → 2:55:00.</b> Los pasos 1 a 5 recorren el arco de la tarde: Miguel observó, Salvador intervino, descompuso y trazó, nosotros auditamos.
    Paso 6, problemas abiertos (Sharkey et al., "Open Problems in Mechanistic Interpretability", TMLR 2025): la mayoría de los resultados de circuitos explican un prompt, no un mecanismo global; los grafos de atribución explican un modelo de reemplazo, y cuán fiel es al modelo real es una pregunta abierta; automatizar la interpretabilidad con agentes; no hay estándares de evaluación acordados.
    Paso 7, implicaciones: aseguramiento y auditorías (el bloque de hoy), evidencia que los reguladores podrían exigir, y usar los modelos como objetos de estudio científico.
    Frase de honestidad: "Estas herramientas son jóvenes. La mayoría de los resultados son sobre modelos pequeños o prompts sueltos. Traten cada interpretación como una hipótesis con una prueba asociada."
""",

"p3-res": """
    <b>2:55:00 → 2:56:00.</b> No leas la lista. "Columna izquierda: las herramientas de los notebooks y dónde aprender más; el capítulo 1 de ARENA es el mejor curso gratuito para continuar. Columna derecha: los artículos sobre los que se construyeron los bloques de hoy; la revisión de Open Problems es el mapa de lo que todavía nadie sabe."
    Toy Models of Superposition: transformer-circuits.pub/2022/toy_model · Towards Monosemanticity: transformer-circuits.pub/2023/monosemantic-features · Circuit Tracing (métodos): transformer-circuits.pub/2025/attribution-graphs/methods.html.
    Todos los enlaces están también en la carpeta de materiales (ver la última slide).
""",

"p3-exit": """
    <b>2:56:00 → 2:58:00.</b> TODO: insertar el enlace al formulario de salida y el código QR en el recuadro punteado antes de la sesión.
    Dales los dos minutos completos en silencio. La pregunta 2 es de la que más aprendemos.
""",

"p3-thanks": """
    <b>2:58:00 → 3:00:00.</b> TODO: sustituir el marcador "materials link" por la URL del repositorio o del Drive (y un QR si es posible).
    Agradece al asistente por su nombre. Invita a quedarse a preguntas; los notebooks siguen funcionando después de hoy.
""",

}
