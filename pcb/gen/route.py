"""Orthogonal wire router for the generated schematic (D-038).

Works on the 1.27 mm grid in integer units. A route may not touch another net's
pin, run along or end on another net's wire (crossing straight through is fine,
it doesn't connect), enter a symbol body or a power symbol. Wires are kept as
unit edges per net and merged into straight runs on output, broken at pins,
corners and branch points, so every connection is end-to-end.
"""
G = 1.27
DIRS = {"E": (1, 0), "W": (-1, 0), "N": (0, -1), "S": (0, 1)}       # sheet y grows down
OPP = {"E": "W", "W": "E", "N": "S", "S": "N"}
ANG = {0: "E", 90: "N", 180: "W", 270: "S"}
MAX_EDGE = 32        # grid units (~40 mm); longer pin-to-pin hops read better as labels


def _u(p):
    return (round(p[0] / G), round(p[1] / G))


def _mm(q):
    return (round(q[0] * G, 4), round(q[1] * G, 4))


def _step(a, b):
    return "E" if b[0] > a[0] else "W" if b[0] < a[0] else "S" if b[1] > a[1] else "N"


class Router:
    def __init__(self):
        self.pins = {}       # point -> set of nets (None = no-connect)
        self.bodies = []     # (x0, y0, x1, y1), open interior is blocked
        self.reserved = set()
        self.occ = {}        # point -> {net: set of edge directions}

    # --- obstacles --------------------------------------------------------
    def add_pin(self, pos, net):
        self.pins.setdefault(_u(pos), set()).add(net)

    def add_body(self, ends):
        pts = [_u(p) for p in ends]
        if len(pts) < 2:
            return
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        if x0 == x1:
            x0, x1 = x0 - 1, x1 + 1
        elif not any(y == y0 and x0 < x < x1 for x, y in pts):
            y0 -= 1          # no pins on this edge: the body outline sits beyond the pin rows
        if y0 == min(ys) and y1 == max(ys) and y0 == y1:
            y0, y1 = y0 - 1, y1 + 1
        elif not any(y == max(ys) and x0 < x < x1 for x, y in pts):
            y1 += 1
        self.bodies.append((x0, y0, x1, y1))

    def reserve(self, pos, angle, length=3):
        """Keep wires out of the space a power symbol or label will occupy."""
        x, y = _u(pos)
        dx, dy = DIRS[ANG[angle]]
        for i in range(1, length + 1):
            self.reserved.add((x + dx * i, y + dy * i))

    # --- routing ----------------------------------------------------------
    def _path_dirs(self, pts):
        dirs, edges = {}, []
        for a, b in zip(pts, pts[1:]):
            d = _step(a, b)
            dx, dy = DIRS[d]
            q = a
            while q != b:
                n = (q[0] + dx, q[1] + dy)
                dirs.setdefault(q, set()).add(d)
                dirs.setdefault(n, set()).add(OPP[d])
                edges.append((q, n))
                q = n
        return dirs, edges

    def _ok(self, net, dirs):
        for q, nd in dirs.items():
            if q in self.reserved:
                return False
            if any(n != net for n in self.pins.get(q, ())):
                return False
            if any(x0 < q[0] < x1 and y0 < q[1] < y1 for x0, y0, x1, y1 in self.bodies):
                return False
            for n, od in self.occ.get(q, {}).items():
                if n == net:
                    continue
                cross = ({frozenset(nd), frozenset(od)} ==
                         {frozenset("EW"), frozenset("NS")})
                if not cross:
                    return False
        return True

    def _candidates(self, a, b):
        (ax, ay), (bx, by) = a, b
        if ax == bx or ay == by:
            yield [a, b]
            return
        yield [a, (bx, ay), b]
        yield [a, (ax, by), b]
        lo, hi = min(ax, bx), max(ax, bx)
        for mx in sorted(range(lo - 6, hi + 7), key=lambda m: abs(m - (ax + bx) / 2)):
            if mx not in (ax, bx):
                yield [a, (mx, ay), (mx, by), b]
        lo, hi = min(ay, by), max(ay, by)
        for my in sorted(range(lo - 6, hi + 7), key=lambda m: abs(m - (ay + by) / 2)):
            if my not in (ay, by):
                yield [a, (ax, my), (bx, my), b]

    def _route(self, net, a, b):
        best = None
        for pts in self._candidates(a, b):
            dirs, edges = self._path_dirs(pts)
            if not self._ok(net, dirs):
                continue
            cost = len(edges) + 4 * (len(pts) - 2)
            if cost > 1.5 * MAX_EDGE:
                continue
            if best is None or cost < best[0]:
                best = (cost, dirs)
        if best is None:
            return False
        for q, d in best[1].items():
            self.occ.setdefault(q, {}).setdefault(net, set()).update(d)
        return True

    def connect(self, net, positions):
        """Wire the pins together where possible; returns the connected groups (mm points)."""
        pts = list(dict.fromkeys(_u(p) for p in positions))
        parent = {p: p for p in pts}

        def find(p):
            while parent[p] != p:
                p = parent[p]
            return p

        pairs = sorted(((abs(a[0] - b[0]) + abs(a[1] - b[1]), a, b)
                        for i, a in enumerate(pts) for b in pts[i + 1:]))
        for d, a, b in pairs:
            if d <= MAX_EDGE and find(a) != find(b) and self._route(net, a, b):
                parent[find(a)] = find(b)
        groups = {}
        for p in pts:
            groups.setdefault(find(p), set()).add(_mm(p))
        return list(groups.values())

    def free_dir(self, pos, angle):
        """True if a label can sit at `pos` facing `angle` without lying on a wire."""
        x, y = _u(pos)
        d = ANG[angle]
        dx, dy = DIRS[d]
        if any(d in s for s in self.occ.get((x, y), {}).values()):
            return False
        return not any(self.occ.get((x + dx * i, y + dy * i)) for i in range(1, 4))

    # --- output -----------------------------------------------------------
    def _breaks(self):
        """Points where a straight run must end: pins, corners, branches, wire ends."""
        out = set()
        for q, nets in self.occ.items():
            for d in nets.values():
                if q in self.pins or d not in ({"E", "W"}, {"N", "S"}):
                    out.add(q)
        return out

    @property
    def wires(self):
        brk = self._breaks()
        out = []
        for q, nets in self.occ.items():
            for d in nets.values():
                for s in ("E", "S"):          # start a run at each break, heading E or S
                    if s not in d or q not in brk:
                        continue
                    dx, dy = DIRS[s]
                    e = (q[0] + dx, q[1] + dy)
                    while e not in brk:
                        e = (e[0] + dx, e[1] + dy)
                    out.append((_mm(q), _mm(e)))
        return out

    def junctions(self):
        out = []
        for q, nets in self.occ.items():
            for d in nets.values():
                if len(d) + (1 if q in self.pins else 0) >= 3:
                    out.append(_mm(q))
        return out
