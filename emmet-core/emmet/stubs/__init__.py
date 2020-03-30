"""
This module stubs in pydantic models for common MSONable classes, particularly those in Pymatgen
Use pymatgen classes in pydantic models by importing them from there when you need schema

"""

from emmet.stubs.utils import patch_msonable, use_model
from emmet.stubs.structure import Structure as StubStructure
from emmet.stubs.misc import Composition as StubComposition
from emmet.stubs.misc import ComputedEntry as StubComputedEntry
from pymatgen import Structure, Composition
from pymatgen.entries.computed_entries import ComputedEntry

use_model(Structure, StubStructure)
use_model(Composition, StubComposition, add_monty=False)
use_model(ComputedEntry, StubComputedEntry)
