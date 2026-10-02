"""Explicit package-resource navigation and instance creation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from . import graph_authoring as api
from .graph_inspection import checked_graph, graph_identity, page


def _package(path: str):
    resolved = api._sbs_path(path, must_exist=True)
    found = api.package_manager().getUserPackageFromFilePath(str(resolved))
    if found is None:
        raise api.GraphAuthoringError("Open the requested package first", "PACKAGE_NOT_OPEN")
    return found


def list_resources(package_path: str, offset: int = 0, limit: int = 100) -> dict[str, Any]:
    page([], offset, limit)
    package = _package(package_path)
    rows = [
        {
            "resource_url": resource.getUrl(),
            "identifier": resource.getIdentifier(),
            "type_id": api.value(resource.getType(), "getId"),
            "embed_method": str(getattr(resource.getEmbedMethod(), "name", resource.getEmbedMethod())),
        }
        for resource in api.items(package.getChildrenResources(True))
    ]
    return {"package_path": api.package_path(package), **page(rows, offset, limit)}


def _resource(package: Any, resource_url: str) -> Any:
    if not isinstance(resource_url, str) or not resource_url or len(resource_url) > 1024:
        raise api.GraphAuthoringError("resource_url must be a bounded nonempty string", "INVALID_RESOURCE_URL")
    resource = package.findResourceFromUrl(resource_url)
    if resource is None:
        raise api.GraphAuthoringError("Resource was not found in the selected package", "RESOURCE_NOT_FOUND")
    return resource


def select_graph(package_path: str, resource_url: str) -> dict[str, str]:
    from sd.api.sdgraph import SDGraph

    graph = _resource(_package(package_path), resource_url)
    if not isinstance(graph, SDGraph):
        raise api.GraphAuthoringError("Resource is not a graph", "RESOURCE_NOT_GRAPH")
    uid = graph_identity(graph)
    api.application().getUIMgr().openResourceInEditor(graph)
    if graph_identity(api.active_graph()) != uid:
        raise api.GraphAuthoringError("Graph selection readback failed", "GRAPH_SELECTION_FAILED")
    return {"graph_uid": uid, "resource_url": graph.getUrl()}


def create_subgraph(graph_id: str, expected_graph_uid: str) -> dict[str, str]:
    from sd.api.sbs.sdsbscompgraph import SDSBSCompGraph

    graph = checked_graph(expected_graph_uid)
    package = graph.getPackage()
    identifier = api.require_identifier(graph_id, "graph_id")
    if any(resource.getIdentifier() == identifier for resource in api.items(package.getChildrenResources(True))):
        raise api.GraphAuthoringError("Resource identifier already exists", "DUPLICATE_RESOURCE_ID")
    resource = SDSBSCompGraph.sNew(package)
    try:
        resource.setIdentifier(identifier)
        return {"resource_url": resource.getUrl(), "graph_uid": graph_identity(resource)}
    except BaseException:
        resource.delete()
        raise


def instance_resource(package_path: str, resource_url: str, expected_graph_uid: str) -> dict[str, str]:
    from sd.api.sdgraph import SDGraph

    graph = checked_graph(expected_graph_uid)
    resource = _resource(_package(package_path), resource_url)
    # Walk referenced graphs before instancing: direct and indirect recursion fail.
    pending, seen = [resource], set()
    while pending:
        current = pending.pop()
        if not isinstance(current, SDGraph):
            continue
        uid = graph_identity(current)
        if uid == expected_graph_uid:
            raise api.GraphAuthoringError("Graph instances would be recursive", "GRAPH_RECURSION")
        if uid not in seen:
            seen.add(uid)
            pending.extend(node.getReferencedResource() for node in api.items(current.getNodes()))
    node = graph.newInstanceNode(resource)
    if node is None:
        raise api.GraphAuthoringError("Resource cannot be instanced in this graph", "RESOURCE_INSTANCE_FAILED")
    return {"graph_uid": expected_graph_uid, "node_id": api.node_identifier(node), "resource_url": resource.getUrl()}


def open_package(path: str) -> dict[str, Any]:
    resolved = api._sbs_path(path, must_exist=True)
    manager = api.package_manager()
    package = manager.getUserPackageFromFilePath(str(resolved))
    if package is not None:
        # Never reload an already open package and discard unsaved edits.
        return {"package_path": str(resolved), "saved": not package.isModified(), "already_open": True}
    package = manager.loadUserPackage(str(resolved), True, False)
    if package is None or Path(package.getFilePath()).resolve() != resolved:
        raise api.GraphAuthoringError("Package open readback failed", "PACKAGE_OPEN_FAILED")
    return {"package_path": str(resolved), "saved": not package.isModified(), "already_open": False}


def describe_shipped_resource_properties(package_name: str, resource_id: str) -> dict[str, Any]:
    """Describe exact native edge properties of one shipped resource instance.

    Inspection for preflight: reports native isConnectable(), isReadOnly(),
    and property types for every instance input/output as the Designer SDK
    would expose them on a created node. The production graph and its package
    are never touched: the resource is instanced once in an isolated temporary
    package/graph that is deleted and unloaded before return. Shipped packages
    only, mirroring create_resource_node identity rules. Non-graph resources
    fail closed.
    """
    import re

    from sd.api.sdproperty import SDPropertyCategory

    from .graph_inspection import describe_property

    if not isinstance(package_name, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,128}\.sbs", package_name):
        raise api.GraphAuthoringError("Expected a shipped .sbs package filename", "INVALID_PACKAGE_NAME")
    resource_id = api.require_identifier(resource_id, "resource_id")
    app = api.application()
    from sd.api.sdapplication import SDApplicationPath
    from sd.api.sbs.sdsbscompgraph import SDSBSCompGraph
    from sd.api.sdgraph import SDGraph

    root = (Path(app.getPath(SDApplicationPath.DefaultResourcesDir)) / "packages").resolve()
    path = (root / package_name).resolve()
    if path.parent != root or not path.is_file():
        raise api.GraphAuthoringError("Shipped resource package not found", "RESOURCE_NOT_FOUND")
    package = app.getPackageMgr().loadUserPackage(str(path), True)
    if package is None:
        raise api.GraphAuthoringError("Shipped resource package not found", "RESOURCE_NOT_FOUND")
    resource = package.findResourceFromUrl(resource_id)
    if resource is None:
        for candidate in api.items(package.getChildrenResources(True)):
            try:
                if candidate.getIdentifier() == resource_id:
                    resource = candidate
                    break
            except Exception:
                continue
    if resource is None:
        raise api.GraphAuthoringError("Resource identifier not found in package", "RESOURCE_NOT_FOUND")
    if not isinstance(resource, SDGraph):
        raise api.GraphAuthoringError("Resource is not a graph", "RESOURCE_NOT_GRAPH")
    temp_package = app.getPackageMgr().newUserPackage()
    if temp_package is None:
        raise api.GraphAuthoringError("Designer could not create an inspection package", "PACKAGE_CREATE_FAILED")
    temp_graph = None
    node = None
    try:
        temp_graph = SDSBSCompGraph.sNew(temp_package)
        if temp_graph is None:
            raise api.GraphAuthoringError("Designer could not create an inspection graph", "GRAPH_CREATE_FAILED")
        node = temp_graph.newInstanceNode(resource)
        if node is None:
            raise api.GraphAuthoringError("Designer rejected resource instance", "NODE_TYPE_UNAVAILABLE")
        inputs = [describe_property(prop) for prop in api.items(node.getProperties(SDPropertyCategory.Input))]
        outputs = [describe_property(prop) for prop in api.items(node.getProperties(SDPropertyCategory.Output))]
        if len(inputs) > 4096 or len(outputs) > 4096:
            raise api.GraphAuthoringError("Resource property metadata exceeds the bounded limit", "RESOURCE_METADATA_BOUND_EXCEEDED")
        return {
            "package_name": package_name,
            "resource_id": resource_id,
            "resource_url": resource.getUrl(),
            "inputs": inputs,
            "outputs": outputs,
        }
    finally:
        try:
            if node is not None and temp_graph is not None:
                try:
                    temp_graph.deleteNode(node)
                except Exception:
                    pass
        except Exception:
            pass
        try:
            if temp_graph is not None:
                try:
                    temp_graph.delete()
                except Exception:
                    pass
        except Exception:
            pass
        try:
            app.getPackageMgr().unloadUserPackage(temp_package)
        except Exception:
            pass
