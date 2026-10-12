# Image-B runtime address and producer audit

The selected 312-unit image-B archive has 3 named undefined symbols. The
final source-fit linker binds all addresses. Two are authenticated BSS bounds
(`0x20017090..0x2002d79c`), one is the exact initialized sample-app pointer
at `0x20016f74`, and twelve runtime RAM slots lie inside that BSS interval; all twelve now have
source-owned storage; the denoise queue also has a separately placed buffer.
The final ELF has no undefined symbols, but an address binding alone does not
establish a runtime value.

Native system init `0x1000314c` calls `preserve_memory_10003ffc` and clears
the interval only when the return is zero. That function reads SoC status and
retention MMIO. On the retained path, these twelve RAM slots keep their
ambient prior contents; they must not be modeled with invented zero defaults.

| RAM slot | Selected source producer or consumer | Remaining condition |
| --- | --- | --- |
| exception scratch `0x20017390` | `backup_stage2_exception_experiment.c` stores fault frame | Fatal path and later diagnostic reader unqualified |
| clock gate bits `0x20017394` | `backup_stage2_clock_init_experiment.c` reads replay bits | Producer on retained path not established |
| console port `0x2001739c` | `backup_stage2_main_initial_leaves.c` writes port; debug putchar reads | Port selection and device effects remain runtime dependent |
| GPIO IRQ masks `0x200173a0` | main initial leaves reads pair | Producer for both words not established |
| IRQ descriptors `0x200173a8` | `backup_runtime_helpers.c` writes handler/context; generic IRQ reads | Registered lines and physical IRQ delivery unqualified |
| timer records `0x200174bc` | timer initializer fills 360 bytes | Scheduler/clock timing unqualified |
| flash probe state `0x2001765c` | flash wait reads and writes state 1 | Transition to state 2 or retained producer not established |
| SPI device state `0x20017670` | board device initializer writes 21-word record; callbacks read | Physical controller effect unqualified |
| board-pins-ready `0x200176d8` | pin initializer writes 1; finish reads | Pin MMIO qualification open |
| PMU record `0x2002cb88` | cold initializer clears 144 bytes; warm branch replays callbacks; resource controls write | Retained callback records and hardware wake path open |
| denoise mode state `0x2002d2bc` | mode initializer and tick read/write; beamforming init also accesses | Product mode selection and warm state open |
| denoise ring `0x2002d2d8` | audio callback and tick pass it to queue/GSC consumers | Exact queue capacity and producer lifecycle open |

The source-fit audit also caught four *defined* BSS symbols whose native
addresses were previously lost to a generic linker wildcard: platform
shadow, mode loop, mode index, and tokenizer cursor. The new linker script
places them at `0x20017398`, `0x2002d2b4`, `0x2002d2b8`, and `0x2002d3e0`
respectively and asserts each symbol. The current ELF and stock-length
payload derive from this corrected source snapshot, not the earlier fit ELF.

The offline BINH B stage pair contains source stage1 (12,288 bytes), the
four zero bytes observed between stock stages, and source stage2 (82,060
bytes). The separator's field meaning and outer codec package authentication
are unknown. `source-binh-stage-pair-receipt.json` verifies offsets and hashes;
this is an offline package-shape artifact, not a flashable image.

A bounded direct-literal scan of the authenticated stage2 bytes found one
word reference to gate bits (`0x100034c4`), one to GPIO masks
(`0x1000483c`), one to flash state (`0x10008000`), and two to denoise ring
(`0x1000bc20`, `0x1000bdac`). That supports the listed consumers and does not
reveal an additional direct-address producer. PC-relative, computed, DMA, and
resident producers are outside that scan; these four runtime roles remain
genuine unresolved value/lifecycle contracts.

The stage-1 selected loader's two marker paths now have a bounded native/source
instruction crosswalk (`stock-stage1-loader-receipt.json`). The normal branch
copies exactly 82,060 bytes to `0x10003000`. The marker branch first reads
four bytes from `package+0x323b0`, then passes the returned word plus
`0x323b4` to the reader with a zero-byte request at `0x20000000`, and returns
to stage-1 reset. The selected C expresses those exact arguments and branch
targets. Its zero-byte reader side effects, actual package data, reset
execution and physical IRAM/DRAM alias remain external evidence gates; no
runtime slot value was inferred from this static branch proof.

The flash probe byte at `0x2001765c` now has a typed source definition
(`backup_stage2_flash_probe_state.c`) and exact address placement in the
stock-length source-fit linker. Native `0x10007fc8` loads one byte and
`0x10007ffa` stores one byte with value 1; selected
`backup_stage2_flash_probe_wait.c` has the corresponding accesses. The new
object is one NOBITS byte with no initializer inside the conditional CRT BSS
range. The fresh 302-unit archive has 14 genuine imports (down from 15),
and the final layout still emits 82,060 bytes. The reproducible
`build-stock-length-flash-state-byte-round/flash-state-byte-receipt.json`
binds stock instructions, source hashes, section and ELF placement. This
closes the source storage/placement role only: a warm retained value or
producer of state 2 remains unresolved, as do flash hardware effects.

The board-pins-ready word at `0x200176d8` is now a four-byte source-owned
NOLOAD object at its exact native BSS address. Stock code reads the word at
`0x10008892` and writes value 1 at `0x100089d4`; selected C uses the same
word in `board_pin_apply` and `rtc_tick_initialize`. The fresh 303-unit
archive has 13 genuine imports, and its 307-object source-fit ELF still yields
the stock 82,060-byte transfer. The bounded
`build-stock-length-board-pins-ready-round/board-pins-ready-receipt.json`
ties source, native instructions, object size and ELF placement. Retained value
and physical pin effects remain unqualified.

