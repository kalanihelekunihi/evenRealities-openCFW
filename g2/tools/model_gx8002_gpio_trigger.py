# SPDX-License-Identifier: MIT
"""Independent GPIO trigger registration and ordered register-write model."""
from dataclasses import dataclass
MASK = 0xffffffff
TABLE = 0x20027930
BASE = 0xa0001000
TRIGGER_OFFSETS = {1: 0x2c, 2: 0x28, 3: 0x24, 4: 0x14, 8: 0x18}


@dataclass(frozen=True)
class Case:
    port: int = 0
    trigger: int = 1
    callback: int = 0x10201000
    private: int = 0x20020000
    seed: int = 0


class Model:
    def __init__(self, case):
        self.case = case
        self.trace = []
        self.words = {TABLE + offset: (case.seed ^ offset * 0x1020304) & MASK
                      for offset in range(0, 384, 4)}
        self.words.update({BASE + offset: (case.seed ^ offset * 0x87654321) & MASK
                           for offset in TRIGGER_OFFSETS.values()})

    def read(self, address):
        if address not in self.words:
            raise ValueError('trigger read bounds')
        value = self.words[address]
        self.trace.append(('read', address, value))
        return value

    def write(self, address, value):
        if address not in self.words:
            raise ValueError('trigger write bounds')
        self.words[address] = value & MASK
        self.trace.append(('write', address, value & MASK))

    def call(self, name, *args):
        self.trace.append((name, *args))
        # Helper effects are deliberately outside this first boundary model.
        return self.case.seed


def expected(case):
    model = Model(case)
    if (case.port & MASK) >= 32:
        return model.trace, model.words, MASK
    model.call('direction', case.port, 0)
    record = TABLE + case.port * 12
    for offset, value in ((0, case.port), (4, case.callback), (8, case.private)):
        model.write(record + offset, value)
    offset = TRIGGER_OFFSETS.get(case.trigger & MASK)
    if offset is not None:
        address = BASE + offset
        model.write(address, model.read(address) | (1 << case.port))
    model.call('request_irq', 1, 0x10205ee0, 0)
    return model.trace, model.words, 0
