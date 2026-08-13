# FreeRTOS+CLI `FreeRTOS_CLIGetParameter` candidate and production audit

## Result

`runtime_freertos_cli_get_parameter_candidate.c` remains an isolated,
production-excluded qualification oracle. A separately named and separately
licensed production leaf, `runtime_freertos_cli_get_parameter.c`, now replaces
the G2 parameter accessor at `[0x005848FC,0x00584960)`. The official 100-byte
body has SHA-256
`35c6a4ce194bbea2a6044c3ab8f1108bb6c88806bafbf196fdb88c49a983a6f4`.
Candidate and production are behaviorally differential-tested against the
actual authenticated FreeRTOS+CLI V1.0.4-compatible source snapshot selected
at official commit `43defa566cc440251dbd6b48d1fcca27f88cfcdd`.

This leaf is a space-delimited string scanner. It has no allocator, global
state, FreeRTOS primitive, device register, callback, transport, generated
schema, or hardware dependency. Its only contract is a NUL-terminated input
string, a 32-bit unsigned wanted index, and a writable 32-bit signed result
length. Parameter numbering begins at one; index zero and missing parameters
return null after writing length zero.

The candidate is absent from the production overlay, every manifest, and the
Makefile. Production registers only the independently named
`open_cfw_freertos_cli_get_parameter` accessor. The former source-owned
collector-capacity fragment was retired when the complete console task became
a seven-leaf source replacement; its byte-consumer now preserves the same
127-byte safety bound directly. The candidate therefore cannot alter a
flashable artifact even though its qualified algorithm has been promoted
through the separate production file. No hardware was connected, signed for,
erased, programmed, reset, or flashed.

## Authenticated source and stock identity

The upstream oracle is the unchanged MIT `FreeRTOS_CLI.c` snapshot:

| Evidence | Value |
|---|---|
| upstream source | 11,623 bytes; SHA-256 `1719b355951afaf3349a371ff633d9dd4867a3e3442b91552fd3550082ef93f4` |
| exact accessor source slice | 1,316 bytes; SHA-256 `b9e95de63ffd212c6dd455159839b6f9d6507d40662493f5b5e3832919d0094b` |
| official G2 package | 3,523,396 bytes; SHA-256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| installed mapping | package byte 32 maps to `0x00438000` |
| stock accessor | `[0x005848FC,0x00584960)`, 100 bytes, SHA-256 `35c6a4ce194bbea2a6044c3ab8f1108bb6c88806bafbf196fdb88c49a983a6f4` |

The test compiles the authenticated upstream file itself with a narrow host
FreeRTOS configuration shim, rather than maintaining a handwritten behavioral
oracle. Candidate and upstream return offsets and lengths are compared for
empty input, index zero, missing parameters, repeated/leading/trailing spaces,
the fact that only ASCII space is a delimiter, a 255-byte parameter, and the
safe logical-boundary witness described below. A second differential test
exhausts all 5,461 strings through six bytes over `a`, `b`, ASCII space, and
tab against indices 0–6 and `UINT32_MAX`: 43,688 candidate/oracle comparisons.

## Exact ABI and behavior

The stock prologue is:

```text
30b4 0300 0025 0024 0020 1060
```

It preserves working registers, copies R0 into the byte cursor, clears the
found-count and return pointer, and stores zero through R2. R1 is compared as
the full wanted-parameter word. The epilogue moves the selected interior
pointer or null into R0, restores registers, and returns with `BX LR`.

The isolated header therefore uses exact four-byte types:

```c
typedef __UINT32_TYPE__ open_cfw_freertos_cli_ubase_type;
typedef __INT32_TYPE__  open_cfw_freertos_cli_base_type;
```

Compile-time assertions keep both at four bytes. The algorithm preserves
these upstream edge cases:

- wanted index zero returns null and length zero without scanning;
- empty input and a missing parameter return null and length zero;
- one or more ASCII spaces separate words;
- leading spaces make the first nonempty word parameter one;
- repeated spaces are skipped and trailing spaces do not create a parameter;
- tab is part of a word, not a delimiter; and
- returned pointers refer directly into the caller's string and are not
  separately NUL terminated.

## Complete ingress and boundary proof

The official image contains exactly 115 direct Thumb `BL` calls to
`0x005848FC`. Their ordered little-endian address stream hashes to
`e43d8a1d82be6ce7313378790a1c74156806f3c0d1d6f1f9db1251d6a8ffee69`;
the ordered `address || instruction` records hash to
`00271d27ae69620b273eaa6d1824990df438fc3550fade8401200da774c32ce8`.
The dedicated test stores all 115 addresses explicitly, not only their count.

