# Guía de ejecución paso a paso

## Fase A — GitHub

1. Crear un repositorio, por ejemplo `actividad3-devops-cicd`.
2. Copiar todo el contenido de este proyecto al repositorio.
3. Ejecutar:

```bash
git init
git add .
git commit -m "feat: estructura inicial laboratorio CI CD"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/actividad3-devops-cicd.git
git push -u origin main
```

4. En GitHub abrir **Actions**.
5. Esperar el workflow `CI - Build, Test and Validate`.
6. Abrir el job `Python CI` y comprobar que todos los steps estén verdes.
7. Tomar capturas de la ejecución completa y del detalle de pruebas.

### Prueba adicional para demostrar pull request

```bash
git checkout -b feature/mejora-mensaje
# Realizar un cambio menor en app.py
git add app.py
git commit -m "feat: ajustar mensaje de inicio"
git push -u origin feature/mejora-mensaje
```

Crear un Pull Request hacia `main` y capturar que el mismo CI vuelve a ejecutarse automáticamente.

## Fase B — Docker Hub

1. Crear un repositorio público o privado llamado `devops-web-lab`.
2. Crear un Access Token para Jenkins; no guardar la contraseña en el Jenkinsfile.

## Fase C — Jenkins

### Requisitos del agente Jenkins

El agente que ejecute el job debe disponer de:

- Git.
- Docker CLI con acceso a un daemon Docker.
- `curl`.
- Acceso de red a GitHub y Docker Hub.

### Crear credenciales

En **Manage Jenkins → Credentials**:

- Kind: `Username with password`.
- ID: `dockerhub-credentials`.
- Username: usuario de Docker Hub.
- Password: Access Token.

### Crear el pipeline

1. New Item → Pipeline.
2. Nombre: `actividad3-devops-cd`.
3. En Pipeline elegir `Pipeline script from SCM`.
4. SCM: Git.
5. Repository URL: URL del repositorio.
6. Branch Specifier: `*/main`.
7. Script Path: `Jenkinsfile`.
8. Guardar.
9. Ejecutar **Build with Parameters**.
10. En `DOCKERHUB_NAMESPACE`, escribir el usuario real de Docker Hub.
11. Mantener `DEPLOY_TO_K8S=false` para esta entrega.

### Evidencia esperada

Los stages visibles deben ser:

1. Checkout.
2. Validate Definition.
3. Build Docker Image.
4. Smoke Test Container.
5. Publish to Docker Hub.
6. Prepare Kubernetes Manifest.
7. Deploy to Kubernetes - Optional (skipped en esta actividad).

El stage opcional demuestra continuidad con la siguiente fase ABP sin exigir un cluster para aprobar esta entrega.

## Fase D — Capturas

Capturar únicamente evidencia real. No fabricar imágenes.

- `01-repositorio-github.png`
- `02-actions-success.png`
- `03-actions-tests.png`
- `04-jenkins-stages.png`
- `05-jenkins-console.png`
- `06-dockerhub-image.png`

Actualizar después las rutas en `INFORME_TECNICO.md`.
