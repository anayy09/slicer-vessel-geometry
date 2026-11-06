"""Print Slicer, VTK, and Python versions and check required extensions.

Run headless:
    "$SLICER_EXE" --no-main-window --python-script scripts/00_check_env.py

Exits with code 0 if every required check passes, 1 otherwise.
"""

import sys
import traceback

import slicer
import vtk

# Module names registered by each extension. The effect modules in
# SegmentEditorExtraEffects are named SegmentEditor<Effect>; we look for
# Local threshold specifically because the segmentation plan uses it.
REQUIRED_MODULES = {
    "SlicerVMTK": ["ExtractCenterline"],
    "SegmentEditorExtraEffects": ["SegmentEditorLocalThreshold"],
}
OPTIONAL_MODULES = {
    "SlicerVMTK (cross-section analysis)": ["CrossSectionAnalysis"],
    "TotalSegmentator": ["TotalSegmentator"],
}


def check_modules(groups, all_modules):
    results = {}
    for label, names in groups.items():
        results[label] = {name: name in all_modules for name in names}
    return results


def main():
    ok = True
    print(f"Slicer version : {slicer.app.applicationVersion}")
    print(f"Slicer revision: {slicer.app.repositoryRevision}")
    print(f"VTK version    : {vtk.vtkVersion.GetVTKVersion()}")
    print(f"Python version : {sys.version.split()[0]}")
    print(f"Python exe     : {sys.executable}")

    all_modules = set(slicer.app.moduleManager().modulesNames())

    print("\nRequired extensions:")
    for label, found in check_modules(REQUIRED_MODULES, all_modules).items():
        for name, present in found.items():
            print(f"  [{'OK' if present else 'MISSING'}] {label}: {name}")
            ok = ok and present

    print("\nOptional:")
    for label, found in check_modules(OPTIONAL_MODULES, all_modules).items():
        for name, present in found.items():
            print(f"  [{'OK' if present else '--'}] {label}: {name}")

    # Show the SegmentEditor effect modules actually installed, in case the
    # expected name above has changed in this Slicer version.
    effects = sorted(m for m in all_modules if m.startswith("SegmentEditor"))
    print(f"\nSegmentEditor* modules present: {', '.join(effects) or 'none'}")

    # Default coordinate system used when saving model files (STL/OBJ/VTK).
    # Recent Slicer saves models in LPS while the scene is RAS.
    storage = slicer.vtkMRMLModelStorageNode()
    cs = storage.GetCoordinateSystem()
    cs_name = slicer.vtkMRMLStorageNode.GetCoordinateSystemTypeAsString(cs)
    print(f"\nDefault model storage coordinate system: {cs_name}")

    try:
        import SampleData  # noqa: F401
        print("SampleData module importable: yes")
    except ImportError:
        print("SampleData module importable: NO")
        ok = False

    print(f"\nResult: {'PASS' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    exit_code = 1
    try:
        exit_code = 0 if main() else 1
    except Exception:
        traceback.print_exc()
    finally:
        # Without this the headless process never quits.
        slicer.util.exit(exit_code)