An exhaustive halfword scan finds:

- no `B.W` entry jump;
- no wide conditional entry;
- no narrow `B`, conditional branch, `CBZ`, or `CBNZ` entry;
- no external branch to an interior halfword; and
- no aligned stored word or odd Thumb function pointer naming the entry or an
  interior address.

A byte-granular stored-value scan has exactly one numerical collision:
unaligned bytes at `0x00778176` decode little-endian as even value
`0x00584952`. They are the ASCII suffix `RIX\0` inside the complete string
`NON_INVERTIBLE_MATRIX`; the storage address is two-byte-misaligned and the
value is not a Thumb pointer. The test records this collision explicitly so a
future image cannot silently add a real stored pointer.

The eight bytes immediately before the entry are
`00242000bde8f087`, SHA-256
`55e991a5166aaf1ba985d30f4cd65c23c29dbc5253bce1b72144bb9731089ee0`.
They end the preceding `FreeRTOS_CLIProcessCommand` with `POP.W {...,pc}`.
The accessor itself ends in `BX LR`, and the successor at `0x00584960` begins
with `PUSH {r4,lr}`. The complete 46-byte successor body hashes to
`7603491ef1e11c9a1163028ac35a5800f53402536eb99633a45fee477948a32c`.
There is consequently no predecessor fallthrough, accessor fallthrough, or
shared successor prologue.

## Exhaustive caller argument setup

For every one of the 115 calls, the qualification suite retains a bounded
record containing the call address, the 16 bytes before the call, and the
four-byte `BL`. The concatenated records hash to
`e19714e9aecd89167144a65f49c4d6ec5bfa6f4dfe6b23b8339270e95a9c0d71`.
A second canonical stream containing each call address and its individual
20-byte-window SHA-256 hashes to
`c2693e4d02cc2f5db9cdd8d1fcc6e660ddac9eddd277e322db783d13f1374dcf`.
Thus a change to any one argument window fails closed even if its branch still
lands at the stock entry.

R1 and R2 are statically classified at all 115 sites. The canonical
`address || minimum-index || maximum-index || stack-offset` records hash to
`641e283917a4da175037b8a0eebc7f6ae93c33b1fc9754d3d6ff7c6aae21182c`.
There are no unresolved R1 or R2 sites. R1 has the following complete
distribution:

| Inclusive index range | Calls |
|---:|---:|
| 1 | 55 |
| 2 | 36 |
| 3 | 14 |
| 3–5 | 2 |
| 3–7 | 1 |
| 3–11 | 1 |
| 4 | 4 |
| 5 | 1 |
| 6 | 1 |

The four computed-index callsites are exactly bounded:

| Call | Proof-window SHA-256 | R1 range |
|---|---|---:|
| `0x00580A7C` | `c6513159fb2210bed62e6c240869100acf2512816e373af29d96d5108d9b7e4c` | 3–5 |
| `0x00580AC8` | `467d589b69acf53887a1f96de29f739155d7954be7fe7d88d280b06dc128a465` | 3–5 |
| `0x00580B14` | `4d96b7ab8313a8e8c90985433a81909af15887f24642382f997adc9c1edaac70` | 3–11 |
| `0x0058191A` | `e61574f553b20eba5d55ac01a3621d65aef8d6806bcd3ca8ff996f49f9ad3bef` | 3–7 |

The first three initialize R4 to zero, increment it, compare it with three or
nine, and form `R1 = R4 + 3`. The fourth clamps R8 to 0–5, initializes SB to
zero, and forms `R1 = SB + 3` only while `SB < R8`.

Every R2 is either `SP` or an aligned `SP + offset` in the active writable
caller stack frame. The exact offset distribution in bytes is: 0 (60 calls),
4 (20), 8 (7), 12 (5), 16 (14), 20 (2), 24 (3), 28 (2), 32 (1), and 36 (1).
This closes the four-byte writable length-output setup for every caller.

## Whole-program R0 provenance

R0 provenance is now closed for all 115 calls, without treating the bounded
call windows alone as semantic proof. `FreeRTOS_CLIProcessCommand` has one
direct caller, `0x0054166E`. That caller loads R0 from the sole stored input
array literal at `0x00541778`, whose value is `0x20071BC8`; it passes R1 as the
output array `0x20071B48` and R2 as 128. The process prologue preserves those
three values as R5/R6/R7.

