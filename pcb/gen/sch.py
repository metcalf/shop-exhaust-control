"""Small schematic-as-code layer over kiutils (D-035).

Connectivity is defined by net names. At write time (D-038): pins on the common
rails (POWER_NETS) get power symbols; within a block, pins sharing a net are joined
by drawn wires (route.py), and each wired group keeps one net label so names
survive into the netlist and link the group to other blocks. Where no clean route
exists the pin falls back to its own label. The netlist assertions (check.py) stay
the review surface; the drawing is for reading.
"""
import copy
import math
import uuid as uuidlib

from kiutils.items.common import Effects, Font, Justify, PageSettings, Position, Property, TitleBlock
from kiutils.items.schitems import (Connection, Junction, LocalLabel, NoConnect, SchematicSymbol, SymbolProjectInstance,
                                    SymbolProjectPath, Text)
from kiutils.schematic import Schematic
from kiutils.symbol import SymbolLib

from route import Router

KICAD_SYMBOLS = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/"
GRID = 2.54
PROJECT = "exhaust"
# Rails drawn as power symbols: {net: (lib_id, direction the symbol graphic points at rot 0)}
POWER_NETS = {"GND": ("power:GND", 270), "+3V3": ("power:+3V3", 90), "+5V": ("power:+5V", 90)}


def _uuid():
    return str(uuidlib.uuid4())


def _snap(v):
    return round(round(v / 1.27) * 1.27, 4)


