# Luma · Asistente virtual de Computación

Aplicación independiente con avatar animado, chat en español, lectura de respuestas en voz alta y entrada por micrófono cuando el navegador la admite.

## Ejecutar

```bash
git clone https://github.com/thomasklz/asistentevirtual.git
cd asistentevirtual
docker compose up --build -d
```

Abrir **http://localhost:8001**. Sin clave de API, funciona en **modo demostración** con respuestas sobre la carrera de Computación y sus docentes, limitadas a `carrera.json` y `docentes.json`; la interfaz indica claramente que no hay IA conectada.

## Conectar ChatGPT mediante la API de OpenAI

1. Copiar `.env.example` a `.env`.
2. Poner `OPENAI_API_KEY=...` en `.env` (nunca en el código ni en el navegador).
3. Ejecutar `docker compose up -d --force-recreate`.

Se usa la Responses API con `gpt-6-luna` por defecto; puedes cambiar `OPENAI_MODEL` en `.env`. La API se factura por separado de una suscripción a ChatGPT. El servidor solo envía las preguntas y los datos de carrera y docentes cuando la clave está configurada. No guarda las conversaciones en disco. La interfaz informa de la transferencia a OpenAI.

El máximo de salida de la API es `OPENAI_MAX_OUTPUT_TOKENS=1200` por defecto (incluye tokens visibles y de razonamiento). Se puede cambiar en `.env` y recrear el contenedor; el servidor acepta valores entre 256 y 4000. Las preguntas de un solo dato siguen recibiendo respuestas breves, mientras que las peticiones de explicación o listado pueden ser más completas. La pregunta del visitante tiene un límite distinto: 500 caracteres.

## Información de la carrera

`carrera.json` contiene una ficha revisable elaborada a partir de los PDF y los datos proporcionados por el usuario: malla actual, prácticas, requisitos documentados, temas de algunas asignaturas, jornada, horario, contacto, objetivo, misión, visión, campo profesional y perfil de egreso. La malla actual es la referencia predeterminada; la anterior solo se usa si la pregunta la menciona. El PDF de rediseño de 2015 describe un plan histórico de diez períodos y no sustituye la duración actual de ocho niveles. No se convierten niveles a años ni se inventan admisión o costos. Confirma la vigencia y cualquier situación individual con la coordinación de la carrera.

Para actualizar la ficha, edita `carrera.json` y reconstruye con `docker compose up --build -d`.

## Docentes y asignaturas

`docentes.json` guarda el listado de asignaciones entregado por el usuario, consolidado por docente, asignatura y nivel para no repetir paralelos. Luma puede responder quién dicta una asignatura, qué asignaturas figuran para un docente o qué docentes aparecen en un nivel. Los niveles 9 y 10 se etiquetan como malla anterior. El listado no incluye fecha ni período académico, por lo que no se presenta como garantía de asignaciones vigentes o futuras.

Este repositorio contiene únicamente el asistente de Computación. No incluye proyectos de feria y Luma no responde sobre ellos.

El micrófono usa Web Speech API del navegador y puede no estar disponible en todos; el texto siempre funciona. Algunos navegadores pueden enviar el audio a su propio servicio de reconocimiento. La síntesis de voz usa las voces instaladas en el navegador. Para una feria, Chrome o Edge en `localhost` suelen ser una opción práctica, pero hay que probar micrófono y altavoces en el equipo real.

## Pruebas

```bash
python3 -m unittest -v test_knowledge.py
docker compose ps
curl http://localhost:8001/api/status
```

El contenedor solo escucha desde el equipo local (`127.0.0.1:8001`). No pongas una clave de API en un sitio público sin autenticación y límites de uso más estrictos.
