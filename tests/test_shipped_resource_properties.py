"""Read-only shipped resource property inspection for edge preflight."""

from __future__ import annotations

import sys
from types import ModuleType, SimpleNamespace

import pytest

from dcc_mcp_substance3d_designer import graph_authoring as api
from dcc_mcp_substance3d_designer import graph_resources as resources
from dcc_mcp_substance3d_designer.skill_support import typed_result


class FakeProp:
    def __init__(self, identifier, category, type_id="float", readonly=False, connectable=True):
        self.identifier, self.category, self.type_id = identifier, category, type_id
        self.readonly, self.connectable = readonly, connectable

    def getId(self):
        return self.identifier

    def getCategory(self):
        return SimpleNamespace(name=self.category)

    def getTypes(self):
        if self.type_id is None:
            return []
        return [SimpleNamespace(getId=lambda: self.type_id, getModifier=lambda: SimpleNamespace(name="Auto"))]

    def isReadOnly(self):
        return self.readonly

    def isConnectable(self):
        return self.connectable

    def isVariadic(self):
        return False

    def getLabel(self):
        return self.identifier

    def getDescription(self):
        return "SDK property"

    def getDefaultValue(self):
        return None


class FakeInstanceNode:
    """SDK instance node as created in an isolated inspection graph."""

    def __init__(self):
        # spline_coords_1-class: texture, read-only value but edge-legal.
        # spline_amount_1-class: scalar, read-only non-texture, edge-illegal.
        self.inputs = [
            FakeProp("spline_coords_1", "Input", type_id="SDTypeTexture", readonly=True, connectable=True),
            FakeProp("spline_data_1", "Input", type_id="SDTypeTexture", readonly=True, connectable=True),
            FakeProp("spline_amount_1", "Input", type_id="int", readonly=True, connectable=True),
            FakeProp("locked_port", "Input", type_id="float", readonly=False, connectable=False),
        ]
        self.outputs = [
            FakeProp("spline_coords", "Output", type_id="SDTypeTexture"),
            FakeProp("spline_data", "Output", type_id="SDTypeTexture"),
            FakeProp("spline_amount", "Output", type_id="int"),
        ]

    def getProperties(self, category):
        return self.inputs if category == "Input" else self.outputs


class FakeGraph:
    """Shipped resource graph; instance properties come from a scratch instance."""

    def __init__(self, identifier="spline_append"):
        self.identifier = identifier
        self.instance = FakeInstanceNode()
        self.deleted_nodes = []
        self.deleted = False

    def getIdentifier(self):
        return self.identifier

    def getUrl(self):
        return self.identifier

    def newInstanceNode(self, resource):
        assert resource is self
        return self.instance

    def deleteNode(self, node):
        self.deleted_nodes.append(node)

    def delete(self):
        self.deleted = True


def _install_sd_modules(monkeypatch, tmp_path, package_name="spline_tools.sbs", resource=None):
    resources_dir = tmp_path / "resources" / "packages"
    resources_dir.mkdir(parents=True, exist_ok=True)
    (resources_dir / package_name).write_bytes(b"fake-sbs")
    fake_package = SimpleNamespace(
        findResourceFromUrl=lambda url: resource if url == getattr(resource, "identifier", None) else None,
        getChildrenResources=lambda _recursive: [resource] if resource is not None else [],
    )
    temp_package = SimpleNamespace(unloaded=False)
    temp_graph_holder: dict = {}

    class _FakeCompGraph:
        @staticmethod
        def sNew(package):
            assert package is temp_package
            graph = SimpleNamespace(
                newInstanceNode=lambda res: resource.newInstanceNode(res),
                deleteNode=lambda node: resource.deleted_nodes.append(node),
                delete=lambda: setattr(resource, "deleted", True),
            )
            temp_graph_holder["graph"] = graph
            return graph

    comp_module = ModuleType("sd.api.sbs.sdsbscompgraph")
    comp_module.SDSBSCompGraph = _FakeCompGraph
    unloaded: list = []
    def _new_user_package():
        return temp_package

    def _unload(package):
        assert package is temp_package
        unloaded.append(package)
        return True

    fake_manager = SimpleNamespace(
        loadUserPackage=lambda _path, _flag: fake_package,
        newUserPackage=_new_user_package,
        unloadUserPackage=_unload,
    )
    fake_app = SimpleNamespace(
        getPath=lambda _kind: str(tmp_path / "resources"),
        getPackageMgr=lambda: fake_manager,
    )
    monkeypatch.setattr(api, "application", lambda: fake_app)
    monkeypatch.setattr("builtins.temp_unloaded_marker", lambda: None, raising=False)
    prop_module = ModuleType("sd.api.sdproperty")
    prop_module.SDPropertyCategory = SimpleNamespace(Input="Input", Output="Output")
    graph_module = ModuleType("sd.api.sdgraph")
    graph_module.SDGraph = FakeGraph
    sbs_pkg = ModuleType("sd.api.sbs")
    monkeypatch.setitem(sys.modules, "sd.api.sbs", sbs_pkg)
    monkeypatch.setitem(sys.modules, "sd.api.sbs.sdsbscompgraph", comp_module)
    app_module = ModuleType("sd.api.sdapplication")
    app_module.SDApplicationPath = SimpleNamespace(DefaultResourcesDir="DefaultResourcesDir")
    monkeypatch.setitem(sys.modules, "sd", ModuleType("sd"))
    monkeypatch.setitem(sys.modules, "sd.api", ModuleType("sd.api"))
    monkeypatch.setitem(sys.modules, "sd.api.sdproperty", prop_module)
    monkeypatch.setitem(sys.modules, "sd.api.sdgraph", graph_module)
    monkeypatch.setitem(sys.modules, "sd.api.sdapplication", app_module)
    return fake_package


