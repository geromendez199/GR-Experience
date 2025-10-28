# GR-Experience
Repositorio para el proyecto GR Experience del Hack the Track 2025

### Prompt for Codex

Eres el socio de código de ChatGPT utilizando los modelos Codex de OpenAI. Debes construir una aplicación web full‑stack llamada **GR‑Experience** que use los datos de telemetría y cronometraje de la Toyota GR Cup para ofrecer analítica en tiempo real, entrenamiento de pilotos y una experiencia inmersiva para los fans. Usa **Python** (para procesamiento de datos, modelado y backend) y **React/Next.js** (para el frontend) junto con **Three.js** para la visualización 3D. La aplicación debe incluir las siguientes funciones:

1. **Ingesta de datos**: Escribe scripts que descarguen y descompriman los datasets de telemetría (“barber-motorsports-park.zip”, “circuit-of-the-americas.zip”, etc.) que contienen datos de telemetría y tiempos de vuelta en CSV/JSON. Limpia y normaliza los datos, corrigiendo errores en el conteo de vueltas y valores faltantes.

2. **Modelado y analítica**:
   - Calcula métricas por vuelta: velocidad, posición de acelerador/freno, tiempos de sector.
   - Calcula la línea de carrera óptima comparando cada vuelta con la más rápida usando *Dynamic Time Warping* y destaca dónde el piloto es más lento o rápido.
   - Crea modelos predictivos (con scikit‑learn: RandomForest, GradientBoosting) para predecir tiempos de vuelta, degradación de neumáticos y estrategia de paradas en boxes usando datos históricos. Implementa funciones para simular escenarios de carrera (safety car, pit stops).
   - Implementa un motor de estrategia en tiempo real: dado el estado actual de la carrera, calcula la ventana de parada recomendada y la posición final prevista.

3. **Backend API (FastAPI)**:
   - Expone endpoints REST para obtener datos agregados y estadísticas por carrera/evento/piloto.
   - Proporciona predicciones y sugerencias en función del escenario actual.
   - Sirve coordenadas 3D y telemetría para el replay 3D.
   - Ofrece sugerencias de entrenamiento para pilotos (sectores a mejorar, puntos de frenado recomendados).
   - Utiliza WebSockets para enviar actualizaciones en tiempo real al cliente.

4. **Frontend (Next.js con React)**:
   - Construye un dashboard interactivo con:
     - Desplegables para seleccionar carrera, piloto y dataset.
     - Gráficas (Plotly.js o D3.js) de tiempos de vuelta, rendimiento por sector y trazas de acelerador/freno.
     - Un panel de estrategia en tiempo real donde el usuario puede ajustar variables (vuelta de parada, condiciones climáticas) y ver el resultado previsto de la carrera.
     - Una pestaña de entrenamiento que superponga la línea óptima en un mapa del circuito y resalte las zonas de mejora.
   - Implementa un replay 3D con Three.js: renderiza el trazado y mueve el modelo del auto según la telemetría; permite controlar la cámara para ver desde el interior o desde un helicóptero; muestra superposiciones de datos en tiempo real.

5. **Arquitectura y organización del repositorio**:
   - Estructura el proyecto en `/data` para scripts y datasets, `/backend` para el servidor FastAPI y `/frontend` para la app de Next.js.
   - Utiliza TypeScript en el frontend.
   - Incluye un `docker-compose.yml` para orquestar backend y frontend.
   - Incluye pruebas unitarias para el procesamiento y los modelos.
   - Documenta cómo ejecutar el backend y el frontend en local.

Escribe código limpio y modular con comentarios y sin texto de relleno. Asegúrate de que todo el proyecto funcione de extremo a extremo según estas especificaciones.
