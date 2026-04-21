# Kubescape Hardening Scan Report

**Generation date:** 2026-04-21 13:29:09

## Summary by resources

- `apps/v1/kafka/Deployment/kafka-1`: ✅ 23 / ❌ 5
- `apps/v1/kafka/Deployment/kafka-2`: ✅ 23 / ❌ 5
- `apps/v1/kafka/Deployment/kafka-operator`: ✅ 24 / ❌ 4
- `apps/v1/kafka/Deployment/kafka-integration-tests-runner`: ✅ 24 / ❌ 4
- `apps/v1/kafka/Deployment/kafka-backup-daemon`: ✅ 25 / ❌ 3
- `apps/v1/kafka/Deployment/kafka-service-operator`: ✅ 24 / ❌ 4
- `apps/v1/kafka/Deployment/akhq`: ✅ 24 / ❌ 4
- `apps/v1/kafka/Deployment/kafka-3`: ✅ 23 / ❌ 5

---

## Resource: `apps/v1/kafka/Deployment/kafka-1`

| ControlID | Control name | Status |
|-----------|--------------|--------|
| C-0030 | Ingress and Egress blocked | ❌ |
| C-0055 | Linux hardening | ✅ |
| C-0270 | Ensure CPU limits are set | ✅ |
| C-0056 | Configured liveness probe | ✅ |
| C-0061 | Pods in default namespace | ✅ |
| C-0075 | Image pull policy on latest tag | ✅ |
| C-0013 | Non-root containers | ❌ |
| C-0041 | HostNetwork access | ✅ |
| C-0269 | Ensure memory requests are set | ✅ |
| C-0044 | Container hostPort | ✅ |
| C-0292 | Nginx Ingress Controller End of Life | ✅ |
| C-0045 | Writable hostPath mount | ✅ |
| C-0076 | Label usage for resources | ❌ |
| C-0077 | K8s common labels usage | ✅ |
| C-0012 | Applications credentials in configuration files | ❌ |
| C-0016 | Allow privilege escalation | ✅ |
| C-0034 | Automatic mapping of service account | ✅ |
| C-0271 | Ensure memory limits are set | ✅ |
| C-0014 | Access Kubernetes dashboard | ✅ |
| C-0038 | Host PID/IPC privileges | ✅ |
| C-0057 | Privileged container | ✅ |
| C-0020 | Mount service principal | ✅ |
| C-0017 | Immutable container filesystem | ❌ |
| C-0046 | Insecure capabilities | ✅ |
| C-0048 | HostPath mount | ✅ |
| C-0018 | Configured readiness probe | ✅ |
| C-0074 | Container runtime socket mounted | ✅ |
| C-0268 | Ensure CPU requests are set | ✅ |

**Total:** ✅ passed: 23, ❌ failed: 5

---

## Resource: `apps/v1/kafka/Deployment/kafka-2`

| ControlID | Control name | Status |
|-----------|--------------|--------|
| C-0030 | Ingress and Egress blocked | ❌ |
| C-0055 | Linux hardening | ✅ |
| C-0270 | Ensure CPU limits are set | ✅ |
| C-0056 | Configured liveness probe | ✅ |
| C-0061 | Pods in default namespace | ✅ |
| C-0075 | Image pull policy on latest tag | ✅ |
| C-0013 | Non-root containers | ❌ |
| C-0041 | HostNetwork access | ✅ |
| C-0269 | Ensure memory requests are set | ✅ |
| C-0044 | Container hostPort | ✅ |
| C-0292 | Nginx Ingress Controller End of Life | ✅ |
| C-0045 | Writable hostPath mount | ✅ |
| C-0076 | Label usage for resources | ❌ |
| C-0077 | K8s common labels usage | ✅ |
| C-0012 | Applications credentials in configuration files | ❌ |
| C-0016 | Allow privilege escalation | ✅ |
| C-0034 | Automatic mapping of service account | ✅ |
| C-0271 | Ensure memory limits are set | ✅ |
| C-0014 | Access Kubernetes dashboard | ✅ |
| C-0038 | Host PID/IPC privileges | ✅ |
| C-0057 | Privileged container | ✅ |
| C-0020 | Mount service principal | ✅ |
| C-0017 | Immutable container filesystem | ❌ |
| C-0046 | Insecure capabilities | ✅ |
| C-0048 | HostPath mount | ✅ |
| C-0018 | Configured readiness probe | ✅ |
| C-0074 | Container runtime socket mounted | ✅ |
| C-0268 | Ensure CPU requests are set | ✅ |

