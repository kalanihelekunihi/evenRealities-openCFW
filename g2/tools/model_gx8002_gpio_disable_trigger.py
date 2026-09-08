# SPDX-License-Identifier: MIT
"""GPIO trigger disable sequence against the shared callback/register layout."""
from model_gx8002_gpio_trigger import Case, Model, MASK, TABLE, BASE


def expected(case):
    model = Model(case)
    if (case.port & MASK) >= 32:
        return model.trace, model.words, MASK
    model.call('direction', case.port, 2)
    keep = MASK ^ (1 << case.port)
    for offset in (0x14, 0x18, 0x28, 0x2c, 0x24):
        address = BASE + offset
        model.write(address, model.read(address) & keep)
    record = TABLE + case.port * 12
    for offset, value in ((0, 255), (4, 0), (8, 0)):
        model.write(record + offset, value)
    return model.trace, model.words, 0
