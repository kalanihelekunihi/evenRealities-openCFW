# Status wait at 6608

The exact 66-byte body [6608,664A) contains 0 instructions. Inputs are a decrementing budget, a mode and a descriptor. For modes 2 and 3, select mask 0x01000000 and expected value (mode << 24) & mask. Otherwise select mask 1 and retain the full mode as expected value. This means modes outside 0–3 cannot match the masked status.

Repeatedly resolve the peripheral through descriptor[0], that object's word at offset 8, and the resulting object's first word. Read status at peripheral + 0x180. Return 0 immediately if (status & mask) differs from expected. If it matches and budget is zero, return 4. Otherwise call A324(1), decrement budget with unsigned wrapping and repeat. The helper return is ignored. Restore the 24-byte frame and saved registers.

54 original-instruction fixtures exercise six modes, three budgets and three controlled status transitions. They verify every status read, delay call, result and restored stack. The delay helper remains controlled; physical status transitions and time units are unresolved. This is private pseudocode evidence, with no canonical admission or C implementation.
