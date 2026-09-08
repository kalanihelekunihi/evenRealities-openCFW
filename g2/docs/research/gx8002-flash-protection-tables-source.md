# Protection policy source tables

The three arrays in runtime_gx8002_flash_protection_tables.c encode understood
query/setter fields: two expected status bytes, two masks and protected length.
Lengths are expressed in 64 KiB units, with named unprotected/policy entries.
No binary file is read to generate the C declarations. The verifier compiles
the C with the native macOS C-SKY toolchain and compares its output against
authenticated stock only as a qualification oracle.

The 256/512/1024 KiB policies have 5/7/9 entries, respectively:40/56/72 bytes.
All168 compiled data bytes match stock at package0x18590/0x185b8/0x185f0,
are four-byte aligned, and contain no relocations. Static layout assertions
check the eight-byte entry and length offset. The verifier also checks strictly
increasing lengths, initial zero and terminal capacity. Vendor hardware bit
semantics are not independently qualified; these are the shipped policies
as interpreted by recovered source code.

The initializer at package0x166d8 writes pointers and counts into three
consecutive eight-byte BSS descriptors starting at0x20026ff8. Its direct call
was located at package0x164ae/runtime0x1002449a, inside the separate flash
interface initialization routine beginning at package0x16450. That routine
and whole startup ordering still require qualification. Data admission adapter
and reviewed JSON are prepared; full package integration remains pending.

The profile initializer is now reconstructed in C and compiles byte-exactly
into its 44-byte original envelope. Its linker-resolved BSS symbol avoids
GCC splitting a fixed address across two literal bases. The table types and
extern declarations share runtime_gx8002_flash_protection_tables.h; both
builders record that header's hash. Regenerated table checks still pass.
Initializer verification requires exact instruction bytes, fits/no relocations,
and decoded replay of all six ordered stores. The function has no inputs,
branches, calls or stack frame; it was replayed with two incoming r0 values.
Prepared its reviewed admission report. BSS allocation ownership and the
larger startup caller remain separate outstanding work; integration is next.

Caller-prefix inspection confirms profile initialization is conditional on
successful device discovery: package0x164a2 calls discovery,0x164a8 branches
away on nonzero, and0x164ae calls the profile initializer. The interface
initializer also registers IRQ15 with handler0x10023ac0 before discovery and
uses an initial controller divisor4 before changing it to2 after profile
initialization. These are observed caller-prefix facts, not full caller
qualification; this path differs from the separate resume initializer.

Tables and initializer are now integrated into the reviewed codec candidate.
All155 native macOS tests, package assembly and artifact verification pass.
This migrates212 bytes from retained stock to source ownership without changing
the codec or package hashes. BSS ownership and full interface initialization
remain outstanding; no physical flash protection operation was performed.
