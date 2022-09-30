# DO NOT EDIT! This file was generated by jschema_to_python version 0.0.1.dev29,
# with extension for dataclasses and type annotation.

from __future__ import annotations

import dataclasses
from typing import Optional

from torch.onnx._internal.diagnostics.infra.sarif_om import (
    _multiformat_message_string,
    _property_bag,
)


@dataclasses.dataclass
class ArtifactContent(object):
    """Represents the contents of an artifact."""

    binary: Optional[str] = dataclasses.field(
        default=None, metadata={"schema_property_name": "binary"}
    )
    properties: Optional[_property_bag.PropertyBag] = dataclasses.field(
        default=None, metadata={"schema_property_name": "properties"}
    )
    rendered: Optional[
        _multiformat_message_string.MultiformatMessageString
    ] = dataclasses.field(default=None, metadata={"schema_property_name": "rendered"})
    text: Optional[str] = dataclasses.field(
        default=None, metadata={"schema_property_name": "text"}
    )


# flake8: noqa
