pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 20, unit: 'MINUTES')
    }

    parameters {
    string(
        name: 'DOCKERHUB_NAMESPACE',
        defaultValue: 'victorc901202',
        description: 'Usuario u organización de Docker Hub'
    )
    string(
        name: 'DOCKERHUB_REPOSITORY',
        defaultValue: 'devops-web-lab',
        description: 'Repositorio de imágenes en Docker Hub'
    )
    booleanParam(
        name: 'DEPLOY_TO_K8S',
        defaultValue: false,
        description: 'Fase opcional para el siguiente laboratorio: desplegar en Kubernetes'
    )
}

    environment {
        LOCAL_IMAGE = 'devops-web-lab'
        DOCKERHUB_CREDENTIALS_ID = 'dockerhub-credentials'
    }

    stages {
        stage('1. Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_SHORT = sh(
                        script: 'git rev-parse --short=7 HEAD',
                        returnStdout: true
                    ).trim()
                    env.IMAGE_TAG = "${env.BUILD_NUMBER}-${env.GIT_SHORT}"
                    env.REMOTE_IMAGE = "${params.DOCKERHUB_NAMESPACE}/${params.DOCKERHUB_REPOSITORY}"
                }
            }
        }

        stage('2. Validate Definition') {
            steps {
                sh '''
                    test -f Dockerfile
                    test -f k8s/deployment.yaml
                    test -f k8s/service.yaml
                    test -f .github/workflows/ci.yml
                '''
            }
        }

        stage('3. Build Docker Image') {
            steps {
                sh 'docker build --pull -t ${LOCAL_IMAGE}:${BUILD_NUMBER} .'
            }
        }

        stage('4. Smoke Test Container') {
    steps {
        sh '''
            set -eu
            CONTAINER_ID=$(docker run -d -p 18000:8000 ${LOCAL_IMAGE}:${BUILD_NUMBER})
            trap 'docker rm -f "$CONTAINER_ID" >/dev/null 2>&1 || true' EXIT

            i=0
            until curl -fsS http://docker:18000/health >/dev/null; do
                i=$((i + 1))
                if [ "$i" -ge 20 ]; then
                    docker logs "$CONTAINER_ID" || true
                    exit 1
                fi
                sleep 1
            done

            curl -fsS http://docker:18000/health
        '''
    }
}

        stage('5. Publish to Docker Hub') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: env.DOCKERHUB_CREDENTIALS_ID,
                        usernameVariable: 'DOCKERHUB_USER',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        set -eu
                        echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USER" --password-stdin

                        docker tag ${LOCAL_IMAGE}:${BUILD_NUMBER} ${REMOTE_IMAGE}:${IMAGE_TAG}
                        docker push ${REMOTE_IMAGE}:${IMAGE_TAG}

                        case "${BRANCH_NAME:-${GIT_BRANCH:-}}" in
                            main|origin/main)
                                docker tag ${LOCAL_IMAGE}:${BUILD_NUMBER} ${REMOTE_IMAGE}:latest
                                docker push ${REMOTE_IMAGE}:latest
                                ;;
                        esac
                    '''
                }
            }
        }

        stage('6. Prepare Kubernetes Manifest') {
            steps {
                sh '''
                    mkdir -p build
                    sed "s#IMAGE_PLACEHOLDER#${REMOTE_IMAGE}:${IMAGE_TAG}#g" \
                        k8s/deployment.yaml > build/deployment-${IMAGE_TAG}.yaml
                    cp k8s/service.yaml build/service.yaml
                    echo "Artefacto listo para CD: ${REMOTE_IMAGE}:${IMAGE_TAG}"
                '''
                archiveArtifacts artifacts: 'build/*.yaml', fingerprint: true
            }
        }

        stage('7. Deploy to Kubernetes - Optional') {
            when {
                expression { return params.DEPLOY_TO_K8S }
            }
            steps {
                withCredentials([
                    file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')
                ]) {
                    sh '''
                        kubectl apply -f build/deployment-${IMAGE_TAG}.yaml
                        kubectl apply -f build/service.yaml
                        kubectl rollout status deployment/devops-web-lab --timeout=120s
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "CD finalizado. Imagen publicada: ${env.REMOTE_IMAGE}:${env.IMAGE_TAG}"
        }
        failure {
            echo 'El pipeline falló. Revisar el stage y la consola para retroalimentación rápida.'
        }
        always {
            sh 'docker logout >/dev/null 2>&1 || true'
        }
    }
}
