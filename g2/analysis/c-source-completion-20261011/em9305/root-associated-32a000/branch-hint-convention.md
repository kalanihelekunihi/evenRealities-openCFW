# Forward BBIT Y-bit convention

The native disassembler prints `.t` for seven forward BBIT instructions.
The assembler handles these suffixes relative to the branch displacement,
with BBIT choosing the opposite T/NT insertion operand from ordinary BRCC.
See pinned tc-arc.c lines4328..4375 and arc-flag.def lines126..127.

Using the disassembler suffix verbatim produced Y=0, decoded as `.nt`.
Using `.nt` in this source produces Y=1, decoded as native `.t`.
Fresh strict ARC compilation and target disassembly confirm all seven
prediction bits now match. No instruction bytes are embedded as source.

This fixes the isolated hint discrepancy. Full branch destinations,
delay slots, BIH slots, child relocations and final image remain separate
review requirements. It does not establish hardware timing or execution.
