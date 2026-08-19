# Informe técnico — Actividad 3: Laboratorio CI/CD

**Asignatura:** Fundamentos de DevOps  
**Actividad:** Laboratorio técnico — Integración y Entrega Continua  
**Estudiante:** Victor Enrique Cantor Beltran 
**Repositorio:** https://github.com/vecantor15/actividad3-devops-cicd 
**Fecha:** 18 de agosto 2026

## 1. Objetivo

El laboratorio implementa una primera fase del proyecto ABP mediante dos pipelines versionados junto con el código de una aplicación web. GitHub Actions se utiliza para Integración Continua (CI), mientras Jenkins define la Entrega Continua (CD) del artefacto contenerizado. El propósito es transformar cada cambio de código en retroalimentación verificable y, cuando las validaciones son satisfactorias, producir una imagen Docker trazable y preparada para un despliegue posterior en Kubernetes.

## 2. Aplicación seleccionada

Se construyó una aplicación web mínima con Python y Flask. La aplicación expone un endpoint principal (`/`) y un endpoint de salud (`/health`). La simplicidad funcional es deliberada: permite concentrar el laboratorio en el flujo DevOps y no en complejidad accidental de negocio.

## 3. Arquitectura del flujo

```text
Push / Pull Request
        |
        v
     GitHub
        |
        +--> GitHub Actions (CI)
        |    Checkout -> Dependencias -> Compile -> Ruff -> Pytest/Cobertura
        |
        +--> Jenkins (CD)
             Checkout -> Docker Build -> Smoke Test -> Docker Hub
                                          |
                                          v
                                 Manifiesto Kubernetes
                                  (despliegue opcional)
```

La división entre CI y CD responde al alcance de la actividad: GitHub Actions proporciona retroalimentación automática ante cada cambio; Jenkins transforma un estado validado del repositorio en un artefacto de entrega versionado.

## 4. Pipeline CI con GitHub Actions

El archivo `.github/workflows/ci.yml` se activa ante `push` y `pull_request`. Se definieron las siguientes etapas lógicas:

1. **Checkout:** obtiene la revisión exacta asociada al evento.
2. **Setup Python:** fija Python 3.13 para evitar variaciones entre ejecutores.
3. **Instalación de dependencias:** reproduce el entorno requerido por la aplicación y las pruebas.
4. **Validación sintáctica:** detecta tempranamente errores de compilación/importación.
5. **Análisis estático:** Ruff verifica reglas de calidad antes de las pruebas.
6. **Pruebas automatizadas:** Pytest valida comportamiento funcional y exige cobertura mínima del 85 %.
7. **Evidencia:** se conserva `coverage.xml` como artefacto del workflow.

Estas etapas aplican el enfoque *shift left*: la calidad se verifica cerca del momento en que se introduce el cambio. Además, el pipeline constituye un ciclo rápido de retroalimentación porque el resultado queda asociado al `push` o Pull Request.

### Evidencia CI

![GitHub Actions exitoso](evidencias/02-actions-success.png)

![Pruebas y cobertura](evidencias/03-actions-tests.png)

> Reemplazar estas referencias únicamente con capturas reales de la ejecución.

## 5. Pipeline CD con Jenkins

El `Jenkinsfile` utiliza Pipeline Declarativo y Pipeline as Code. Los stages definidos son:

### 5.1 Checkout

Clona el repositorio y obtiene un SHA corto. El identificador se combina con `BUILD_NUMBER` para crear una etiqueta de imagen trazable.

### 5.2 Validate Definition

Comprueba que los artefactos mínimos del flujo estén presentes antes de construir: Dockerfile, workflow CI y manifiestos Kubernetes.

### 5.3 Build Docker Image

Construye una imagen reproducible a partir del Dockerfile. La aplicación se ejecuta dentro de un contenedor con un usuario sin privilegios y expone el puerto 8000.

### 5.4 Smoke Test Container

Inicia temporalmente el contenedor y consulta `/health`. El pipeline se detiene si el artefacto construido no responde correctamente. Esta etapa evita publicar una imagen que fue construida técnicamente, pero que no puede arrancar.

