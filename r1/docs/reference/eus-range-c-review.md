# Full-range EUS transport in C

The C receiver now accepts the complete 4,096-byte range already supported by
the stock sender. Stock RX rejects initial counter 17; accepting it is an
intentional improvement, bounded by a 4,096-byte allocation and copy checks.
The shared header defines the frame/message limits and correct three-argument
send callback type. The TX object remains unchanged after recompilation.

Verification executes the actual C sender, CRC, memory routines, receiver and
RX queue encoder. It passes 1,355 compatible stock/C comparisons, every length
from 4,063 through 4,096, 16 C safety scenarios, 36 compatible queue comparisons,
272 extended queue cases and five allocation-failure cases. Queue ownership is
checked by poisoning freed assembly memory and verifying retained payload;
every successful allocation is freed or transferred to the queue exactly once.

The normal open-source build compiles 852 units and composes both payloads.
All 841 other nongenerated objects remain unchanged. R1 manifest validation
passes. There are still 66 application and 22 bootloader imports. RTOS services,
allocation and radio are modeled; final firmware linking, boot and physical
radio delivery remain unverified. The global receive stream is not made
connection-isolated or reentrant. Byte identity and a paid compiler are not
requirements.

Hashes, REA stock read, test matrices and build audit are in
[eus-range-c-review.json](eus-range-c-review.json). The earlier
[RX review](rx-reassembly-c-review.md) describes the baseline; its recorded
counter-17 limitation is superseded here.
