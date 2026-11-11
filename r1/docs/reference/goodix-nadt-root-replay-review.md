# R1 Goodix NADT root stock/C replay, 2026-11-11

The locked application root is `goodix_nadt_calc` at `0x6e008`. The current C
root implements the uninitialized return, initialized off-cadence return,
public sample preparation and the typed 25-sample stream. The authenticated
stock application SHA-256 is
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
The current varied-state and 32,000-call replays execute the strict-linked
source ELF `build/r1-link-nadt-history-ordinal-20261111/application.elf` (SHA-256
`9e0606712a324b388d89bd93e90f39e54d37c2248d623dbbedbc58101906dffc`)
against that stock image in the Unicorn Cortex-M4 model. Earlier bounded
replays in the table used prior source ELFs, as recorded by their receipts.

The uninitialized branch clears native state offsets `+40`, `+32`, `+34` and
`+11`, copies the word at `+44` to public result `+4`, sets status byte `+3`
to 2 and returns 2 without reading input. The initialized off-cadence branch
clears an optional 52-byte allocation, zeros public result `+0`, advances
the 16-bit counter at state `+30`, copies state `+44` to result `+4` and returns
zero without reading input. The source root follows these stock paths.

The full-cadence replay exposed four further stock effects now represented in
C. The locked `0x28e14` integrity check sends a bad three-lane sample to the
9,000,000 sentinel before preparation, writing to the PPG array in direct
mode or the calibration array in calibrated mode. The `0x36034` helper writes its three
prepared lanes through the caller's sample pointer. The root records signed
primary/secondary extrema in the 16-word workspace history and the current
low-primary count in state `+60..+63`. At a 25-sample boundary stock resets
the axis-ratio and inactive-window counters; the secondary history uses
signed division by 256 with truncation toward zero. These were traced from
stock writes and corrected in the source root and typed stream.

| Replay | Paired cases | Boundary checked | Ignored receipt |
| --- | ---: | --- | --- |
| Uninitialized | 160 | Five non-`0xbf` markers, 32 seeds each | `build/r1-nadt-uninit-replay-20261111/results.json` |
| Initialized off cadence | 320 | Four rates, counter wraparound, optional allocation | `build/r1-nadt-uninit-replay-20261111/initialized-cadence-results.json` |
| Direct sample helper | 256 | Four channel strides, full sample array, preparation state and output lanes | `build/r1-nadt-uninit-replay-20261111/sample-preparation-results.json` |
| Calibrated sample helper | 256 | Four channel strides, full sample array, preparation state and output lanes | `build/r1-nadt-uninit-replay-20261111/calibrated-preparation-results.json` |
| First processed sample | 256 | Valid/invalid integrity words, state, result, sample array and workspace | `build/r1-nadt-uninit-replay-20261111/full-cadence-matrix-results.json` |
| First calibrated sample | 64 | Valid/invalid calibration integrity words, state, both input arrays, result and workspace | `build/r1-nadt-uninit-replay-20261111/calibrated-root-matrix-results.json` |
| Two and four calls | 256 each | Same sample buffer and accumulated state | `build/r1-nadt-uninit-replay-20261111/repeated-cadence-matrix-results.json`, `four-cadence-matrix-results.json` |
| 25, 50 and 100 calls | 64 each | Allocation-backed windows on a reused sample buffer | `build/r1-nadt-uninit-replay-20261111/window-allocation-matrix-results.json`, `two-window-allocation-matrix-results.json`, `hundred-sample-matrix-results.json` |
| Fresh input sequence | 32 sequences of 100 calls | Changing sample, sequence and scale codes, with valid and periodically invalid integrity words | `build/r1-nadt-uninit-replay-20261111/fresh-input-matrix-results.json` |
| Fresh calibrated sequence | 32 sequences of 100 calls | Changing calibration, sequence and scale codes, with valid and periodically invalid integrity words | `build/r1-nadt-uninit-replay-20261111/calibrated-hundred-matrix-results.json` |
| 50 Hz direct and calibrated sequences | 32 sequences of 100 calls each | Every other call skips sample processing; fresh input and calibration arrays use the same two integrity patterns | `build/r1-nadt-uninit-replay-20261111/fifty-hz-direct-matrix-results.json`, `fifty-hz-calibrated-matrix-results.json` |
| 100 Hz direct and calibrated sequences | 32 sequences of 100 calls each | Three of four calls skip sample processing; fresh arrays and both integrity patterns | `build/r1-nadt-uninit-replay-20261111/100-hz-direct-matrix-results.json`, `100-hz-calibrated-matrix-results.json` |
| 200 Hz direct and calibrated sequences | 32 sequences of 100 calls each | Seven of eight calls skip sample processing; fresh arrays and both integrity patterns | `build/r1-nadt-uninit-replay-20261111/200-hz-direct-matrix-results.json`, `200-hz-calibrated-matrix-results.json` |
| Varied 25 Hz direct configuration | 64 sequences of 100 calls | Eight combinations of classifier level, elapsed window limit, minimum samples, two streak limits and two metric thresholds, with fresh input and both integrity patterns | `build/r1-nadt-uninit-replay-20261111/varied-config-matrix-results.json` |
| Varied initialized state | 128 one-call pairs | Four channel strides, 16 seeded native states, valid and invalid integrity words, full state, result, sample, workspace and allocation | `build/r1-nadt-uninit-replay-20261111/varied-state-first-matrix-results.json` |

