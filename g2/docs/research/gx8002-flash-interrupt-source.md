# Flash controller interrupt callback

The C callback at package0x15ad4/runtime0x10023ac0 snapshots the word at
0xa2000030. If bit1 is set it reads0xa2000038; if bit3 is set it then reads
0xa200003c. Both decisions use the original snapshot, and it returns zero.
The reads remain volatile. No inferred hardware register names or additional
acknowledgment writes are introduced.

Native compilation produces30 bytes within the32-byte original slot, without
relocations or helper dependencies. Qualification replays846 decoded cases:
all low-byte status values, individual high bits, combined flags and varied
read results. It verifies exact ordered addresses and preserved registers.
Four rejection tests cover extra/missing reads, register corruption and unknown
instructions. The interface initializer registers this callback for IRQ15;
physical register side effects and interrupt timing are not qualified.

Integrated through the reviewed admission adapter. All159 native macOS codec
tests, full package build and artifact verification pass. The 32-byte stock
interval is now30 compiled C bytes and two unreachable fill bytes. Physical
IRQ behavior and full interface initialization remain unqualified.