def test_shipped_texture_inputs_are_edge_legal_and_scalar_readonly_is_not(monkeypatch, tmp_path):
    graph = FakeGraph()
    _install_sd_modules(monkeypatch, tmp_path, resource=graph)
    result = resources.describe_shipped_resource_properties("spline_tools.sbs", "spline_append")
    assert result["package_name"] == "spline_tools.sbs"
    assert result["resource_id"] == "spline_append"
    by_id = {row["id"]: row for row in result["inputs"]}
    coords = by_id["spline_coords_1"]
    amount = by_id["spline_amount_1"]
    locked = by_id["locked_port"]
    # Both texture and scalar report read-only, but only texture carries SDTypeTexture.
    assert coords["read_only"] is True and coords["connectable"] is True
    assert any(kind["id"] == "SDTypeTexture" for kind in coords["types"])
    assert amount["read_only"] is True and amount["connectable"] is True
    assert not any(kind["id"] == "SDTypeTexture" for kind in amount["types"])
    assert locked["connectable"] is False
    # typed_result preserves the exact envelope including the property contract.
    wrapped = typed_result("describe", resources.describe_shipped_resource_properties, "spline_tools.sbs", "spline_append")
    assert wrapped["error"] is None
    assert wrapped["success"] is True


def test_shipped_inspection_creates_no_node_and_ignores_active_graph(monkeypatch, tmp_path):
    graph = FakeGraph()
    _install_sd_modules(monkeypatch, tmp_path, resource=graph)
    created = []
    monkeypatch.setattr(api, "active_graph", lambda: (_ for _ in ()).throw(AssertionError("must not touch active graph")))
    result = resources.describe_shipped_resource_properties("spline_tools.sbs", "spline_append")
    assert result["inputs"] and result["outputs"]
    assert created == []


def test_shipped_missing_resource_and_non_graph_fail_closed(monkeypatch, tmp_path):
    _install_sd_modules(monkeypatch, tmp_path, resource=None)
    with pytest.raises(api.GraphAuthoringError) as error:
        resources.describe_shipped_resource_properties("spline_tools.sbs", "absent_resource")
    assert error.value.code == "RESOURCE_NOT_FOUND"
    non_graph = SimpleNamespace(getIdentifier=lambda: "bitmap", getUrl=lambda: "bitmap")
    _install_sd_modules(monkeypatch, tmp_path, resource=non_graph)
    with pytest.raises(api.GraphAuthoringError) as error:
        resources.describe_shipped_resource_properties("spline_tools.sbs", "bitmap")
    assert error.value.code == "RESOURCE_NOT_GRAPH"


def test_shipped_invalid_identifiers_fail_closed(monkeypatch, tmp_path):
    graph = FakeGraph()
    _install_sd_modules(monkeypatch, tmp_path, resource=graph)
    with pytest.raises(api.GraphAuthoringError) as error:
        resources.describe_shipped_resource_properties("not-a-package", "spline_append")
    assert error.value.code == "INVALID_PACKAGE_NAME"
    with pytest.raises(api.GraphAuthoringError) as error:
        resources.describe_shipped_resource_properties("spline_tools.sbs", "0bad")
    assert error.value.code in {"INVALID_IDENTIFIER", "INVALID_PROPERTY_ID"}
