pipeline {
  agent any
  parameters {
    choice(name: 'DEPLOY_SLOT', choices: ['green', 'blue'], description: 'Which slot to deploy to?')
  }
  environment {
    IMAGE = "myapp:${params.DEPLOY_SLOT}"
  }
  stages {
    stage('Checkout') {
      steps { checkout scm }
    }
    stage('Build') {
      steps {
        sh "docker build -t ${IMAGE} --build-arg ENV=${params.DEPLOY_SLOT} ."
      }
    }
    stage('Test') {
      steps {
        sh """
          docker run --rm -d --name test_${params.DEPLOY_SLOT} \
            -e APP_ENV=${params.DEPLOY_SLOT} ${IMAGE}
          sleep 5
          TEST_IP=\$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' test_${params.DEPLOY_SLOT})
          curl -f http://\$TEST_IP:8080/health || (docker stop test_${params.DEPLOY_SLOT} && exit 1)
          docker stop test_${params.DEPLOY_SLOT}
        """
      }
    }
    stage('Deploy to Slot') {
      steps {
        sh "kubectl apply -f k8s/${params.DEPLOY_SLOT}.yaml"
        sh "kubectl rollout status deployment/myapp-${params.DEPLOY_SLOT} --timeout=90s"
      }
    }
    stage('Health Check') {
      steps {
        sh """
          POD=\$(kubectl get pod -l env=${params.DEPLOY_SLOT} -o jsonpath='{.items[0].metadata.name}')
          echo "Checking pod: \$POD"
          kubectl exec \$POD -- python3 -c "import urllib.request; r=urllib.request.urlopen('http://localhost:8080/health'); print(r.read())"
          echo "Health check passed!"
        """
      }
    }
    stage('Switch Traffic') {
      steps {
        input message: "Switch live traffic to ${params.DEPLOY_SLOT}?", ok: 'Switch now!'
        sh """
          kubectl patch service myapp-main \
            -p '{"spec":{"selector":{"env":"${params.DEPLOY_SLOT}"}}}'
          echo "Traffic switched to ${params.DEPLOY_SLOT}"
        """
      }
    }
  }
  post {
    success { echo "Blue-Green deployment to ${params.DEPLOY_SLOT} successful!" }
    failure {
      script {
        def prev = params.DEPLOY_SLOT == 'green' ? 'blue' : 'green'
        sh "kubectl patch service myapp-main -p '{\"spec\":{\"selector\":{\"env\":\"${prev}\"}}}' || true"
        echo "Rolled back to ${prev}"
      }
    }
  }
}
