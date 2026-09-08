# GX8002 GPIO interrupt dispatch candidate

Stock package0xf46c/runtime0x10205ee0, envelope68 bytes. The authenticated
NationalChip gpio_mini.o at commit8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5
contains gpio_isr with matching decoded control flow and a relocated .bss
literal. Vendor callback table is0x20027930,32 records of12bytes: port,
callback, private pointer. The authenticated gx_gpio.h defines GPIO_CALLBACK
as int (*)(int, void *).

The candidate C snapshots0xa0001030 once, visits bits0..31, reads live callback
and private/port fields for pending pins, invokes callbacks, then writes the
pin mask to0xa0001030. A missing callback still causes the mask write. Newly
pending bits do not join the snapshot; callback registration changes can
affect later visited pins. Return is0; callback results are ignored.

Native macOS candidate compilation fits68 bytes; SHA
3f877adbc531c6990cf25740acb7798c9270b21d7fec2c7203ed92064147c41d.
It is NOT registered or qualified yet. An independent model has four passing
semantic tests covering empty snapshot, missing callback, changed pending
bits and live later callback. The model's write-one-clear pending state is a
hardware interpretation; target qualification must compare exact MMIO writes
without treating this model as silicon evidence. Next implement the decoded
stock/source interpreter, enforce28-byte frame and preserved registers, and
compare callback/memory traces including external mutation.

Decoded qualification now passes864 cases across pending patterns (empty,
full, alternating and all32 single bits), callback masks, three register seeds
and external mutation on/off. Both stock and source enforce28-byte saved
frame, caller clobbers and callee-saved ABI. Ten model/target tests pass,
including corrupt acknowledgement mask, wrong MMIO address, wrong callback
target and damaged frame. The reviewed qualification report is saved.
The candidate remains unregistered pending completion of the current
state-query integration. Physical GPIO behavior and callback bodies remain
outside this trace qualification.

Integration completed:607 tests pass. Full macOS apple-clang package build
and verify-artifacts succeed, with7,822 placed regions and zero unresolved.
Codec SHA3c4a3fca9904601b0bca7427d3d884fac4de454cbf4dbdf8b02e3dcfafb8505f;
EVENOTA SHAf0245331c18a8b7c517287a6f49ecaa854733fad6a667891853439aa08d68f8d.
The handler now supplies68 compiled C bytes. The artifact remains hybrid
and hardware-unqualified.