The exact callback-dispatch window `[0x005848A4,0x005848BC)` is 24 bytes with
SHA-256
`131ab6846509750583837a737d44c940c3fe0ec3c4e758950b7a434b0d9b5f56`.
Immediately before the indirect `BLX`, it executes `R2 = R5`, `R1 = R7`, and
`R0 = R6`. This is the recovered and upstream callback ABI:

```c
BaseType_t callback(char *output, uint32_t output_len, const char *input);
```

Exactly 55 of the 76 authenticated command descriptors select handlers that
call the accessor. At each handler entry, callback R2 is either moved directly
to R0 or saved once in a callee-saved carrier and reloaded before every call.
The complete mapping of registered handler, carrier, and call tuple hashes to
`99ce1c81159593bd505566b495198a1ab9b36a0856dcafd415a9bf904a654eaa`.
The 55 bounded entry-through-first-call prefixes hash to
`73123df6c9ec6f8b14ef8e9ab1ec120318b54b15af90a084d5d2856924572843`;
the 115 `call || carrier || final-halfword` records hash to
`6b67204cb7d5dcf06b1f550020857e2b8b9ecfa67f0177afd4b657130690f044`.

| Carrier | Handlers | Calls | Meaning |
|---|---:|---:|---|
| R0 | 26 | 26 | callback R2 moved directly to R0 |
| R4 | 20 | 42 | callback R2 preserved in R4 |
| R5 | 3 | 18 | callback R2 preserved in R5 |
| R6 | 4 | 16 | callback R2 preserved in R6 |
| R7 | 1 | 7 | callback R2 preserved in R7 |
| R8 | 1 | 6 | callback R2 preserved in R8 |

Six direct-R0 filesystem handlers have a parameter-count guard between the
entry move and call. Their success `BEQ` branches over the only R0-zeroing
exit path and lands at R2/R1 setup. The other 20 direct-R0 prefixes are linear
and at most 14 bytes before the call. Every saved-register call has the exact
final move from its classified carrier to R0. There are no unresolved R0
sites: every accessor input is the same console input array.

## Maximum observed parameter index

The exact retained window `[0x00580AF4,0x00580B1C)` is 40 bytes with SHA-256
`8a19c2866a484db48995aedef803a5d404ec12a03cdae35ac7f466b30a19318f`.
It calls the accessor at `0x00580B14`. The loop increments R4, requires R4 to
remain below nine, and forms R1 as `R4 + 3`, issuing indices 3 through 11.
The exhaustive R1 classification above confirms that eleven is the highest
index among all 115 callers. The accessor itself
has no independent numeric maximum; it stops only at the requested index or
the input terminator.

## Safe characterization of the 128-byte caller hazard

The enclosing command-console task is exactly `[0x00541600,0x0054171C)`, 284
bytes with SHA-256
`c1b9332fb9c932550478f1c2fa80546883aae78259aa887a0ec23ffb007338ef`.
Its complete collect/dispatch portion `[0x0054165E,0x0054171C)` is 190 bytes
with SHA-256
`e0e237ca437e66333fd76287f76ab48dae97a1f2263a35958ba58d7429f3625a`.
The task owns a 128-byte input array and accepts byte indices through 127. Its
exact append window `[0x00541704,0x0054171C)` has SHA-256
`93ed4e2a27efe979fcfe6ec2158443550f9bc1176be6fc7a814e693b78b97284`
and does not append a terminator after the final accepted byte. The upstream
leaf, and therefore this compatibility candidate, has no length argument and
must scan until NUL.

The fully recovered state machine is:

1. R4 starts at zero and is the accepted-byte count.
2. Input byte `0x7F` is converted to backspace, and every received byte is
   echoed.
3. LF or CR dispatches the command. `FreeRTOS_CLIProcessCommand` can be called
   repeatedly for a handler that reports more output; the 128-byte output
   array is cleared after each call.
4. When the handler finally returns false, R4 is reset to zero and the input
   array is cleared completely by `0x0043C0E4` with `(array, 128, 0)`. The
   complete process/output-clear/input-clear window `[0x00541664,0x00541694)`
   hashes to
   `87977ac7163fc502cee45aeba30abdad55598eb15d115b55e8fd65e0d3a2027a`.