**Total:** ✅ passed: 23, ❌ failed: 5

---

## Resource: `apps/v1/kafka/Deployment/kafka-operator`

| ControlID | Control name | Status |
|-----------|--------------|--------|
| C-0030 | Ingress and Egress blocked | ❌ |
| C-0055 | Linux hardening | ✅ |
| C-0270 | Ensure CPU limits are set | ✅ |
| C-0056 | Configured liveness probe | ✅ |
| C-0061 | Pods in default namespace | ✅ |
| C-0075 | Image pull policy on latest tag | ✅ |
| C-0013 | Non-root containers | ❌ |
| C-0041 | HostNetwork access | ✅ |
| C-0269 | Ensure memory requests are set | ✅ |
| C-0044 | Container hostPort | ✅ |
| C-0292 | Nginx Ingress Controller End of Life | ✅ |
| C-0045 | Writable hostPath mount | ✅ |
| C-0076 | Label usage for resources | ❌ |
| C-0077 | K8s common labels usage | ✅ |
| C-0012 | Applications credentials in configuration files | ✅ |
| C-0016 | Allow privilege escalation | ✅ |
| C-0034 | Automatic mapping of service account | ✅ |
| C-0271 | Ensure memory limits are set | ✅ |
| C-0014 | Access Kubernetes dashboard | ✅ |
| C-0038 | Host PID/IPC privileges | ✅ |
| C-0057 | Privileged container | ✅ |
| C-0020 | Mount service principal | ✅ |
| C-0017 | Immutable container filesystem | ❌ |
| C-0046 | Insecure capabilities | ✅ |
| C-0048 | HostPath mount | ✅ |
| C-0018 | Configured readiness probe | ✅ |
| C-0074 | Container runtime socket mounted | ✅ |
| C-0268 | Ensure CPU requests are set | ✅ |

**Total:** ✅ passed: 24, ❌ failed: 4

---

## Resource: `apps/v1/kafka/Deployment/kafka-integration-tests-runner`

| ControlID | Control name | Status |
|-----------|--------------|--------|
| C-0030 | Ingress and Egress blocked | ❌ |
| C-0055 | Linux hardening | ✅ |
| C-0270 | Ensure CPU limits are set | ✅ |
| C-0056 | Configured liveness probe | ✅ |
| C-0061 | Pods in default namespace | ✅ |
| C-0075 | Image pull policy on latest tag | ✅ |
| C-0013 | Non-root containers | ❌ |
| C-0041 | HostNetwork access | ✅ |
| C-0269 | Ensure memory requests are set | ✅ |
| C-0044 | Container hostPort | ✅ |
| C-0292 | Nginx Ingress Controller End of Life | ✅ |
| C-0045 | Writable hostPath mount | ✅ |
| C-0076 | Label usage for resources | ❌ |
| C-0077 | K8s common labels usage | ✅ |
| C-0012 | Applications credentials in configuration files | ✅ |
| C-0016 | Allow privilege escalation | ✅ |
| C-0034 | Automatic mapping of service account | ✅ |
| C-0271 | Ensure memory limits are set | ✅ |
| C-0014 | Access Kubernetes dashboard | ✅ |
| C-0038 | Host PID/IPC privileges | ✅ |
| C-0057 | Privileged container | ✅ |
| C-0020 | Mount service principal | ✅ |
| C-0017 | Immutable container filesystem | ❌ |
| C-0046 | Insecure capabilities | ✅ |
| C-0048 | HostPath mount | ✅ |
| C-0018 | Configured readiness probe | ✅ |
| C-0074 | Container runtime socket mounted | ✅ |
| C-0268 | Ensure CPU requests are set | ✅ |

