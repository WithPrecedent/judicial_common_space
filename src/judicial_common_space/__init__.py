"""Computes Judicial Common Space scores on demand"""

from __future__ import annotations

__version__ = '0.0.1'

__author__: str = 'Corey Rayburn Yung'

from . import (
    export,
    fjc,
    options,
    politics,
    scores,
    sources,
    states,
    stations,
    utilities,
    verify,
)
from .main import compute, run

__all__: list[str] = [
    'compute',
    'export',
    'fjc',
    'options',
    'politics',
    'run',
    'scores',
    'sources',
    'states',
    'stations',
    'utilities',
    'verify']
