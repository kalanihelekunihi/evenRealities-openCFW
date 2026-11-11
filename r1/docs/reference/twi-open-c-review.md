# Hardware TWI open paths in C

`native_hw_twi_lifecycle.c` now contains no inline assembly. Both open paths
construct their configuration in C and call the existing init, error, and enable
providers directly. The naked bridges and out-of-line open kernels are removed;
close functions and both configuration templates retain their previous bytes and
relocations.

REA reads from the locked application cover primary open at `0x55278` (100 code
bytes) and secondary open at `0x552e4` (66 code bytes). An already-open bus returns
zero without provider calls. Otherwise each path copies its frequency/config tail,
loads both pins, initializes the legacy instance at cluster+28 with the current IRQ
metadata and null context, reports any nonzero init status, enables the embedded
TWIM instance at cluster+32, writes opened=1, and returns zero. A returning error
provider continues to enable, as stock does; actual fatal/reset behavior is outside
the fixture.

Primary configures both GPIO outputs first and reloads the second pin after the
first call. It retains its copied config pin fields when GPIO callbacks change
the underlying record. IRQ metadata is reloaded after both GPIO calls. Both native
and C primary frames are 40 bytes; both secondary frames are 32 bytes. Each init
configuration pointer is exactly caller SP-32. Two private secondary frame words
retain this native envelope; their contents are not claimed identical. Live
provider callee registers and other private saved words still differ.

There are 3,240 direct stock/C comparisons across both buses, opened values
0/1/255, pin boundaries, null/non-null callback metadata, full-width init statuses,
and six provider mutation modes. Mutations change the second pin/callback, config
bytes, instance bytes or opened state during GPIO/init/error/enable calls. These
checks verify ordered calls, configuration bytes and pointer, arguments, final
cluster state, return value, callee registers on return, SP and interrupt masks.
Six negative controls reject wrong frequency, wrong secondary hold setting,
missing error reporting, wrong enable instance, missing opened store and a stale
second pin.

Another 3,240 pairs execute the actual stock GPIO configuration instructions and
the existing compiled C SDK GPIO output wrapper. Ordered GPIO register writes and
mapped register memory match for the tested valid pins. MMIO uses emulated memory;
this does not establish electrical or peripheral behavior. Init, error and enable
remain modeled, as do the opaque callback signature boundary and real interrupt
behavior. Arbitrary frame aliases, faults and concurrency remain unproven.

The final normal Clang object reproduces the probe's open bytes and relocations.
All other 588 R1 objects are identical. All 589 units compile and compose with no
duplicate strong symbols; unresolved sets remain 164 application / 34 bootloader.
Qualification selects no new regions. A fresh canonical hybrid build retains the
locked application SHA with 4,245 source-built, 641,915 executable fallback and 248
resource bytes. The source plan is unchanged. Neither complete source-only
firmware nor exact reconstruction is established.

Machine-readable evidence and report pointers: `twi-open-c-review.json`.
Reproducible probes: ignored `build/goal-r1-twi-open-c/`.
