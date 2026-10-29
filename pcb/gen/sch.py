"""Small schematic-as-code layer over kiutils (D-035).

Every pin gets a net label at its endpoint, so connectivity is defined by net
names, not drawn wires. That keeps the generator simple and makes the netlist
assertions (check.py) the real review surface; the rendered sheet is for reading.
"""
import copy
import math
import uuid as uuidlib

from kiutils.items.common import Effects, Font, Justify, PageSettings, Position, Property, TitleBlock
from kiutils.items.schitems import (LocalLabel, NoConnect, SchematicSymbol, SymbolProjectInstance,
                                    SymbolProjectPath, Text)
from kiutils.schematic import Schematic
from kiutils.symbol import SymbolLib

KICAD_SYMBOLS = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/"
GRID = 2.54
PROJECT = "exhaust"


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
              fields=None):
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
        sym.unit, sym.inBom, sym.onBoard, sym.dnp = 1, True, True, dnp
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
        seen = set()
        for num, (name, px, py, ang, _t) in pins.items():
            rx = px * math.cos(r) - py * math.sin(r)
            ry = px * math.sin(r) + py * math.cos(r)
            pos = (_snap(x + rx), _snap(y - ry))
            if num in ncs:
                self.s.noConnects.append(NoConnect(position=Position(*pos), uuid=_uuid()))
                continue
            if num not in resolved or pos in seen:   # stacked pins (e.g. module GND) share one label
                continue
            seen.add(pos)
            la = (ang + rot + 180) % 360
            just = Justify(horizontally="right") if la in (180, 270) else Justify(horizontally="left")
            self.s.labels.append(LocalLabel(text=resolved[num], position=Position(pos[0], pos[1], la),
                                            effects=Effects(font=Font(height=1.0, width=1.0),
                                                            justify=just),
                                            uuid=_uuid()))
        self.parts.append((ref, lib_id, dict(resolved)))
        return ref

    def note(self, text, at, size=1.8):
        self.s.texts.append(Text(text=text, position=Position(_snap(at[0]), _snap(at[1]), 0),
                                 effects=Effects(font=Font(height=size, width=size),
                                                 justify=Justify(horizontally="left")),
                                 uuid=_uuid()))

    def write(self, path):
        self.s.to_file(path)
