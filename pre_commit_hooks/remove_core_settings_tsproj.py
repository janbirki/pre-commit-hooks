#!/usr/bin/env python3
"""
remove_settings_tsproj.py

- Searches the current directory (including subfolders) for *.tsproj files
- Removes every <Settings> element (including all subelements)
- Writes the cleaned file back (overwrites the original)
"""

import sys
import pathlib
import xml.etree.ElementTree as ET
from typing import List

# ----------------------------------------------------------------------
# helper functions
# ----------------------------------------------------------------------
def _find_tsproj_files(base_dir: pathlib.Path) -> List[pathlib.Path]:
    """
    Returns a sorted list of all *.tsproj files in the specified directory.
    The search is recursive, so subfolders are also included.
    """
    if not base_dir.is_dir():
        sys.exit(f"Der Pfad '{base_dir}' is not a valid directory.")
    return sorted(base_dir.rglob("*.tsproj"))  # rglob = rekursives Glob


def _load_xml(path: pathlib.Path) -> ET.ElementTree:
    """Loads the XML file and returns the ElementTree object."""
    try:
        return ET.parse(path)
    except ET.ParseError as exc:
        sys.exit("Error parsing from '{path}': {exc}")
    except OSError as exc:
        sys.exit("Could not open file '{path}': {exc}")


def _remove_settings(tree: ET.ElementTree) -> bool:
    """Remove all <Settings> elements in the tree."""
    root = tree.getroot()
    removed = False

    for parent in root.iter():
        for child in list(parent):
            if child.tag == "Settings":
                parent.remove(child)
                removed = True
    return removed


def _indent(elem: ET.Element, level: int = 0) -> None:
    """
    Recursive indentation (fallback for Python < 3.9).
    Prevents unnecessary blank lines.
    """
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for child in elem:
            _indent(child, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if not elem.tail or not elem.tail.strip():
            elem.tail = i


def _write_xml(tree: ET.ElementTree, out_path: pathlib.Path) -> None:
    """Write back the (modified) XML with clean formatting."""
    root = tree.getroot()
    if hasattr(ET, "indent"):               # Python ≥3.9
        ET.indent(tree, space="  ")
    else:
        _indent(root)

    tree.write(out_path, encoding="utf-8", xml_declaration=True)


# ----------------------------------------------------------------------
# main logic
# ----------------------------------------------------------------------
def main() -> None:
    # Base directory: the current working directory from which the script is started
    base_dir = pathlib.Path.cwd()

    tsproj_files = _find_tsproj_files(base_dir)

    if not tsproj_files:
        sys.exit("No *.tsproj files found in the XYZ directory.")

    for proj_path in tsproj_files:
        rel = proj_path.relative_to(base_dir)
        print("Process: {rel}")

        tree = _load_xml(proj_path)

        if _remove_settings(tree):
            _write_xml(tree, proj_path)   # overwrites the original file
            print("   <Settings> removed and file saved.\n")
        else:
            print("   No <Settings> element found - unchanged.\n")


if __name__ == "__main__":
    main()