5. Backspace at nonzero length decrements R4 and writes NUL at the new index.
6. An ordinary byte is accepted only when `UXTB(R4) < 128`, stored at
   `input[R4]`, and followed by `R4++`. Once R4 is 128, further ordinary bytes
   are ignored.

Because the array is cleared before reuse, payloads of zero through 127 bytes
retain a NUL at `input[length]`. The defect occurs exactly when 128 ordinary
bytes have been accepted since the clear and no backspace reduces the count
before LF/CR: byte 127 overwrites the last remaining NUL. The neighboring
address `0x20071C48` is named independently by a stored literal at
`0x004721F8`, so it cannot be claimed as a spare byte or sentinel without
recovering that other object's ownership.

The host test does **not** invoke undefined behavior. It allocates 130 bytes,
treats the first 128 as the G2 caller's 128-byte logical boundary, places a
space at logical byte 127, and places `Z\0` in the two allocated witness bytes
beyond that boundary. Both the candidate and authenticated upstream oracle
return offset 128 with length one. This safely demonstrates that the stock API
can consume bytes beyond the caller's logical array when the caller fails to
terminate it, without ever asking the host process to read outside allocated
storage.

The smallest authenticated binary repair is one halfword at `0x00541708`:
change `CMP R0,#128` (`8028`) to `CMP R0,#127` (`7f28`). The existing `BGE`
then reserves byte 127 as the terminator, so payloads of lengths 0–127 are
byte-for-byte unchanged and only the unsafe attempted 128th byte is rejected.
Applying only that halfword changes the complete task SHA-256 to
`518c83a818d6cd6eb34a7f1da015010adaf10637e42b7830a3f365adaf28bb5f`.
The test models every safe length and the exact-full/backspace states.

The preceding accessor-only production overlay applied this repair through the
independently compiled two-byte leaf
`open_cfw_freertos_cli_collector_capacity_patch`. The original
halfword is authenticated as `8028`; the extracted source bytes are exactly
`7f28`, SHA-256
`dbf2d8a1ffb886d7964cf470133c8a289aff606c14e6d75fd258678de0f47495`.
The neighboring instruction window becomes `2000c0b27f28c3da`, and the
complete hardened task retains the SHA-256 above.

That two-byte patch relies on the existing static-storage initialization and
post-command full clear. A standalone source redirect has no smaller normal
function boundary: the append block is interior control flow with live R4,
SP, and buffer registers. The smallest self-contained source boundary is the
complete task `[0x00541600,0x0054171C)`, whose source version should explicitly
clear the input array at entry as well as after each completed command and
reserve one byte for NUL. That complete-task boundary is now production
source, so the phase-local interior repair and its appended two-byte leaf have
been removed without weakening the accessor's NUL-termination contract.

## Startup NUL-initialization proof

The retained static input array is zero before the first command. The exact
startup gate `[0x005E4228,0x005E4232)` is the ten bytes
`06480749086001207047`, SHA-256
`bee8bcf07546d7e7b549b10cfe4fc3c6519a6a49dc357d32179df469f5a8e36c`.
Reset calls it at `0x005E4294` and tests its return against zero. The gate
returns one, so reset calls the scatter loader at `0x005E429C`.

The authenticated scatter record `[0x0075D3C8,0x0075D3E0)` hashes to
`2a52162870b1f1b036f1769e75dabcf475f17eb6c37c85ffcabcb9dcfd064e15`.
It resolves to the 56-byte zero handler `[0x005FA01E,0x005FA056)`, SHA-256
`8b74bda81d1262930007b87bd980ccaebc6028472d7dd7413c20cc1f281b1b67`,
and zeroes `[0x20004558,0x20075048)`. That range fully contains the console
input array `[0x20071BC8,0x20071C48)`. This startup proof, the source task's
explicit entry initialization, and its post-command full clear establish the
NUL precondition for the production accessor with the 127-byte payload bound.

## Dual-toolchain target closure

The candidate suite compiles the candidate twice. The phase-local accessor
qualification also compiled the separate production source and then-current
capacity fragment twice, with Thumb-v7E-M, `-O2`, ROPI,
function/data sections, no builtins, no unaligned access, and no unwind-table
generation. Apple clang 21.0.0 at `/usr/bin/clang` and Linux/Homebrew clang
22.1.8 at the exact root `/home/linuxbrew/.linuxbrew/bin/clang` have separate
profile pins. The independently generated profile artifacts currently happen
to be byte identical:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| complete ELF object | 1,064 | `aeef70e13e386f34dd78548a0dbfe211fb883ee2b1e5146f209e7bef78318832` |
| isolated function section | 252 | `7b77ccc3441cb8e725fa8a97a8197e0f993a00456925c6eb0126e77fb00f9914` |
| `.ARM.exidx` | 8 | `01acecb507abfe1a354aa8064f4af5d3f1acd019e37db3c11c97523b71c76e9d` |

