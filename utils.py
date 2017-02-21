#/usr/bin/python3

"""Kubernetes API access functions"""

from kubernetes import client, config
import logging

scale_logger = logging.getLogger("scale")
logging.getLogger("kubernetes").setLevel(logging.WARNING)
config.load_kube_config()
v1 = client.CoreV1Api()


def get_nodes():
    """Return a list of v1.Node"""
    scale_logger.debug("Getting all nodes in the cluster")
    return v1.list_node().items


def get_pods():
    """Return a list of v1.Pod"""
    scale_logger.debug("Getting all pods in all namespaces")
    return v1.list_pod_for_all_namespaces().items


def get_pod_host_name(pod):
    """Return the host node name of the pod"""
    # Based on Kubernetes API:
    # https://kubernetes.io/docs/api-reference/v1/definitions/#_v1_podspec
    # ** API is unclear the value of nodeName flag after the pod is scheduled
    return pod.spec.node_name


def get_cluster_name(node=None):
    """Return the (guessed) name of the cluster"""
    if node == None:
        node = get_nodes()[0]
    node_name = node.metadata.name
    parts = node_name.split('-')
    assert len(parts) > 2
    return parts[1]


def get_pod_type(pod):
    """Return the Type of the pod"""
    # TODO: May not be the best approach
    return pod.metadata.name.split('-')[0]


def set_unschedulable(node_name, value=True):
    """Set the spec key 'unschedulable'"""
    scale_logger.debug(
        "Setting %s node's unschedulable property to %r" % (node_name, value))
    new_node = client.V1Node(
        api_version="v1",
        kind="Node",
        metadata=client.V1ObjectMeta(name=node_name),
        spec=client.V1NodeSpec(unschedulable=value)
    )
    # TODO: exception handling
    v1.patch_node(node_name, new_node)
