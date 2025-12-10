# Deployment strategy

## Considerations

### Security

- Input validation and sanitization
- Implement RBAC access controls for API access (AI API Gateway solution)
- Authz and Authn for user facing applications
- Implement IAM based access policies for different model end-points
- Rate limits
- Implement Guardrails for different agents
- Vulnerability scans

### Observability and Monitoring

- Infrastructure monitoring and alerts
  - Cost and Token usage
  - Error rate and latency
- Model monitoring
  - Model metrics like accuracy, hallucination and groundedness
  - Online and Offline evaluations
  - Feedback loop with Human in the loop
  - LLM as Judge
  - Prompt tuning

### Cost optimization

- Cache prompts and frequent requests
- Batch or Asynchronous calls
- Chunking strategies
- Use cheaper models where applicable (Gemini Flash, Gemini Flash Lite etc.)

### Reliability

- API Gateway and AI Gateway
- Retry mechanisms
- Error handling
- Self healing and graceful recovery
- Multi stage CI pipeline to trigger automated unit tests and integration tests
- Auto scaling policies for application deployment
  - K8s node groups
  - K8s Horizontal pod scaling and Vertical pod scaling
  - K8s scaling frameworks - Serverless (KServe) or Event based (KEDA)
  - K8s GitOps strategy using ArgoCD to automate deployments.
- Multi-region and multi zone deployments
- Provisioned throughput

## Docker and K8s setup

### Docker

#### 1. **Docker build**

- Docker build

  ```bash
  docker build -t multi-agent-pipeline:latest .
  ```

- Tag the image for your ECR repository:

  ```bash
  docker tag multi-agent-pipeline:latest <your-account-id>.dkr.ecr.<region>.amazonaws.com/multi-agent-pipeline:latest
  ```

#### 2. **Docker push**

- Authenticate Docker with ECR:

  ```bash
  aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <your-account-id>.dkr.ecr.<region>.amazonaws.com
  ```

- Push the image to ECR:

  ```bash
  docker push <your-account-id>.dkr.ecr.<region>.amazonaws.com/multi-agent-pipeline:latest
  ```

### K8s

#### 3. **Create Kubernetes Deployment**

- Create a `deployment.yaml` file:

  ```yaml
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: multi-agent-pipeline
    labels:
      app: multi-agent-pipeline
  spec:
    replicas: 2
    selector:
      matchLabels:
        app: multi-agent-pipeline
    template:
      metadata:
        labels:
          app: multi-agent-pipeline
      spec:
        containers:
        - name: multi-agent-pipeline
          image: <your-account-id>.dkr.ecr.<region>.amazonaws.com/multi-agent-pipeline:latest
          ports:
          - containerPort: 8061
          env:
          - name: GEMINI_MODEL_FLASH
            value: "your_gemini_flash_model"
          - name: GEMINI_MODEL_PRO
            value: "your_gemini_pro_model"
  ```

#### 4. **Create Kubernetes Service**

- Create a `service.yaml` file:

  ```yaml
  apiVersion: v1
  kind: Service
  metadata:
    name: multi-agent-pipeline-service
  spec:
    type: LoadBalancer
    selector:
      app: multi-agent-pipeline
    ports:
    - protocol: TCP
      port: 80
      targetPort: 8061
  ```

#### 5. **Apply Kubernetes Resources**

- Apply the deployment and service:

  ```bash
  kubectl apply -f deployment.yaml
  kubectl apply -f service.yaml
  ```

#### 6. **Access the Application**

- Wait for the LoadBalancer to be provisioned:

  ```bash
  kubectl get services
  ```

- Note the `EXTERNAL-IP` of the `multi-agent-pipeline-service` and access the application at `http://<EXTERNAL-IP>`.

#### 7. **Verify Deployment**

- Check the status of the pods:

  ```bash
  kubectl get pods
  ```

- Check the logs of a pod:

  ```bash
  kubectl logs <pod-name>
  ```

#### 8. **Cleanup**

  ```bash
  kubectl delete service multi-agent-pipeline-service
  kubectl delete deployment multi-agent-pipeline
  ```
