# Image-B runtime address and producer audit

The selected 301-unit image-B archive has 15 named undefined symbols. The
final source-fit linker binds all addresses. Two are authenticated BSS bounds
(`0x20017090..0x2002d79c`), one is the exact initialized sample-app pointer
at `0x20016f74`, and twelve are runtime RAM slots inside that BSS interval.
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
