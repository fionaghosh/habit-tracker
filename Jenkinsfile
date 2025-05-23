pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "fionaghosh/habit-tracker:${env.BUILD_NUMBER}"
        REGISTRY     = "docker.io"
        APP_NAME     = "habit-tracker"
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Build') {
            steps {
                sh "docker build -t ${DOCKER_IMAGE} ."
            }
        }
        stage('Test') {
            steps {
                sh "docker run --rm ${DOCKER_IMAGE} pytest -q tests"
            }
        }
        stage('Code Quality') {
            steps {
                sh "docker run --rm ${DOCKER_IMAGE} flake8 ."
                sh "docker run --rm ${DOCKER_IMAGE} flake8 --format=html --htmldir=flake-report ."
                archiveArtifacts 'flake-report/**/*'
            }
        }
        stage('Security Scan') {
            steps {
                sh "docker run --rm ${DOCKER_IMAGE} bandit -r . -f html -o bandit-report.html"
                archiveArtifacts 'bandit-report.html'
            }
        }
        stage('Release') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKERHUB_USER',
                    passwordVariable: 'DOCKERHUB_PASS'
                )]) {
                    sh "docker login -u $DOCKERHUB_USER -p $DOCKERHUB_PASS ${REGISTRY}"
                    sh "docker tag ${DOCKER_IMAGE} ${REGISTRY}/${DOCKER_IMAGE}"
                    sh "docker push ${REGISTRY}/${DOCKER_IMAGE}"
                }
            }
        }
        stage('Deploy') {
            steps {
                sh """
                  ssh deploy@your-server \\
                    'docker pull ${REGISTRY}/${DOCKER_IMAGE} && \\
                     docker rm -f ${APP_NAME} || true && \\
                     docker run -d --name ${APP_NAME} -p 8000:8000 ${REGISTRY}/${DOCKER_IMAGE}'
                """
            }
        }
        stage('Monitoring') {
            steps {
                sh "curl -sf http://your-server:8000/healthz || exit 1"
                sh "curl http://your-server:8000/metrics > metrics_snapshot.txt"
                archiveArtifacts 'metrics_snapshot.txt'
            }
        }
    }

    post {
        success { echo "🎉 Build ${env.BUILD_NUMBER} succeeded!" }
        failure { echo "❌ Build ${env.BUILD_NUMBER} failed." }
    }
}
