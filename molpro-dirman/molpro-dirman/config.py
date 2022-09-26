# Utils for interacting with local config files

from pathlib import Path
from collections import namedtuple


def symlink_name(project_name: str, is_main:bool=True) -> str:
  "Name to be used for symlink(s) - naming differs if intended as main or aux project"
  if is_main:
    return "current_project"
  return f"project_{project_name}"


class Config:

  @staticmethod
  def version() -> str:
    return "0.0.2"


  @staticmethod
  def base_project_directory() -> Path:
    "Directory path object within which all project directories are being stored"
    return Path.home() / "Projects"


  @staticmethod
  def base_symlink_directory() -> Path:
    "Directory path object where symlinks to active projects should be created"
    return Path.home()

  
  @staticmethod
  def main_project_symlink_name() -> str:
    return symlink_name("", is_main=True)


# PREFIX DESCRIPTIONS
class Prefixes:

  PrefixDescription = namedtuple(
    "PrefixDescription", 
    ["short", "long"],
  )


  @staticmethod
  def definitions(verbose: bool=False) -> dict[str, PrefixDescription]:
    "Dictionary mapping serial prefix characters to their meanings"
    return {
      "A": Prefixes.PrefixDescription(
        short="Artistic",
        long="Has major artistic or aesthetic aspect - renders, artwork, graphic design, image editing, etc"
      ),
      "C": Prefixes.PrefixDescription(
        short="Collaborative",
        long="Was created in cooperation with 1 or more other outside parties - not all rights to project materials may belong to MolarFox or MolarFox Prototyping SP"
      ),
      "D": Prefixes.PrefixDescription(
        short="Digital / Software",
        long="Involved development of software or code"
      ),
      "F": Prefixes.PrefixDescription(
        short="Additive Manufacturing",
        long="Involved some form of additive manufacturing (FDM / SLA / SLS / etc)"
      ),
      "H": Prefixes.PrefixDescription(
        short="Hardware",
        long="Involved production / modification of physical item (beyond simple additive manufacturing)"
      ),
      "O": Prefixes.PrefixDescription(
        short="Open Source",
        long="Created as open source - projects that were initially closed source may lack this prefix"
      ),
      "P": Prefixes.PrefixDescription(
        short="Prototype",
        long="Created with the intention of not being production ready"
      ),
      "R": Prefixes.PrefixDescription(
        short="Restricted",
        long="Project metadata and contents are subject to tighter security and access restrictions"
      ),
      "S": Prefixes.PrefixDescription(
        short="Special",
        long="Special purpose - eg: gifts, metaprojects, milestone projects"
      ),
    }


  @staticmethod
  def as_dict(verbose: bool=False) -> dict[dict[str, str]]:
    return {
      s: {"short": desc.short, "long": desc.long}
      for s, desc in Prefixes.definitions().items()
    }
