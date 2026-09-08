# Flash status and device configuration recovery

The image-A command transport is now source-built. Four recovered callers
also fit their original entry points when compiled with the native macOS
C-SKY compiler at `-Os`:

| Package offset | C function suffix | Behavior | C / envelope bytes |
| --- | --- | --- | ---: |
| 0x15748 | flash_read_status | Read one byte with command 0x05 | 24 / 24 |
| 0x15760 | flash_write_enable | Send command 0x06 without payload, return 0 | 16 / 16 |
| 0x15770 | flash_wait_ready | Repeat status reads until bit 0 clears, return 1 | 18 / 20 |
| 0x15784 | flash_read_status2 | Read one byte with command 0x35 | 24 / 24 |
| 0x16300 | flash_device_config | For the separately selected JEDEC 0x204016 path, set bit 4 via commands 0x15/0x11 | 66 / 68 |

The status comparison executes actual stock and compiled instructions,
including nested calls to the status-read helper from wait-ready. It checks
all 256 status bytes, every even ready status, four busy sequences, three
caller-clobber patterns, argument addresses, stack restoration, and return
values (3075 scenarios). The write-enable body is also byte-identical.
Command transport calls use the separately qualified source transport's
successful-completion contract; they are not opaque behavior invented to
make a stub pass. Physical controller behavior remains unqualified.

The device configuration comparison covers all 256 initial bytes and four
caller-clobber patterns (1024 scenarios). If bit 4 is already set, no write
occurs. Otherwise it preserves the other seven bits, waits ready, enables
writing, writes one byte using command 0x11, waits again, and returns zero.
The stack frame stays eight bytes. These control calls now resolve to named,
separately reconstructed C helpers. This function does not itself select the
JEDEC identifier; selection belongs to the still-unadmitted flash initializer.

The polling routines have no timeout or error return. A completed command
read initializes the byte; a device that never becomes ready causes continued
polling. Qualification does not establish timing, controller liveness, flash
compatibility, or operation under interrupts.

The neighboring generic quad-enable path at 0x162c8 reads status 2 and uses
command 0x31 to set bit 1. The alternate path at 0x16344 reads both status
bytes and uses command 0x01 with a two-byte payload. Both are now independently reconstructed and qualified by 131584 decoded
comparisons covering all status-byte pairs and caller clobbers. Their compiled
bodies (54 and 60 bytes) are integrated through the flash-quad admission adapter.
