"""Minimal reader for KiCad's kicadsexpr netlist (kicad-cli sch export netlist).

Runs under KiCad's bundled Python (pcbnew) and the repo .venv alike: stdlib only.
"""
import re

_TOK = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+')


def parse_sexpr(text):
    stack, cur = [], []
    for m in _TOK.finditer(text):
        t = m.group(0)
        if t == "(":
            stack.append(cur)
            cur = []
        elif t == ")":
            done, cur = cur, stack.pop()
            cur.append(done)
        else:
            cur.append(t[1:-1].replace('\\"', '"') if t.startswith('"') else t)
    return cur[0]


def _get(node, key):
    for c in node:
        if isinstance(c, list) and c and c[0] == key:
            return c
    return None


def _val(node, key, default=None):
    c = _get(node, key)
    return c[1] if c and len(c) > 1 else default


def read(path):
    """Return (components, nets).

    components: {ref: {"value", "footprint", "fields": {name: value}, "uuid"}}
    nets: {name: [(ref, pin), ...]}
    """
    root = parse_sexpr(open(path).read())
    comps = {}
    for c in _get(root, "components")[1:]:
        ref = _val(c, "ref")
        fields = {}
        f = _get(c, "fields")
        if f:
            for fld in f[1:]:
                fields[_val(fld, "name")] = fld[2] if len(fld) > 2 else ""
        for p in c:
            if isinstance(p, list) and p and p[0] == "property":
                fields.setdefault(_val(p, "name"), _val(p, "value", ""))
        comps[ref] = {
            "value": _val(c, "value", ""),
            "footprint": _val(c, "footprint", ""),
            "fields": fields,
            "uuid": _val(c, "tstamps", ""),
        }
    nets = {}
    for n in _get(root, "nets")[1:]:
        nodes = [(_val(x, "ref"), _val(x, "pin")) for x in n if isinstance(x, list) and x and x[0] == "node"]
        nets[_val(n, "name")] = nodes
    return comps, nets


if __name__ == "__main__":
    import sys
    comps, nets = read(sys.argv[1])
    want = set(sys.argv[2:])
    for name, nodes in sorted(nets.items()):
        for ref, pin in nodes:
            if not want or ref in want:
                print(ref, pin, name)