The console port word at `0x2001739c` is now a four-byte source-owned
NOLOAD object. Native code stores the word at `0x1000480c` and reads it at
`0x1000481e`; selected C now routes both producer and debug output consumer
through one named lvalue. The fresh 304-unit archive has 12 genuine imports,
and its 308-object source-fit ELF still yields the 82,060-byte transfer.
`build-stock-length-console-port-round/console-port-receipt.json` binds
native instructions, C producer/consumer, object size and ELF placement.
UART effects and retained runtime value remain unqualified.

The exception anchor word at `0x20017390` is now a four-byte source-owned
NOLOAD object. Stock exception entry stores that word at `0x1000320c`, then
uses the address minus 72 bytes for a separate stack frame before loading
the word at `0x1000321c`. The selected assembly names the same anchor. The
fresh 305-unit archive has 11 genuine imports and its 309-object source-fit
ELF preserves the 82,060-byte transfer. The bounded
`build-stock-length-exception-anchor-round/exception-anchor-receipt.json`
checks source, native instructions, size and placement. This owns only the
anchor word; the preceding frame and exception-path behavior remain open.

The clock gate bits at `0x20017394` now occupy one source-owned NOLOAD
word immediately after the exception anchor. Native `0x10003404` loads the
word and selected clock initialization reads the same lvalue. The fresh
306-unit archive has 10 genuine imports and its 310-object source-fit ELF
still yields 82,060 bytes. `build-stock-length-clock-gate-word-round/clock-gate-word-receipt.json`
checks access width, source storage and placement. A retained-path producer
and value remain unknown.

The GPIO IRQ masks at `0x200173a0` are now a source-owned eight-byte
NOLOAD pair. Native `0x10004830` and `0x10004834` load offsets 0 and 4;
selected startup reads the same pair. The fresh 307-unit archive has nine
genuine imports and its 311-object source-fit ELF still emits 82,060 bytes.
`build-stock-length-gpio-irq-masks-round/gpio-irq-masks-receipt.json` checks
width, extent, source and placement. Retained values and the producer remain
unknown.

The IRQ descriptor table at `0x200173a8` is now a source-owned 256-byte
NOLOAD object. Native registration bounds lines below 32 and writes an
eight-byte handler/argument pair at `base + line * 8`; generic dispatch
reads the same pair. The fresh 308-unit archive has eight genuine imports,
and its 312-object source-fit ELF emits the 82,060-byte transfer. The
`build-stock-length-irq-descriptors-round/irq-descriptors-receipt.json`
checks the native access shape, C producer and consumer, object size and
placement. Native dispatch does not bound the hardware-supplied line;
registered handlers, retained values and physical delivery remain open.

The timer records at `0x200174bc` are now a source-owned 360-byte NOLOAD
object. Native initializer passes that exact byte count to its zero routine;
the IRQ loop advances 36 bytes and stops at `base + 360`, establishing ten
records. The fresh 309-unit archive has seven genuine imports, and its
313-object source-fit ELF emits the 82,060-byte transfer. The bounded
`build-stock-length-timer-records-round/timer-records-receipt.json` checks
native clear/loop extent, C consumer, object size and placement. Timer timing,
callbacks and physical effects remain unqualified.

The PMU record at `0x2002cb88` is now a source-owned 144-byte NOLOAD
object. Native cold initialization passes exactly 144 bytes to its zero
routine; the two eight-entry callback tables fill the record at offsets
`0x10` and `0x50`. The fresh 310-unit archive has six genuine imports and
its 314-object source-fit ELF still emits 82,060 bytes.
`build-stock-length-pmu-record-round/pmu-record-receipt.json` checks native
clear extent, C storage and placement. Warm callback count/contents and PMU
hardware effects remain unqualified.

The SPI state at `0x20017670` now has a 96-byte source-owned NOLOAD
allocation. The pinned `spi_master_v3.o` local BSS gives a 16-byte context
table, 36-byte master and 44-byte controller record at offsets 0, `0x10`
and `0x34`. Native `spi_master_v3_probe` uses the same base and subrecord
starts; the previously selected 84-byte C declaration was too short for
that SDK-correlated layout. The fresh 311-unit archive has five genuine
imports and its 315-object source-fit ELF emits 82,060 bytes. The bounded
`build-stock-length-spi-sdk-record-round/spi-sdk-record-receipt.json` hashes
the pinned SDK object and checks native offsets, C extent and ELF placement.
The SDK object is not byte-identical to product code, so this is a
corroborated source shape, not product runtime or physical SPI proof.

The denoise mode and ring imports now resolve to three disjoint source BSS
objects: a 28-byte prefix at `0x2002d2bc`, a 20-byte five-word queue at
`0x2002d2d8`, and a 40-byte buffer at `0x2002d2f0`. Native mode setup passes
`base+28`, `base+52`, size 40 and member size 4 to queue initialization;
the native queue initializer writes offsets 0, 4, 8, 12 and 16, matching the
pinned `LVP_QUEUE` shape. The four bytes `0x2002d2ec..0x2002d2f0` remain
unattributed. The fresh 312-unit archive has just three genuine imports
(BSS start/end and initialized sample-app pointer); its 316-object
source-fit ELF still emits 82,060 bytes. The bounded
`build-stock-length-denoise-storage-round/denoise-storage-receipt.json`
checks native arguments, SDK queue fields, object extents and placement.
Queue lifecycle, denoise selection and physical audio remain open.