The object contains exactly one nonempty executable section, no allocated
writable data, no undefined symbols, and no text relocations. Its sole
relocation is offset zero, type 42 `R_ARM_PREL31`, from the function's
`.ARM.exidx` section to the local function section. The second exidx word is
exactly `0x00000001` (`CANTUNWIND`). This metadata is suitable for the existing
strict relocated-leaf extractor policy, which authenticates and deliberately
discards this non-executable unwind record.

The following raw-object pins record the phase-local accessor/capacity
qualification. The capacity object is no longer a production input; the
accessor object and extracted text remain current:

| Profile | Accessor object | Capacity object |
|---|---|---|
| Apple Clang 21.0.0 | 1,140 / `eb96bde116aacf0b7c86119b4b5339bbb0ec843ecc7102266bc7a5245a9a77a2` | 540 / `e2b931288aa86668af5e8b87288bc041ec8c0c96dc9f730891433f9fafcf2380` |
| Linux Clang 22.1.8 | 1,120 / `76a9d2f7de4d6c98902b84e1ad535f6bc643ae45a4676794e8e3345f41f5b263` | 540 / `e2b931288aa86668af5e8b87288bc041ec8c0c96dc9f730891433f9fafcf2380` |

## Accessor production and complete-console closure

Accessor promotion remains complete and fail-closed. The 252-byte accessor has no text
relocations and retains the authenticated/discarded
`R_ARM_PREL31`/`CANTUNWIND` metadata contract. Its stock entry is a complete
`B.W` plus NOP-fill replacement. The later complete-console promotion removed
the exact two-byte capacity copy, its fixed-span ownership, and its appended
leaf; the source-owned byte consumer now enforces `length < 127`. Candidate
filename and symbol remain absent from production registration.

The table below is therefore a phase-local record of the accessor-only
milestone, not the current combined artifact identity:

| Profile | Overlay | Apollo-main component | Core-source package |
|---|---|---|---|
| Apple Clang 21.0.0 | 123,454 / `9e5004af49fb14a22e7e7ed7357e4c10f87dc8da3a7fb4d7b97fcffcde804c43` | 3,646,850 / `8722e5565bf54dade66fb751155c11ebd128d7a12853e3e4b8671c3c97807827` | 4,425,304 / `f2688fb35061283c05e9eb165d4f3eeb2cb2c4abd18cd28d074e58cb9da021db` |
| exact-root Linux Clang 22.1.8 | 125,278 / `a0a520069e497613b397af1d7327752201ced44c876d6925a7561ae45c91fa7c` | 3,648,674 / `8c477d28a9f58feaf722bd1e00b9767a8ca745ba618515d46339271cd0288c1a` | 4,427,128 / `5598cb1f2a3b9a8b6101f61afcc5e24de54b01c3d5aa45396bf161344b3618bb` |

Current assembled Apple and Linux scans require exactly one external ingress to the
accessor range: the stock-entry `B.W`. They reject every additional branch,
interior target, and aligned even or Thumb-form stored pointer. The former
capacity function, patch, and manifest regions must be absent. Remaining work
is expansion into the retained interpreter and proprietary commands, not the
console task itself.

This candidate makes no claim that the exact historical G2 checkout was the
selected 2021 source commit. The official source pair is the authenticated
openCFW compatibility choice, and this leaf's retained behavior is identical
across the compatible classic FreeRTOS+CLI lineage.

## Reproduction

```sh
cd openCFW
python3 -m unittest -v tests.test_freertos_cli_get_parameter_candidate
python3 -m unittest -v tests.test_runtime_freertos_cli_get_parameter

docker exec -w /Users/kalani/Repo/SybilSightABCD/openCFW \
  -e OPENCFW_CLANG=/home/linuxbrew/.linuxbrew/bin/clang \
  -e OPENCFW_TOOLCHAIN_PROFILE=linux-clang \
  opencfw-linux-llvm \
  python3 -m unittest -v tests.test_freertos_cli_get_parameter_candidate \
    tests.test_runtime_freertos_cli_get_parameter
```

The focused suite performs no signing, connection, reset, erase, program, or
flash operation.
