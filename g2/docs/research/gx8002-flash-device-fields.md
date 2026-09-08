# Flash device-record field evidence

Each device record is 24 bytes. The discovery and information routines establish
name pointer at +0, JEDEC identifier at +4, and size at +8. Write-protection
status (package 0x15900) establishes the field at +0x10 as a profile pointer:
profile +0 points to 8-byte entries and +4 is their count. Entry bytes 0/1
are status-1 expected value/mask, bytes 2/3 are status-2 expected value/mask,
and entry +4 is the resulting protected length. The routine reloads pointers
after status calls and stops at the first matching mask pair.

OTP accessors establish device +0x14 as an OTP descriptor pointer. Descriptor
+8 is region size, +0xc region count, and the low three bits at +0x10 encode
the selected region. Region selection first checks unsigned region < count,
then stores (old & ~7) | region; it does not independently mask the supplied
region. Caller records and descriptor pointers must be valid. No null checks
are present in these OTP accessors.

The shipped OTP descriptor at runtime 0x200266cc contains five words:
0x1000, 0x1000, 0x200, 3, 0. OTP read at package 0x15fb8 confirms the first word as base address and the
second as region stride: address = base + offset + selected_region * stride.
A source-authored descriptor now records these named fields; its build and
admission checks remain pending.
Protection profiles point into startup-cleared RAM and need their initialization
traced. This document identifies behavior; it does not promote those data
regions into source-owned firmware.
