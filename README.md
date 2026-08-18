# Actividad 3 — Laboratorio técnico CI/CD

Aplicación web mínima en Python/Flask para demostrar dos pipelines complementarios:

- **CI con GitHub Actions:** checkout → instalación → validación sintáctica → análisis estático → pruebas y cobertura.
- **CD con Jenkins:** checkout → validación → construcción Docker → smoke test → publicación en Docker Hub → generación de manifiesto Kubernetes → despliegue opcional.

## 1. Flujo arquitectónico

```text
Desarrollador
    |
    | push / pull request
    v
GitHub Repository
    |
    +------> GitHub Actions (CI)
    |          1. Checkout
    |          2. Setup Python
    |          3. Dependencias
    |          4. Compile check
    |          5. Ruff
    |          6. Pytest + cobertura
    |          7. Artefacto coverage.xml
    |
    +------> Jenkins (CD)
               1. Checkout
               2. Validar definición
               3. docker build
               4. Smoke test /health
               5. docker push
               6. Render manifiesto K8s
               7. kubectl apply (opcional/siguiente fase)
                        |
                        v
                  Docker Hub / Kubernetes
```

## 2. Estructura del repositorio

```text
.
├── .github/workflows/ci.yml
├── docs/
│   ├── INFORME_TECNICO.md
│   ├── GUIA_EJECUCION.md
│   └── evidencias/
├── k8s/
│   ├── deployment.yaml
│   └── service.yaml
├── tests/test_app.py
├── app.py
├── Dockerfile
├── Jenkinsfile
├── pyproject.toml
├── requirements.txt
└── requirements-dev.txt
```

## 3. Ejecutar localmente

```bash
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
pip install -r requirements-dev.txt
ruff check app.py tests
pytest --cov=app --cov-report=term-missing
python app.py
```

Abrir `http://localhost:8000/` y validar salud en `http://localhost:8000/health`.

## 4. CI — GitHub Actions

El workflow `.github/workflows/ci.yml` se dispara automáticamente con **cada `push` y `pull_request`**. También incluye `workflow_dispatch` para ejecutar una demostración manual sin perder los disparadores automáticos exigidos.

El job falla si el análisis estático presenta defectos, si una prueba falla o si la cobertura queda por debajo del 85 %. Esto convierte las validaciones en un **quality gate** antes de avanzar hacia la entrega.

## 5. CD — Jenkins

El `Jenkinsfile` usa Pipeline Declarativo y define stages explícitos. Para publicar una imagen se requiere:

1. Crear en Docker Hub el repositorio `devops-web-lab`.
2. En Jenkins crear una credencial tipo **Username with password**:
   - ID: `dockerhub-credentials`
   - Username: usuario Docker Hub
   - Password: Access Token de Docker Hub
3. Crear un Pipeline o Multibranch Pipeline apuntando a este repositorio.
4. Cambiar el parámetro `DOCKERHUB_NAMESPACE` por el usuario/organización de Docker Hub.
5. Ejecutar `Build with Parameters`.

La imagen se publica con una etiqueta inmutable basada en `BUILD_NUMBER` + SHA corto, por ejemplo:

```text
usuario/devops-web-lab:15-a1b2c3d
```

En `main`, el pipeline también actualiza `latest`. Para trazabilidad, la etiqueta inmutable es la referencia recomendada para los manifiestos.

## 6. Kubernetes — continuidad del proyecto ABP

La actividad actual solo requiere definir el CD; por eso el despliegue real está deshabilitado por defecto (`DEPLOY_TO_K8S=false`). El pipeline sí produce un manifiesto listo para un entorno Kubernetes agnóstico. Esto deja preparada la siguiente fase del proyecto sin convertir este laboratorio en una implementación dependiente de un proveedor de nube.

## 7. Evidencias para entregar

Agregar capturas reales en `docs/evidencias/` y referenciarlas desde `docs/INFORME_TECNICO.md`:

1. Repositorio GitHub mostrando estructura completa.
2. GitHub Actions en estado verde después de un `push`.
3. Detalle de los stages/steps de CI, especialmente Ruff y Pytest.
4. Jenkins Stage View o Blue Ocean mostrando los stages definidos.
5. Consola Jenkins mostrando `docker build` y `docker push` exitosos, si se ejecutan.
6. Docker Hub mostrando la imagen y sus tags.

## 8. Principios DevOps evidenciados

- **Flujo:** automatización desde el commit hasta un artefacto desplegable.
- **Retroalimentación rápida:** GitHub Actions informa fallos inmediatamente en el mismo flujo de desarrollo.
- **Aprendizaje y mejora continua:** cobertura, lint y resultados del pipeline generan evidencia objetiva para ajustar el software.
- **Pipeline as Code:** CI y CD están versionados junto al código (`ci.yml` y `Jenkinsfile`).
- **Shift left:** pruebas y análisis estático se ejecutan antes de construir/publicar el artefacto final.
- **Reproducibilidad:** Docker encapsula la aplicación y Kubernetes define declarativamente su ejecución futura.

## 9. Entrega

Entregar:

- URL del repositorio GitHub.
- Capturas de GitHub Actions y Jenkins.
- Todos los archivos de configuración dentro del repositorio.
- `docs/INFORME_TECNICO.md` exportado a PDF si se desea entregar en PDF.
