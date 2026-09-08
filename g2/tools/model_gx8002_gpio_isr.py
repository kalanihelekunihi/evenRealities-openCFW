# SPDX-License-Identifier: MIT
"""Independent GPIO snapshot/dispatch/acknowledgement model."""
from dataclasses import dataclass
MASK = 0xffffffff
PENDING = 0xa0001030
RECORDS = 0x20027930


@dataclass(frozen=True)
class Case:
    pending: int = 0
    callbacks: int = MASK
    seed: int = 0
    mutation: bool = False


class Model:
    def __init__(self, case):
        self.case = case
        self.trace = []
        self.calls = 0
        self.words = {PENDING: case.pending & MASK}
        for pin in range(32):
            address = RECORDS + pin * 12
            self.words[address] = pin
            self.words[address + 4] = 0x10201000 + pin * 4 if case.callbacks & (1 << pin) else 0
            self.words[address + 8] = (case.seed ^ (pin * 0x1020304)) & MASK

    def read(self, address):
        if address not in self.words:
            raise ValueError('GPIO read bounds')
        value = self.words[address]
        self.trace.append(('read', address, value))
        return value

    def write(self, address, value):
        if address != PENDING:
            raise ValueError('GPIO write bounds')
        self.trace.append(('write', address, value & MASK))
        self.words[PENDING] &= ~(value & MASK)

    def callback(self, target, port, private):
        self.trace.append(('callback', target, port, private))
        self.calls += 1
        if self.case.mutation:
            # The hardware can add pending bits; callback registration can
            # change before later pins are visited. These writes are external.
            self.words[PENDING] ^= MASK
            for pin in range(32):
                self.words[RECORDS + pin * 12 + 4] = 0x10202000 + pin * 4
                self.words[RECORDS + pin * 12 + 8] = (self.case.seed ^ self.calls ^ pin) & MASK
        return (self.case.seed ^ self.calls) & MASK


def expected(case):
    model = Model(case)
    snapshot = model.read(PENDING)
    for pin in range(32):
        bit = 1 << pin
        if snapshot & bit:
            record = RECORDS + pin * 12
            callback = model.read(record + 4)
            if callback:
                private = model.read(record + 8)
                port = model.read(record)
                model.callback(callback, port, private)
            model.write(PENDING, bit)
    return model.trace, model.words, 0
