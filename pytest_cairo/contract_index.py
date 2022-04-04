from itertools import count
from pathlib import Path
from textwrap import indent
from typing import Dict, List, Union

INDENT = 4 * ' '


class Const:

    def __init__(self, name: str, value: int) -> None:
        self.name = name
        self.value = value

    def __str__(self) -> str:
        return f'const {self.name} = {self.value}'


class Namespace:

    def __init__(self, name: str) -> None:
        self.name = name
        self.consts: List[Const] = []
        self.namespaces: Dict[str, 'Namespace'] = {}

    def add(self, elem: Union['Namespace', Const]) -> None:
        if isinstance(elem, Namespace):
            self.namespaces[elem.name] = elem
        elif isinstance(elem, Const):
            self.consts.append(elem)
        else:
            raise Exception(f'Unknown element type {type(elem)}')

    def __str__(self) -> str:
        lines = [
            f'namespace {self.name}:',
            *[indent(str(c), INDENT) for c in self.consts],
            *[indent(str(n), INDENT) for n in self.namespaces.values()],
            'end',
        ]
        return '\n'.join(lines)


def generate_namespace(contract_dir: Path, count: count) -> Namespace:
    root = Namespace(contract_dir.parts[-1])

    for i, path in zip(count, contract_dir.glob('**/*.cairo')):

        parts = path.relative_to(contract_dir).parts
        scope = parts[:-1]
        contract = str(Path(parts[-1]).stem)

        current_namespace = root
        for name in scope:
            if name not in current_namespace.namespaces:
                current_namespace.add(Namespace(name))
            current_namespace = current_namespace.namespaces[name]
        current_namespace.add(Const(name=contract, value=i))

    return root


def generate_contract_index(root: Path) -> str:
    _count = count()

    return '\n'.join(
        str(generate_namespace(p, _count))
        for p in root.glob('[!.]*')
        if p.is_dir()
    )
