"""Generate the code reference pages and navigation."""

import importlib.util
import sys
from inspect import getmembers, isclass
from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()
mod_symbol = '<code class="doc-symbol doc-symbol-nav doc-symbol-module"></code>'

root = Path(__file__).parent.parent
src = root / "src"
sys.path.insert(0, str(src))


def snake_to_title(snake_str):
    return ' '.join(x.title() for x in snake_str.split('_'))


for path in sorted(src.rglob("*.py")):
    module_path = path.relative_to(src).with_suffix("")
    doc_path = path.relative_to(src / "payslip_parser").with_suffix(".md")
    full_doc_path = Path("reference", doc_path)

    parts = tuple(module_path.parts)

    if parts[-1] == "__init__":
        parts = parts[:-1]
        doc_path = doc_path.with_name("index.md")
        full_doc_path = full_doc_path.with_name("index.md")
    elif parts[-1].startswith("_"):
        continue

    # Extract class name from the module
    module_name = ".".join(parts)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    class_name_to_obj = {
        name: obj for name, obj in getmembers(module) if isclass(obj) and obj.__module__ == module_name
    }
    classes = list(class_name_to_obj)

    if classes:
        class_name = classes[0]  # Assuming one class per module
        # Convert the class name and module path to CamelCase format
        camel_case_parts = [snake_to_title(part) for part in parts[1:-1]] + [class_name]
        nav_parts = camel_case_parts
    else:
        continue

    nav[tuple(nav_parts)] = doc_path.as_posix()

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        ident = ".".join(parts)
        fd.write(f"---\ntitle: {ident}\n---\n\n::: {ident}")

    mkdocs_gen_files.set_edit_path(full_doc_path, ".." / path.relative_to(root))

with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
