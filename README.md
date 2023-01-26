OpenShift Virtualization With Nvidia vGPU
====

Ansible playbooks for deploying a ready-to-use Nvidia GPU operator with vGPU support for Openshift Virtualization 


# Pre-requisites

* An Openshift Cluster with Virtualization. 
* Nvidia vGPU Software from NVIDIA Licensing Portal. more information found in the [Nvidia Documentation](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/openshift/openshift-virtualization.html#building-the-vgpu-manager-image)
*  python3.8+ with [Virtualenv module](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/)


# How To Deploy
1. Create a variables file form `example-varts.yaml` as `vars.yaml`
2. Update needed values
```yaml
# vars.yaml
### Cluster KUBECONFIG path
KUBECONFIG: "path/to/kubeconfig"

# Downloaded vGPU software
DRIVER_FILE_PATH: "path/to/NVIDIA-Linux-x86_64-< version >-vgpu-kvm.run"

### private registry where the vgpu image will be pushed/pulled from
PRIVATE_REGISTRY: "myregistry.com/userspace"
PRIVATE_REGISTRY_USER: "username"
PRIVATE_REGISTRY_KEY:  "VerySecretPassword"
```
3. Run playbook
```console
make deploy-all
```