The fresh-input fixtures compare **after every call**: the full 92-byte
native state, 24-byte public result, complete sample array, 52-byte
allocation, and native workspace payload. The calibrated fixture also compares
the complete calibration array. They omit only the 24-byte filter
descriptor whose pointers relocate between the stock and source memory maps.
They also check return values, stack pointer and callee-saved registers. All
320 sequences at 25, 50, 100 and 200 Hz, or 32,000 paired calls, pass. The early returns additionally
check that neither root reads the input. The older source roots fail focused
negative controls before the corresponding fixes.

The varied-state replay initially failed all 128 pairs. Focused byte probes
and stock root disassembly at `0x6e1cc..0x6e1fe` and `0x6e4dc..0x6e530`
identified four missing native rules: the stream preserves byte `+2` exactly;
the input profile writes classification mode at `+10` while internal profile
at `+25` persists; profile `0` clears the counter at `+84`, while profile `2`
increments it at batch count `10` when below `100`; and a raw classifier word
of `2` or `3` copies native mode byte `+1` to quality byte `+9` before clearing
the stored classifier word at `+44`. The latter rule uses the raw word, even
when the public result has bit two set. These rules are now in the typed C
stream and native boundary. The focused single-byte probe still has a counterexample for
activity lane byte `+13 = 7`, outside the typed loader's supported `0..3`
range. A separate stock instruction at `0x6e520` copies the raw classifier
word to the allocation byte; the source now does the same, resolving the
focused noncanonical `+44 = 7` counterexample. The current image also passes
all 128 one-call varied-state pairs and the 32,000-call suite.

An additional unmodified-Unicorn 100-call replay starts from those same 128
varied native states. It passes 82 sessions and finds 46 mismatches, with no
emulation errors:
`build/r1-nadt-uninit-replay-20261111/varied-state-hundred-matrix-results.json`.
The first differences occur at later classifier windows, including native
state bytes `+4`, `+17`, and `+18`. A separate 176-pair short-history probe
sets the batch count to 24 and the primary history count to 1..22. All 176
pairs now match state, result, allocation, return, sample writes, and the
workspace history:
`build/r1-nadt-uninit-replay-20261111/short-primary-count-results.json`.
Two further 528-pair probes vary bounded initialized state at each primary
history count from 1 through 22. One uses a zeroed workspace; the other
seeds its history and signal arrays with bounded nonzero values. Both pass
without mismatches or emulation errors:
`build/r1-nadt-uninit-replay-20261111/short-primary-varied-results.json` and
`short-primary-workspace-results.json`. These cases support the current
short-history behavior but do not establish every state or input pattern.
Stock calls its primary classifier for short histories. The current C root
keeps the public result path active for them and now records the primary,
auxiliary, alternate, and high-variation allocation bytes computed by the
typed classifier. The stream now exports its sample ordinal before a window
reset; the native history bank uses that ordinal. This corrects the workspace
history order without the source memory-read faults caused by an earlier
long-lived local count probe. The later classifier state transitions remain open.

A focused valid-word, stride-one seed first differs on call 57, when the
primary history reaches 26 entries. Stock clears state byte `+17` (the axis
ratio streak); source leaves it at one, while the public result and allocation
still match. A code hook sees both window classifiers reach their late guard
with classification zero. In the source Unicorn trace, the compiled load of
the 26-entry count leaves its destination register zero even though memory at
that address contains 26, so that trace does not yet establish a C logic
error. The focused probe and trace are under
`build/r1-nadt-uninit-replay-20261111/axis-streak-first-failure*`.

An ignored diagnostic replay clears the stale Thumb ITSTATE at source PC
`0x4ff08`, immediately after the compiled one-instruction `it ne` block.
That makes the missing load execute and the focused 100-call session pass.
Applying the same emulator correction to all 128 varied-state sessions yields
128/128 passing 100-call comparisons, with no errors or mismatching state,
result, allocation, sample, or workspace data:
`build/r1-nadt-uninit-replay-20261111/it-clear-hundred-matrix-results.json`.
An additional 128 sessions combine those varied initial states with seven
varied configuration fields; all 12,800 calls pass under the same diagnostic
ITSTATE correction, including valid and periodically invalid integrity words:
`build/r1-nadt-uninit-replay-20261111/varied-state-config-it-clear-results.json`.
The source image is unchanged. This isolates the 46 raw-replay mismatches to
that Unicorn execution condition for these fixtures; it does not validate
physical-device behavior or arbitrary native states.

The current source receipt
`build/sources-r1-nadt-history-ordinal-20261111/report.json` compiles all
963/963 application and 82/82 bootloader units without duplicate strong
symbols. Both strict links pass with zero undefined references and no
retained stock executable code. The application uses 694,248 of 696,320
flash bytes, leaving 2,072 bytes; its 694,244-byte raw image has SHA-256
`2c3bf3d374eb1df387c8bf0ae942e983420065b69c814d7de8460c4f26c579ab`.
Static application RAM leaves 6,800 bytes before the reserved MSP stack. The
23,024-byte bootloader raw image still has SHA-256
`08e108776638ad4feaf2eada3861ab37d587b44ae3b5b75daacfa386ea67ac67`.

The initialized context in these root replays is seeded directly, and all
processed samples use synthetic 25, 50, 100 or 200 Hz configurations. Both direct and
calibrated conversion are covered for the stated cases. The 25 Hz direct
configuration replay varies seven fields; all other processed replays use the
same seed configuration. The varied-state replays use bounded synthetic states;
the longer variant has the counterexamples above. Other initial states,
configuration fields, allocator peak, actual sensor behavior and physical-device
execution remain unverified. A passing source link or bounded replay does not
establish byte identity or a fully functional R1 firmware image.
