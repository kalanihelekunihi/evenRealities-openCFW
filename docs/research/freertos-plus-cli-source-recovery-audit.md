# FreeRTOS-Plus-CLI source and configuration recovery

Status: exact official source base selected, one local behavioral patch
recovered, production unchanged. This audit reads only the authenticated G2
2.2.6.10 Apollo image. It does not connect to, sign for, or flash hardware.

## Result

The G2 interpreter is conclusively derived from the classic FreeRTOS+CLI
lineage, but neither the exact historical point version nor commit is encoded
in the machine code. Its retained ABI and behavior are compatible with the
V1.0.1--V1.0.4 lineage after the canonical single-quoted `help` error-string
change. The retained core is also **not completely unmodified upstream**. The
safe reconstruction is:

1. reuse the official MIT `FreeRTOS_CLI.c` and `FreeRTOS_CLI.h` pair pinned
   below; and
2. carry one small, explicit G2 patch in `FreeRTOS_CLIProcessCommand`: do not
   emit the stock unknown-command message when the input is exactly carriage
   return or the empty string.

That replaces almost all previous “decompile the CLI” work with authenticated
source. It also corrects the earlier broad claim in
`minor-and-boundary-components-audit.md` that the interpreter was wholly
unmodified.

No official revision in the inspected FreeRTOS repository contains that blank
input branch. The broad historical semantic floor is commit
`747a0e15faf033e9b80cfec0c31b68a29b304f92` (V1.0.1, 2013-08-16), which first
introduces the retained single-quoted error text. Older C spelling and typedef
changes do not survive compilation, so the point version cannot be narrowed
honestly. Accordingly, the exact historical vendor checkout is not claimed.
The selected MIT source pair plus the 42-byte G2 branch is the narrowest
fail-closed reconstruction supported by the image.

## Official source identity

Repository: `https://github.com/FreeRTOS/FreeRTOS.git`

Selected reusable source commit:
`43defa566cc440251dbd6b48d1fcca27f88cfcdd`, tree
`1244875832c8ef8a39ee5b97a9dad657f7ea13ec`, dated 2021-12-23. This is the
202112-era V1.0.4 file pair naturally compatible with the already authenticated
FreeRTOS-Kernel V10.5.1 source selection.

The C/H Git blobs remain byte-identical through commit
`1309654d6f5d1342b4a9d3d7ae0824e8fcaefaf2`, tree
`6d95fe580646a9f12b9cc2f37bd1e9c4d72fbad7`, dated 2023-04-11. The next CLI
source change, `4727d6b3cc369310306ff24f61cafc1017853f82`, adds a static
registration API and restructures the registration function. This interval
pins the exact official source files selected for openCFW; it does not pretend
that comments or repository metadata can reveal G2's original checkout.

| File | Git blob | SHA-256 |
|---|---|---|
| `FreeRTOS_CLI.c` | `52dbe0d4a616b094ba92a7285bb4f31124b90e51` | `1719b355951afaf3349a371ff633d9dd4867a3e3442b91552fd3550082ef93f4` |
| `FreeRTOS_CLI.h` | `0f670ca8303f4732559d4a40a615f186a2d07985` | `c60d23b875d04429ba745b340d934b6c5eae89ce3be2b3a4aa92a034e6176890` |
| `History.txt` | `8c62cf90bb1d1995ece6ba95f12862505ab27303` | `5a561aba760ef014190a64fcf7235af99e005bc63a6732fffc2cc00d8ef5a960` |
| `LICENSE_INFORMATION.txt` | `6812e2716eee9232d8a247daa300584675a1a83a` | `6aa2663d0ffab6e9c830273b00d6f7b233955773057881c808bc368ca0079928` |

The selected component license is **MIT**, and its `History.txt` calls this
V1.0.4. The historical semantic floor predates the MIT relicensing and used
GPLv2/commercial terms; it is provenance evidence, not the recommended import.
The pinned 2021 source files and MIT license can therefore be imported instead
of recreating the library, while labeling V1.0.4 as the openCFW source choice
rather than a proven G2 point version.

## Exact G2 core boundary

| Function | Range | Bytes | SHA-256 |
|---|---:|---:|---|
| `FreeRTOS_CLIRegisterCommand` | `[0x005847AC,0x005847FE)` | 82 | `f38c77e0e672a21d1bb24fd6a26e604b1a782b5d633839aad036a96a69f7390b` |
| `FreeRTOS_CLIProcessCommand` | `[0x005847FE,0x005848FC)` | 254 | `a276b358abd3ec722f4da8e17928590941d16f06ae92ad1375a1baf963e2893d` |
| `FreeRTOS_CLIGetParameter` | `[0x005848FC,0x00584960)` | 100 | `35c6a4ce194bbea2a6044c3ab8f1108bb6c88806bafbf196fdb88c49a983a6f4` |
| `prvHelpCommand` | `[0x00584960,0x0058498E)` | 46 | `7603491ef1e11c9a1163028ac35a5800f53402536eb99633a45fee477948a32c` |
| `prvGetNumberOfParameters` | `[0x005849A8,0x005849D4)` | 44 | `e490fbface011c7219cd628b01e189998e661015dc22991ef18ed63f7faea508` |

The local branch is `[0x005848CA,0x005848F4)`, SHA-256
`4ed35ac83ff6802181aee553929f5eadff5e6b6c797601145d1c688c88eae7c1`.
In source terms its behavior is:

```c
if (!(strlen(pcCommandInput) == 1 && pcCommandInput[0] == '\r') &&
    !(strlen(pcCommandInput) == 0 && pcCommandInput[0] == '\0')) {
    strncpy(pcWriteBuffer, pcUnknownCommand, xWriteBufferLen);
}
```

The rest of the five retained functions matches the classic source behavior:
first exact command token match, signed expected-count validation, callback
continuation until `pdFALSE`, a stateful help iterator, and the stock
space-delimited parameter accessor. The canonical stock “incorrect parameter”
and “command not recognised” strings are retained verbatim.

`FreeRTOS_CLIGetOutputBuffer` is not retained. Its absence matters for the
configuration conclusions below.

## ABI and state

The 32-bit target ABI is fully recovered:

| Object | Layout |
|---|---|
| `CLI_Command_Definition_t` | 16 bytes: command pointer `+0`, help pointer `+4`, Thumb callback `+8`, signed `int8_t` expected count `+0xC`, three bytes padding |
| callback | `BaseType_t callback(char *output, uint32_t output_len, const char *input)` |
| registered-list node | 8 bytes: descriptor pointer `+0`, next pointer `+4` |

The built-in help descriptor is at `0x00785F90`. Its initialized list node is
at `0x20000BE8`; the initialized last-node pointer at `0x20000BF0` starts by
pointing to that node. The process continuation cursor is `0x200745E4` and the
help cursor is `0x200745E8`. Both stateful iterators make the interpreter
non-reentrant exactly as upstream documents.

The expected-count field is signed. `-1` is the documented variable-parameter
sentinel; the machine code bypasses validation for any negative value. Fixed
values are representable from 0 through 127. The 76 G2 descriptors use only
`-1..3`: 15 variable, 19 zero, 27 one, 12 two, and 3 three-parameter commands.
`FreeRTOS_CLIGetParameter` accepts an unsigned 32-bit wanted index and imposes
no global limit. Across 115 retained calls, the highest index actually
requested is 11, in the exact nine-iteration parameter loop at
`[0x00580AF4,0x00580B1C)`.

## Buffers and the boundary of proof

The only call to `FreeRTOS_CLIProcessCommand` is at `0x0054166E`. It passes:

- input buffer `0x20071BC8`;
- output buffer `0x20071B48`; and
- output length `128`.

Both console buffers occupy 128 bytes and are cleared with that exact size.
The effective G2 output limit is therefore 128 bytes. The input collector also
accepts indices 0 through 127, but does not append a NUL after byte 128. The
safe NUL-terminated command payload is at most **127 bytes**. A full 128-byte
line can make the stock `strlen`-based parser read beyond the input array; a
source port should retain the external behavior but repair this memory-safety
defect deliberately and test the compatibility decision.

The exact value of upstream `configCOMMAND_INT_MAX_OUTPUT_SIZE` is **not
recoverable**. `FreeRTOS_CLIGetOutputBuffer` and its optional upstream buffer
are dead, while the G2 console passes its own 128-byte buffer. Likewise,
`configAPPLICATION_PROVIDES_cOutputBuffer` cannot be distinguished after dead
stripping. Treating the effective 128-byte call-site limit as proof of either
macro would overclaim.

## Allocation and static policy

G2 calls the dynamic `FreeRTOS_CLIRegisterCommand` 76 times. The exact body:

- asserts the descriptor is non-null;
- calls `pvPortMalloc(8)` at `0x00456110`;
- asserts allocation success;
- appends under the exact critical-section pair
  `0x004420D0`/`0x004420E8`; and
- never frees a node, consistent with one-time lifetime registration.

This accounts for at least 608 heap payload bytes, excluding allocator
overhead. No static-registration call is observed, and a separate static-body
identity is not established. That proves the deployed descriptor path is
dynamic. It does **not** prove the
compile-time value of `configSUPPORT_STATIC_ALLOCATION`, because an enabled
but unused API can be removed by section garbage collection.

For openCFW, the cleanest source policy is to select one deliberately:
preserve dynamic registration for exact behavior initially, then optionally
move the fixed 76-node set to the official static API as an explicit project
change rather than claiming G2 already did so.

## Vendor glue boundary

The authenticated initialized SRAM contains 76 distinct vendor descriptors;
their call sites, descriptors, command/help strings, callbacks, and ordering
hash as one aggregate to
`268128313cc6da003e82e72b4341f5208a480196b3da1a1c0085b49a79d51788`.
They span platform, filesystem, display, logging, IMU/audio, BLE, touch,
terminal, onboarding, and settings commands. The retained path marker
`D:\01_workspace\s200_ap510b_iar_git\kernel\FreeRTOS-Plus-CLI\prvCommand\prvCommand_filesystem.c`
corroborates that these descriptors and handlers are the application layer;
it is not used as version proof.

This is the correct split for source recovery:

- vendor the pinned official interpreter/header/license;
- carry the one blank-input patch explicitly;
- reconstruct or keep blob-backed the G2 descriptors and their command
  handlers by functional group; and
- do not conflate the 76-command proprietary surface with the two-file open
  source library.

## Reproduction

```sh
cd openCFW
python3 tools/analyze_g2_freertos_plus_cli.py
python3 tools/analyze_g2_freertos_plus_cli.py \
  --upstream-checkout /path/to/official/FreeRTOS
python3 -m unittest -v tests.test_analyze_g2_freertos_plus_cli
```

The analyzer authenticates the whole official payload, every admitted body and
configuration window, the IAR initialized-SRAM stream, the complete
registration/parameter caller sets, the descriptor aggregate, and optionally
the upstream commits, trees, Git blobs, SHA-256 files, history, and MIT
license. Output is deterministic JSON.