**Total:** ✅ passed: 24, ❌ failed: 4

---

## Resource: `apps/v1/kafka/Deployment/kafka-backup-daemon`

| ControlID | Control name | Status |
|-----------|--------------|--------|
| C-0030 | Ingress and Egress blocked | ❌ |
| C-0055 | Linux hardening | ✅ |
| C-0270 | Ensure CPU limits are set | ✅ |
| C-0056 | Configured liveness probe | ✅ |
| C-0061 | Pods in default namespace | ✅ |
| C-0075 | Image pull policy on latest tag | ✅ |
| C-0013 | Non-root containers | ✅ |
| C-0041 | HostNetwork access | ✅ |
| C-0269 | Ensure memory requests are set | ✅ |
| C-0044 | Container hostPort | ✅ |
| C-0292 | Nginx Ingress Controller End of Life | ✅ |
| C-0045 | Writable hostPath mount | ✅ |
| C-0076 | Label usage for resources | ❌ |
| C-0077 | K8s common labels usage | ✅ |
| C-0012 | Applications credentials in configuration files | ✅ |
| C-0016 | Allow privilege escalation | ✅ |
| C-0034 | Automatic mapping of service account | ✅ |
| C-0271 | Ensure memory limits are set | ✅ |
| C-0014 | Access Kubernetes dashboard | ✅ |
| C-0038 | Host PID/IPC privileges | ✅ |
| C-0057 | Privileged container | ✅ |
| C-0020 | Mount service principal | ✅ |
| C-0017 | Immutable container filesystem | ❌ |
| C-0046 | Insecure capabilities | ✅ |
| C-0048 | HostPath mount | ✅ |
| C-0018 | Configured readiness probe | ✅ |
| C-0074 | Container runtime socket mounted | ✅ |
| C-0268 | Ensure CPU requests are set | ✅ |

**Total:** ✅ passed: 25, ❌ failed: 3

---

## Resource: `apps/v1/kafka/Deployment/kafka-service-operator`

| ControlID | Control name | Status |
|-----------|--------------|--------|
| C-0030 | Ingress and Egress blocked | ❌ |
| C-0055 | Linux hardening | ✅ |
| C-0270 | Ensure CPU limits are set | ✅ |
| C-0056 | Configured liveness probe | ✅ |
| C-0061 | Pods in default namespace | ✅ |
| C-0075 | Image pull policy on latest tag | ✅ |
| C-0013 | Non-root containers | ❌ |
| C-0041 | HostNetwork access | ✅ |
| C-0269 | Ensure memory requests are set | ✅ |
| C-0044 | Container hostPort | ✅ |
| C-0292 | Nginx Ingress Controller End of Life | ✅ |
| C-0045 | Writable hostPath mount | ✅ |
| C-0076 | Label usage for resources | ❌ |
| C-0077 | K8s common labels usage | ✅ |
| C-0012 | Applications credentials in configuration files | ✅ |
| C-0016 | Allow privilege escalation | ✅ |
| C-0034 | Automatic mapping of service account | ✅ |
| C-0271 | Ensure memory limits are set | ✅ |
| C-0014 | Access Kubernetes dashboard | ✅ |
| C-0038 | Host PID/IPC privileges | ✅ |
| C-0057 | Privileged container | ✅ |
| C-0020 | Mount service principal | ✅ |
| C-0017 | Immutable container filesystem | ❌ |
| C-0046 | Insecure capabilities | ✅ |
| C-0048 | HostPath mount | ✅ |
| C-0018 | Configured readiness probe | ✅ |
| C-0074 | Container runtime socket mounted | ✅ |
| C-0268 | Ensure CPU requests are set | ✅ |

