"""Describe exact native edge properties of one shipped resource instance via isolated inspection."""

from __future__ import annotations

from dcc_mcp_core.skill import skill_entry

from dcc_mcp_substance3d_designer.graph_resources import describe_shipped_resource_properties
from dcc_mcp_substance3d_designer.skill_support import typed_result


@skill_entry
def main(package_name: str, resource_id: str, **_kwargs):
    return typed_result(
        "Describe exact native edge properties of one shipped resource instance.",
        describe_shipped_resource_properties,
        package_name,
        resource_id,
    )