### 5.5 Publish to Docker Hub

Jenkins utiliza una credencial administrada (`dockerhub-credentials`) y no almacena secretos en el código fuente. Publica una etiqueta inmutable `BUILD_NUMBER-SHA`, y en la rama `main` también actualiza `latest`.

### 5.6 Prepare Kubernetes Manifest

Sustituye `IMAGE_PLACEHOLDER` por la imagen exacta publicada y archiva el manifiesto resultante. El resultado es agnóstico respecto a AWS, Azure o GCP porque se basa en recursos estándar de Kubernetes.

### 5.7 Deploy to Kubernetes — opcional

El stage queda definido para demostrar continuidad arquitectónica con la siguiente fase del proyecto, pero se encuentra deshabilitado por defecto. Solo se ejecutaría con `DEPLOY_TO_K8S=true` y una credencial `kubeconfig` configurada.

### Evidencia CD

![Jenkins stages](evidencias/04-jenkins-stages.png)

![Jenkins console](evidencias/05-jenkins-console.png)

![Docker Hub](evidencias/06-dockerhub-image.png)

> Reemplazar estas referencias únicamente con capturas reales.

## 6. Herramientas seleccionadas y justificación

| Herramienta | Función | Justificación técnica |
|---|---|---|
| Git / GitHub | Control de versiones y colaboración | Mantiene código, pipeline y documentación bajo una única historia de cambios. |
| GitHub Actions | CI | Se integra directamente con eventos `push` y `pull_request`, ofreciendo retroalimentación inmediata. |
| Pytest | Pruebas | Automatiza la validación funcional de la aplicación y puede bloquear el pipeline ante regresiones. |
| Ruff | Análisis estático | Introduce una validación de calidad rápida antes de construir artefactos. |
| Jenkins | CD | Permite modelar explícitamente stages de entrega mediante `Jenkinsfile` y conectar herramientas externas. |
| Docker | Empaquetado | Produce un artefacto portable y consistente para diferentes entornos. |
| Docker Hub | Registro | Centraliza y versiona las imágenes que serán consumidas en etapas posteriores. |
| Kubernetes | Destino agnóstico | Define el destino posterior mediante recursos declarativos independientes de un proveedor de nube específico. |

## 7. Relación con principios DevOps trabajados en clase

La implementación evidencia los tres caminos de DevOps. El **flujo** mejora al automatizar el paso desde código hasta un artefacto listo para entrega. La **retroalimentación** se acelera porque cada `push` o Pull Request recibe resultados automáticos de calidad y pruebas. El **aprendizaje continuo** se apoya en evidencias como cobertura, errores de lint, resultados de ejecución y logs de Jenkins.

También se aplica *X as Code*: el workflow, el Jenkinsfile, el Dockerfile y los manifiestos Kubernetes son archivos versionados, reproducibles y revisables. Esto reduce dependencia de configuraciones manuales y facilita que otro integrante o equipo comprenda cómo se ejecuta el proceso.

## 8. Seguridad y buenas prácticas

Aunque los conectores de seguridad se profundizarán en la siguiente fase del proyecto, este laboratorio incorpora controles básicos desde el diseño:

- Secretos fuera del repositorio mediante Jenkins Credentials.
- Permiso `contents: read` en GitHub Actions, siguiendo mínimo privilegio para el CI.
- Ejecución del contenedor con usuario no root.
- Etiqueta inmutable para trazabilidad.
- Healthcheck y smoke test antes de publicación.
- Quality gate de pruebas y análisis estático.



## 9. Conclusiones

Los dos pipelines conforman un flujo coherente y evolutivo. GitHub Actions actúa como puerta de calidad temprana y automática; Jenkins transforma el código en una imagen Docker versionada y preparada para Kubernetes. La solución evita acoplar el CD a un proveedor de nube específico, mantiene la configuración como código y produce ciclos cortos de retroalimentación. De esta manera, el laboratorio no se limita a cumplir una secuencia de comandos: demuestra principios de automatización, trazabilidad, reproducibilidad y colaboración propios de DevOps.