class Sheet:
    def __init__(self, title, paper="A2"):
        self.s = Schematic.create_new()
        self.s.generator = "shop_exhaust_gen"
        self.s.uuid = _uuid()
        self.s.paper = PageSettings(paperSize=paper)
        self.s.titleBlock = TitleBlock(title=title, company="Shop exhaust controller")
        self._libs = {}
        self._defs = {}
        self.parts = []          # (ref, lib_id, {pin_number: net})
        self.block = None        # current block; wires are drawn only within one block
        self.conns = []          # (block, net, (x, y), outward angle)
        self.router = Router()
        self._npwr = 0

    def begin(self, name):
        """Start a block. Pins of the same net inside a block are wired together."""
        self.block = name

    # --- library symbols -------------------------------------------------
    def _lib(self, nick):
        if nick not in self._libs:
            self._libs[nick] = SymbolLib.from_file(KICAD_SYMBOLS + nick + ".kicad_sym")
        return self._libs[nick]

    def symdef(self, lib_id):
        """Flattened library symbol (derived 'extends' symbols merged with their parent)."""
        if lib_id in self._defs:
            return self._defs[lib_id]
        nick, name = lib_id.split(":")
        lib = self._lib(nick)
        sym = copy.deepcopy(next(x for x in lib.symbols if x.entryName == name))
        if sym.extends:
            parent = copy.deepcopy(next(x for x in lib.symbols if x.entryName == sym.extends))
            parent.properties = sym.properties
            parent.entryName = name
            for u in parent.units:
                u.entryName = name
            sym = parent
        sym.libraryNickname = nick
        self._defs[lib_id] = sym
        self.s.libSymbols.append(sym)
        return sym

    def pins(self, lib_id):
        """{number: (name, x, y, angle, type)} in library coordinates (y up)."""
        out = {}
        for u in self.symdef(lib_id).units:
            for p in u.pins:
                out[p.number] = (p.name, p.position.X, p.position.Y, p.position.angle, p.electricalType)
        return out

    # --- placement -------------------------------------------------------
    def place(self, ref, lib_id, value, at, nets, footprint="", lcsc="", rot=0, nc=(), dnp=False,
              fields=None, power=False):
        """Place one symbol. `nets` maps pin number or pin name -> net name.

        Every pin must be named in `nets` or `nc`; anything else is an error, so a
        forgotten pin can't silently float.
        """
        x, y = _snap(at[0]), _snap(at[1])
        pins = self.pins(lib_id)
        by_name = {}
        for num, (name, *_rest) in pins.items():
            by_name.setdefault(name, []).append(num)
        resolved = {}
        for key, net in nets.items():
            key = str(key)
            nums = [key] if key in pins else by_name.get(key)
            if not nums:
                raise KeyError(f"{ref}: no pin {key!r} on {lib_id}")
            for n in nums:
                resolved[n] = net
        ncs = set()
        for key in nc:
            key = str(key)
            ncs.update([key] if key in pins else by_name[key])
        missing = [n for n, p in pins.items() if n not in resolved and n not in ncs
                   and p[4] != "no_connect"]
        if missing:
            raise ValueError(f"{ref}: unassigned pins {missing}")

        sym = SchematicSymbol()
        sym.libraryNickname, sym.entryName = lib_id.split(":")
        sym.position = Position(x, y, rot)
        sym.unit, sym.inBom, sym.onBoard, sym.dnp = 1, not power, not power, dnp
        sym.uuid = _uuid()
        f = Effects(font=Font(height=1.27, width=1.27))
        hid = Effects(font=Font(height=1.27, width=1.27), hide=True)
        if rot % 180:        # horizontal two-pin parts: ref above, value below
            rpos, vpos = Position(x, y - 2.54, 0), Position(x, y + 2.54, 0)
        else:
            rpos, vpos = Position(x + 5.08, y - 1.27, 0), Position(x + 5.08, y + 1.27, 0)
        props = [("Reference", ref, rpos, f),
                 ("Value", value, vpos, f),
                 ("Footprint", footprint, Position(x, y, 0), hid),
                 ("Datasheet", "", Position(x, y, 0), hid),
                 ("LCSC", lcsc, Position(x, y, 0), hid)]
        for k, v in (fields or {}).items():
            props.append((k, v, Position(x, y, 0), hid))
        sym.properties = [Property(key=k, value=v, id=i, position=p, effects=e)
                          for i, (k, v, p, e) in enumerate(props)]
        sym.instances = [SymbolProjectInstance(name=PROJECT, paths=[
            SymbolProjectPath(sheetInstancePath="/" + self.s.uuid, reference=ref, unit=1)])]
        self.s.schematicSymbols.append(sym)

        r = math.radians(rot)
        seen, ends = set(), []
        for num, (name, px, py, ang, _t) in pins.items():
            rx = px * math.cos(r) - py * math.sin(r)
            ry = px * math.sin(r) + py * math.cos(r)
            pos = (_snap(x + rx), _snap(y - ry))
            ends.append(pos)
            if num in ncs:
                self.s.noConnects.append(NoConnect(position=Position(*pos), uuid=_uuid()))
                self.router.add_pin(pos, None)
                continue
            if num not in resolved or pos in seen:   # stacked pins (e.g. module GND) share one end
                continue
            seen.add(pos)
            self.router.add_pin(pos, resolved[num])
            if not power:
                self.conns.append((self.block, resolved[num], pos, (ang + rot + 180) % 360))
        self.router.add_body(ends)
        if not power:
            self.parts.append((ref, lib_id, dict(resolved)))
        return ref

    def _label(self, net, pos, la):
        just = Justify(horizontally="right") if la in (180, 270) else Justify(horizontally="left")
        self.s.labels.append(LocalLabel(text=net, position=Position(pos[0], pos[1], la),
                                        effects=Effects(font=Font(height=1.0, width=1.0), justify=just),
                                        uuid=_uuid()))

    def _power(self, net, pos, la):
        lib_id, points = POWER_NETS[net]
        self._npwr += 1
        hid = Effects(font=Font(height=1.27, width=1.27), hide=True)
        self.place(f"#PWR{self._npwr:03d}", lib_id, net, pos, {"1": net}, rot=(la - points) % 360,
                   power=True)
        sym = self.s.schematicSymbols[-1]
        sym.properties[0].effects = hid                     # hide #PWR refs
        off = {0: (3.5, 0), 90: (0, -3.5), 180: (-3.5, 0), 270: (0, 3.5)}[la]
        sym.properties[1].position = Position(pos[0] + off[0], pos[1] + off[1], 0)
        sym.properties[1].effects = Effects(font=Font(height=1.0, width=1.0))

    def _finish(self):
        """Power symbols, then wires within each block, then one label per wired group."""
        groups = {}
        for blk, net, pos, la in self.conns:
            if net in POWER_NETS:
                self.router.reserve(pos, la)
            else:
                groups.setdefault((blk, net), []).append((pos, la))
        for blk, net, pos, la in self.conns:
            if net in POWER_NETS:
                self._power(net, pos, la)
        # route small groups first: short local nets get the clean paths
        for (blk, net), pts in sorted(groups.items(), key=lambda kv: (len(kv[1]), kv[0][1])):
            for comp in self.router.connect(net, [p for p, _ in pts]):
                cand = [(p, la) for p, la in pts if p in comp]
                p, la = next(((p, la) for p, la in cand if self.router.free_dir(p, la)), cand[0])
                self._label(net, p, la)
        for a, b in self.router.wires:
            self.s.graphicalItems.append(Connection(type="wire", points=[Position(*a), Position(*b)],
                                                    uuid=_uuid()))
        for j in self.router.junctions():
            self.s.junctions.append(Junction(position=Position(*j), uuid=_uuid()))


    def note(self, text, at, size=1.8):
        self.s.texts.append(Text(text=text, position=Position(_snap(at[0]), _snap(at[1]), 0),
                                 effects=Effects(font=Font(height=size, width=size),
                                                 justify=Justify(horizontally="left")),
                                 uuid=_uuid()))

    def write(self, path):
        self._finish()
        self.s.to_file(path)