**Total:** ✅ passed: 24, ❌ failed: 4

---

## Resource: `apps/v1/kafka/Deployment/akhq`

| ControlID | Control name | Status |
|-----------|--------------|--------|
| C-0030 | Ingress and Egress blocked | ❌ |
| C-0055 | Linux hardening | ✅ |
| C-0270 | Ensure CPU limits are set | ✅ |
| C-0056 | Configured liveness probe | ✅ |
| C-0061 | Pods in default namespace | ✅ |
| C-0075 | Image pull policy on latest tag | ✅ |
| C-0013 | Non-root containers | ❌ |
| C-0041 | HostNetwork access | ✅ |
| C-0269 | Ensure memory requests are set | ✅ |
| C-0044 | Container hostPort | ✅ |
| C-0292 | Nginx Ingress Controller End of Life | ✅ |
| C-0045 | Writable hostPath mount | ✅ |
| C-0076 | Label usage for resources | ❌ |
| C-0077 | K8s common labels usage | ✅ |
| C-0012 | Applications credentials in configuration files | ✅ |
| C-0016 | Allow privilege escalation | ✅ |
| C-0034 | Automatic mapping of service account | ✅ |
| C-0271 | Ensure memory limits are set | ✅ |
| C-0014 | Access Kubernetes dashboard | ✅ |
| C-0038 | Host PID/IPC privileges | ✅ |
| C-0057 | Privileged container | ✅ |
| C-0020 | Mount service principal | ✅ |
| C-0017 | Immutable container filesystem | ❌ |
| C-0046 | Insecure capabilities | ✅ |
| C-0048 | HostPath mount | ✅ |
| C-0018 | Configured readiness probe | ✅ |
| C-0074 | Container runtime socket mounted | ✅ |
| C-0268 | Ensure CPU requests are set | ✅ |

**Total:** ✅ passed: 24, ❌ failed: 4

---

## Resource: `apps/v1/kafka/Deployment/kafka-3`

| ControlID | Control name | Status |
|-----------|--------------|--------|
| C-0030 | Ingress and Egress blocked | ❌ |
| C-0055 | Linux hardening | ✅ |
| C-0270 | Ensure CPU limits are set | ✅ |
| C-0056 | Configured liveness probe | ✅ |
| C-0061 | Pods in default namespace | ✅ |
| C-0075 | Image pull policy on latest tag | ✅ |
| C-0013 | Non-root containers | ❌ |
| C-0041 | HostNetwork access | ✅ |
| C-0269 | Ensure memory requests are set | ✅ |
| C-0044 | Container hostPort | ✅ |
| C-0292 | Nginx Ingress Controller End of Life | ✅ |
| C-0045 | Writable hostPath mount | ✅ |
| C-0076 | Label usage for resources | ❌ |
| C-0077 | K8s common labels usage | ✅ |
| C-0012 | Applications credentials in configuration files | ❌ |
| C-0016 | Allow privilege escalation | ✅ |
| C-0034 | Automatic mapping of service account | ✅ |
| C-0271 | Ensure memory limits are set | ✅ |
| C-0014 | Access Kubernetes dashboard | ✅ |
| C-0038 | Host PID/IPC privileges | ✅ |
| C-0057 | Privileged container | ✅ |
| C-0020 | Mount service principal | ✅ |
| C-0017 | Immutable container filesystem | ❌ |
| C-0046 | Insecure capabilities | ✅ |
| C-0048 | HostPath mount | ✅ |
| C-0018 | Configured readiness probe | ✅ |
| C-0074 | Container runtime socket mounted | ✅ |
| C-0268 | Ensure CPU requests are set | ✅ |

**Total:** ✅ passed: 23, ❌ failed: 5

---