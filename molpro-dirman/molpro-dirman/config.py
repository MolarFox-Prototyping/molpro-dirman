# Utils for interacting with local config files

from pathlib import Path
from collections import namedtuple

def base_project_directory() -> Path:
  "Directory path object within which all project directories are being stored"
  return Path.home() / "Projects"

PrefixDescription = namedtuple(
  "PrefixDescription", 
  ["short", "long"],
)

def prefix_definitions(verbose: bool=False) -> dict[str, PrefixDescription]:
  "Dictionary mapping serial prefix characters to their meanings"
  return {
    "A": PrefixDescription(
      short="Artistic",
      long="Has major artistic or aesthetic aspect - renders, artwork, graphic design, image editing, etc"
    ),
    "C": PrefixDescription(
      short="Collaborative",
      long="Was created in cooperation with 1 or more other outside parties - not all rights to project materials may belong to MolarFox or MolarFox Prototyping SP"
    ),
    "D": PrefixDescription(
      short="Digital / Software",
      long="Involved development of software or code"
    ),
    "F": PrefixDescription(
      short="Additive Manufacturing",
      long="Involved some form of additive manufacturing (FDM / SLA / SLS / etc)"
    ),
    "H": PrefixDescription(
      short="Hardware",
      long="Involved production / modification of physical item (beyond simple additive manufacturing)"
    ),
    "O": PrefixDescription(
      short="Open Source",
      long="Created as open source - projects that were initially closed source may lack this prefix"
    ),
    "P": PrefixDescription(
      short="Prototype",
      long="Created with the intention of not being production ready"
    ),
    "R": PrefixDescription(
      short="Restricted",
      long="Project metadata and contents are subject to tighter security and access restrictions"
    ),
    "S": PrefixDescription(
      short="Special",
      long="Special purpose - eg: gifts, metaprojects, milestone projects"
    ),
  }


def serials_json(verbose: bool=False) -> dict[dict[str, str]]:
  return {
    s: {"short": desc.short, "long": desc.long}
    for s, desc in prefix_definitions().items()
  }
