# Data Model: Local Kubernetes AI Operations (AIOps)

## Local Kubernetes Cluster

**Entity**: LocalCluster
- **Fields**:
  - name: String (cluster identifier)
  - provider: String (minikube, kind, docker-desktop)
  - status: Enum (running, stopped, error)
  - nodes: Integer (number of nodes in cluster)
  - k8s_version: String (Kubernetes version)
  - addons: Array<String> (enabled Kubernetes addons)

**Validation rules**:
- name must be unique within the host system
- provider must be one of the supported local providers
- nodes must be between 1 and 10 for local environments

## Kubernetes Resources

**Entity**: K8sResource
- **Fields**:
  - kind: String (Deployment, Service, ConfigMap, etc.)
  - name: String (resource name)
  - namespace: String (Kubernetes namespace)
  - manifest: Object (raw Kubernetes manifest)
  - status: String (active, failed, pending)

**Validation rules**:
- name must follow Kubernetes naming conventions
- namespace must exist before resource creation
- manifest must be valid Kubernetes YAML

## Container Image

**Entity**: ContainerImage
- **Fields**:
  - name: String (image name)
  - tag: String (version tag)
  - registry: String (registry URL)
  - build_context: String (path to Dockerfile)
  - dockerfile_path: String (path to Dockerfile)

**Validation rules**:
- name must follow Docker image naming conventions
- build_context must be a valid directory path
- dockerfile_path must point to an existing Dockerfile

## Helm Chart

**Entity**: HelmChart
- **Fields**:
  - name: String (chart name)
  - version: String (chart version)
  - repository: String (chart repository URL)
  - values: Object (configuration values)
  - release_name: String (installation name)

**Validation rules**:
- name must follow Helm chart naming conventions
- version must follow semantic versioning
- values must conform to chart schema if provided

## Verification Result

**Entity**: VerificationResult
- **Fields**:
  - test_name: String (name of the verification test)
  - status: Enum (pass, fail, error)
  - timestamp: DateTime (when test was run)
  - details: String (additional information about the result)
  - resource_ref: String (reference to the resource being verified)

**Validation rules**:
- test_name must be unique for each verification run
- status must be one of the defined enum values
- timestamp must be in ISO 8601 format