# G2 FreeRTOS+CLI console-task source-candidate audit

## Result and scope

The command-console task in the authenticated G2 2.2.6.10 Apollo image is a
closed 284-byte Thumb function at `[0x00541600,0x0054171C)`, SHA-256
`c1b9332fb9c932550478f1c2fa80546883aae78259aa887a0ec23ffb007338ef`.
Its registration fanout, receive ABI, echo/edit state machine, command
continuation loop, buffer ownership, display seams, and initializer topology
are now recovered.  The original qualification source is
`runtime_freertos_cli_console_task_candidate.c`.

That original candidate remains **production-excluded**. A separately named
GPL-3.0-only production implementation is now split across seven independently
placeable source leaves and replaces the complete stock task span. Production
does not register the candidate source or symbol, and the authenticated
FreeRTOS-Plus-CLI snapshot also remains excluded. The former standalone
two-byte collector-capacity leaf has been removed because the source-owned
byte-consumer now enforces the 127-byte payload bound directly.

The candidate deliberately makes three source-level safety properties
explicit:

1. both 128-byte arrays are cleared when the task starts;
2. input byte 127 remains the terminator, so at most 127 payload bytes are
   accepted; and
3. a receive result other than exactly one byte is discarded.

The first two express the already-reviewed whole-task replacement policy.  The
third closes a stock error-path defect described under “Receive failure”.

## Authenticated boundary and entry topology

| Object | Span | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| input callback / predecessor | `[0x005415E6,0x00541600)` | 26 | `ee4e0f209aee689ec87471e940a88d9cf1a1aea323b342c3a72f87043faaeb1e` |
| console task | `[0x00541600,0x0054171C)` | 284 | `c1b9332fb9c932550478f1c2fa80546883aae78259aa887a0ec23ffb007338ef` |
| console initializer | `[0x0054171C,0x0054176A)` | 78 | `70ee9cc99f94d99e53017290b5aedfac52d59b8fae2e3e9435622e388134dfe5` |
| task literal table | `[0x0054176C,0x00541790)` | 36 | `0c59069ad8144fd2e3712fc42a3e63ba6e8462f657c42f39155d6b768cf49dba` |

An exhaustive byte-granular 32-bit pointer scan finds exactly one value into
the task: initializer storage `0x0054178C` contains Thumb pointer
`0x00541601`.  There is no external `BL`, `B.W`, narrow `B`, or conditional
branch into the function.  A naive halfword scan reports `0x005415A4 ->
0x00541618`, but bytes `c0 b3` are the low halfword of aligned literal word
`0x2037B3C0` inside authenticated data pool `[0x0054157A,0x005415B4)`, SHA-256
`d672f0e669a363d991186dfaf619e555ea115bc373776000166151bccfeeeef3`.
It is not executable control flow.

The task has the CMSIS/FreeRTOS entry ABI `void task(void *argument)` and does
not inspect `R0`.  Its prologue saves `R2,R3,R4,R5,R6,LR`; `R4` is the input
length and begins at zero.

## Complete retained ABI seam list

| Stock object | Recovered ABI and task use |
| --- | --- |
| 22 setup functions below | `void setup(void)`; return ignored; each body only loads descriptors and calls `FreeRTOS_CLIRegisterCommand` |
| display string `0x005415C2` | `void display_string(const char *text)`; calls `strlen`, then sink selector 1; used for prompt and output |
| display byte `0x005415D8` | `void display_byte(uint8_t value)` under AAPCS; sends one stack byte to sink selector 1 |
| ring read `[0x0057E136,0x0057E220)` | `uint32_t read(void *handle, void *destination, uint32_t length, int32_t timeout)`; task requests `(handle,&byte,1,-1)` |
| CLI processor `[0x005847FE,0x005848FC)` | `int32_t FreeRTOS_CLIProcessCommand(const char *input, char *output, uint32_t output_length)`; task passes 128 and repeats while return is nonzero |
| fill `[0x0043C0E4,0x0043C14A)` | nonstandard released order `(destination,count,value)`; task uses `(array,128,0)` and ignores the returned original destination |
| receive-handle word | `0x200748BC`; dereferenced immediately before read |
| output array | `0x20071B48`, 128 bytes |
| input array | `0x20071BC8`, 128 bytes |
| transport sink | `0x0055E7FA`, selector 1, buffer, length; reached through the two display helpers |

Pinned dependency hashes are:

- display string: `c0046e8521fae144d8ff6cb85288d75d75c4ab7e9f5f58a56f47643906137367`;
- display byte: `0a186e5409fd503e7170317faaeb2f527c7f31dfce0d30f4ace9909ef54dbe23`;
- ring read: `c22d5821764704899a68d46b9b1bf3dbc79294dcd354c6377467fa051add4b82`;
- CLI processor: `a276b358abd3ec722f4da8e17928590941d16f06ae92ad1375a1baf963e2893d`;
- fill: `34da1a99d5cb56ca41cfaff98190ced2a7767f53cd95c53c504009566e9ca10a`.

The CLI processor is already identified as MIT-licensed
FreeRTOS+CLI V1.0.4-compatible source plus G2’s authenticated blank-input
patch.  This task candidate therefore calls that source-compatible ABI rather
than decompiling the interpreter again.

## Exact registration fanout

Instructions `0x00541604..0x0054165B` make these 22 calls in order.  The setup
bodies contain all 76 calls to `FreeRTOS_CLIRegisterCommand` at `0x005847AC`.

| Entry / span | Commands in order | Count | Complete-body SHA-256 |
| --- | --- | ---: | --- |
| `0x57E626..0x57E665` | `reset`, `clear`, `enterProductMode`, `exitProductMode`, `SetGPIO`, `ResetGPIO`, `ProductControlCodec`, `ChargerControl`, `ReadDieId`, `ReadChipId` | 10 | `e9bff22d2c4858dd367cbe53769e56bd344727a552339726a83b3b3895f95394` |
| `0x57E810..0x57E825` | `info`, `AT^thread`, `AT^dump` | 3 | `f57208fb0938240e05e508bfb4248d7d7db290eb940876fa766128d2fa24fa8e` |
| `0x57FF40..0x57FF9D` | `ls`, `cat`, `rm`, `cd`, `mkdir`, `touch`, `pwd`, `mv`, `md5`, `df`, `free`, `rename`, `xip`, `file2xip`, `xip2file` | 15 | `2928d98b67f576aa5a3112fecd80be2be92bb08167ec56bc5d4012ffff0c7ac9` |
| `0x580392..0x5803E9` | `syncTest`, `input`, `dispStop`, `dispExit`, `dispBlockEn`, `dispBlockCancel`, `dispStart`, `udata`, `pdata`, `dispReflash`, `singleStart`, `singleStop`, `singleReflash`, `sinput` | 14 | `e9e11b71d7a953f40add22fc6db7e2c140e512cd6e83358c653982bd00feb044` |
| `0x5807C0..0x5807D5` | `logcat`, `logf`, `AT^LOGTYPE` | 3 | `b566ae9eb61d5562b53453d352def664bd39b47f7b96f70eecdf5d0c6f355ba3` |
| `0x580C04..0x580C0D` | `imu` | 1 | `04d951f1cba903cb2425f8cddc06348aa7b5ed23712701a81222234df00ce437` |
| `0x580FEC..0x580FFB` | `codec`, `audm` | 2 | `ea8fb4e126f02084ed16fb26ec275bb4cc1401ad3136bb9bcc6d53fea29f8efb` |
| `0x5810D8..0x5810E1` | `AT^psn` | 1 | `94d6bd6b2fc3984de1987419124a4b7f9818b89b9883f942b25396deccc70bb6` |
| `0x581136..0x58113F` | `pdm` | 1 | `a5ec3697352cd3f00c5a554f5daf143708b4f59c2369fef18f3f85f8a8ee607c` |
| `0x581644..0x58167D` | `AT^BleGetMac`, `AT^BLECleanBond`, `AT^BLES`, `AT^BLEM`, `AT^BLEMC`, `AT^BLERingSend`, `AT^EM9305`, `AT^BLEADV`, `AT^BLE_KEEPCONNECT` | 9 | `27a190f2ff277e8f9f368cdb0de7f82dfce6b2c5a3c9c305b48604ea6de75ed7` |
| `0x58183A..0x581843` | `xmodem` | 1 | `fe29b54f58fdaf01bf7500576797af8c199bde22d539a23f961aa8124a84e83a` |
| `0x581960..0x58196F` | `alert`, `dashboard_layout` | 2 | `7544cd18573008959e85e849123a12417746c168d2877a8436254b2e875d0d84` |
| `0x581D60..0x581D6F` | `tp`, `weardetect` | 2 | `0b74d5cb46e5b1bca973d0197dbe3347b69752841d3ef10475d1ad19369c40f5` |
| `0x5827D0..0x5827EB` | `teleprompt`, `translate`, `conversate`, `legalregulatory` | 4 | `9adfec854f08f1068db5b1a32dc14964562f0b566e8e75195878cd3750a46c9d` |
| `0x5836B8..0x5836C1` | `terminal` | 1 | `4676a5fe42ac524ae3e0f9c1cecd44b23616bde1c18d741146bc77f97ec58a19` |
| `0x583CEC..0x583CF5` | `set` | 1 | `7e0e6a3cf8169401b0615955c79a1db8d30ce349fcb8c54ef34e6c502bf83091` |
| `0x583F74..0x583F7D` | `buzzer` | 1 | `587c3ca5137a0a107b6406181eabdd6ac3abfd5003292e9fba521f5b01dd2a2f` |
| `0x5840F4..0x5840FD` | `gpio` | 1 | `9a313a0b24e3397f40b3999b268716d2943115ded644c5bd8b635f715bbc58b2` |
| `0x5841EE..0x5841F7` | `box_force_out` | 1 | `e3a09eef8aa716e15de7634d5471832dedcd706e0c9c4e4ee57f3b075a6844c7` |
| `0x584320..0x584329` | `SetLanguage` | 1 | `6a51a0e74eecbf9f31de152e6bec087f77fe35896ce7aa4fb920bf557dd13c9d` |
| `0x584430..0x584439` | `onboarding` | 1 | `cf6853f937ccc3ec295dade574912bd84597651dc5c5ffe2731f1f2587491ca8` |
| `0x584702..0x58470B` | `get` | 1 | `de3ae5de4bd36558588b8156ca0011f877dc2c0cb3bee65a01b42d4b3943ddca` |

## Complete task instruction recovery

The setup/prologue is exact:

| Address | Instruction / effect |
| --- | --- |
| `0x541600` | `PUSH {R2,R3,R4,R5,R6,LR}` |
| `0x541602` | `MOVS R4,#0` |
| `0x541604..0x541658` | 22 consecutive `BL` instructions to the registration entries above |
| `0x54165C` | branch to receive at `0x541694` |

The complete collect, edit, dispatch, and output loop is:

| Address | Recovered instruction-level behavior |
| --- | --- |
| `0x54165E` | `ADR R0,0x54176C`; prompt pointer selects bytes `"\n#\0"` |
| `0x541660` | call display-string |
| `0x541664..0x54166E` | load output `0x20071B48`, input `0x20071BC8`; call processor `(input,output,128)` |
| `0x541672` | copy processor result to `R4` temporarily |
| `0x541674..0x541676` | display the output buffer even when result is zero |
| `0x54167A..0x541680` | clear all 128 output bytes using `(output,128,0)` |
| `0x541684..0x541686` | repeat at `0x541664` while the processor result is nonzero |
| `0x541688` | reset accepted length to zero |
| `0x54168A..0x541690` | clear all 128 input bytes using `(input,128,0)` |
| `0x541694..0x5416A0` | call ring read `(*0x200748BC,SP,1,-1)`; returned count is ignored |
| `0x5416A4..0x5416AE` | if received byte is DEL `0x7F`, replace it with backspace `0x08` in the stack slot |
| `0x5416B2..0x5416B6` | echo the canonicalized byte before any control processing |
| `0x5416BA..0x5416C0` | LF branches to prompt/dispatch |
| `0x5416C2..0x5416C8` | CR branches to prompt/dispatch |
| `0x5416CA..0x5416D0` | redundant second CR comparison/branch; unreachable after the prior CR branch |
| `0x5416D2..0x5416E0` | branch to edit for BS or DEL; the explicit DEL arm is unreachable after canonicalization |
| `0x5416E2..0x5416E8` | if `UXTB(length)==0`, return to receive |
| `0x5416EA..0x5416F4` | decrement length and write NUL at the new input index |
| `0x5416F6..0x5416FE` | emit space then backspace; the common echo already emitted the first backspace |
| `0x541702` | return to receive |
| `0x541704..0x54170A` | compare `UXTB(length)` with 128; stock rejects ordinary bytes only at length 128 |
| `0x54170C..0x541716` | store ordinary byte at `input[length]` |
| `0x541718` | increment length |
| `0x54171A` | return to receive |

Thus every byte is echoed.  DEL is echoed as backspace, not as `0x7F`.
Backspace at zero produces only that common echo.  Backspace at nonzero length
produces backspace, space, backspace and restores a NUL at the shortened end.
LF and CR both echo first, emit exactly `"\n#"`, invoke the processor at least
once, emit/clear every output chunk, and clear the input only after the final
false result.

## Initializer and storage ownership

Initializer `[0x0054171C,0x0054176A)` installs display handler Thumb pointer
`0x005415C3`, installs input-callback pointer `0x005415E7`, creates a transport
object through `0x0057DEEA` with observed register/stack tuple
`(0x800,1,0,0,0)`, and stores the returned handle at `0x200748BC`.  It then
calls CMSIS `osThreadNew` at `0x004490E2` as
`osThreadNew(0x00541601,NULL,0x0075B958)` and stores the returned thread handle
at `0x200748B8`; null reaches the retained assertion/fatal path.

The 36-byte `osThreadAttr_t` at `0x0075B958` is the nine-word tuple:

```text
name=0x0078C614, attr_bits=0,
cb_mem=0x200724C0, cb_size=0x70,
stack_mem=0x2036EE40, stack_size=0x1000,
priority=0x18, tz_module=1, reserved=0
```

The neighboring input callback writes incoming transport data to the same
object through `0x0057E05E`; the console task is its blocking reader.

## Receive failure and explicit candidate policy

Focused disassembly of `[0x0057E136,0x0057E220)` proves that the read function
can return zero without copying if the wait returns and the ring remains
empty.  The stock task ignores `R0` and immediately consumes `SP[0]`:

- before the first successful read, that byte is the low byte of entry-time
  saved `R2`, which the thread ABI does not define for the callee; and
- after a successful read, a later zero result reuses the previous byte.

There is therefore no deterministic C value that can reproduce the first
failure, and replaying stale input is unsafe.  This is not an unresolved
normal-path ABI: the read argument order, width, timeout, and successful
one-byte result are all closed.  It is an explicitly classified stock error
path.  `open_cfw_freertos_cli_console_poll_once_candidate()` consumes a byte
only for return count one and otherwise leaves state/output unchanged.

## Candidate and differential verification

The source separates the bounded state transition from the infinite task:

- `open_cfw_freertos_cli_console_state_initialize` binds and clears arrays;
- `open_cfw_freertos_cli_console_register_groups_candidate` preserves the
  exact 22-group order;
- `open_cfw_freertos_cli_console_consume_byte_candidate` implements one
  canonicalized byte transition;
- `open_cfw_freertos_cli_console_poll_once_candidate` covers the exact receive
  tuple and safe count policy; and
- `open_cfw_freertos_cli_console_task_candidate(void *)` preserves the thread
  entry ABI and ignores its argument.

The native host oracle records every display byte/string, processor input and
output length, group-registration call, and receive call.  Tests cover:

- exhaustive sequences through length four over ordinary bytes, BS, DEL, LF,
  and CR against an independent Python state machine;
- three processor output chunks with positive, negative, and zero
  continuation returns;
- exact prompt/output/clear ordering;
- backspace at zero/nonzero and DEL canonicalization;
- all 128 attempted ordinary input bytes, retaining byte 127 as NUL while
  still echoing the rejected final byte;
- exact `(handle,&byte,1,-1)` receive ABI and zero-count discard;
- all 22 registration groups and all 76 authenticated descriptors;
- boundary/helper/body hashes, initializer attributes, and sole real entry
  pointer; and
- native plus `thumbv7em-none-eabi` warning-clean compilation and explicit
  production exclusion.

Both reviewed target profiles compile twice deterministically with the same
658 text bytes, seven 8-byte EXIDX records, 29 exact retained undefined
symbols, and 53 relocations:

| Profile | Complete object | Entry/state-machine text sizes |
| --- | --- | --- |
| Apple clang 21.0.0 | 6,000 bytes, `ad0ad14954ff3d75f7df2abe418a189da6388b9355ed817af6d74de2c2c9230d` | task 40, poll 60, consume 96, register 94, initialize 28, process 64, fill 276 |
| Linux Homebrew clang 22.1.8 | 6,000 bytes, `be786a9ac53ec9adf5d12a14ec1846c13f30852e156c2dbcc7d8e67b5fe82e9d` | task 40, poll 60, consume 96, register 94, initialize 28, process 64, fill 276 |

The helper isolation is intentional: the compiler cannot duplicate the clear
and process loops into the thread entry.  Five of seven text sections are
byte-identical across profiles; the two profile-specific sections and both
complete objects are independently pinned by the test.

## Production promotion

The promotion binds the descriptive retained symbols to the fixed SRAM
objects and reviewed callable seams above, while keeping the stock
FreeRTOS+CLI interpreter ABI at `0x005847FE`. It does not import or claim
source ownership of the interpreter, the 22 proprietary setup functions, the
76 command descriptors, or their handlers. The seven production leaves own
only the recovered G2 task glue: fill, state initialization, ordered group
registration, command processing, byte consumption, one receive iteration,
and the CMSIS/FreeRTOS task entry.

The complete `[0x00541600,0x0054171C)` entry is redirected to the source task
and NOP-filled; the initializer's sole stored Thumb pointer at `0x0054178C`
remains unchanged and continues to enter `0x00541601`. Production preserves
the exact 22-group/76-descriptor order and the 128-byte interpreter call
boundary. It deliberately differs from stock in two reviewed safety cases:
ordinary input stops at 127 bytes so byte 127 remains NUL, and a received byte
is consumed only when the retained read returns exactly one. The old interior
capacity patch and its appended two-byte leaf are absent from the resulting
production configuration and manifest.

The clean-room source is GPL-3.0-only G2 glue. The classic MIT
FreeRTOS-Plus-CLI snapshot selected by openCFW remains a compatibility oracle,
not proof of Even Realities' historical checkout, and is not linked into this
production closure. Whole-image entry/interior scans and the focused
production suite cover the redirect, stored-pointer topology, relocations,
fixed SRAM bindings, candidate/snapshot exclusion, and both safety policies.

| Profile | Overlay | Apollo-main component | Core-source package |
|---|---|---|---|
| Apple Clang 21.0.0 | 124,212 / `913d0b39126eac6d13ac05baa44c745cd2a0c7317957293e34bbf418547d96bd` | 3,647,608 / `cbe9f7361b47ef2150f2c3a01fca6f03f82e1ff3e2c805b7bbe774ba2154a354` | 4,426,062 / `0c257168dfc07a39e4603847329f6ac542d093719f0ea9c5a4cf904707b83670` |
| exact-root Linux Clang 22.1.8 | 126,032 / `bdc8bf69d75b7ff8354e12aa392416956a2afa04442488e7653e79b89ce62f1f` | 3,649,428 / `d90824df529385ae5fba464c88b0c1e4e7d145a939024632c0806c4462d68d00` | 4,427,882 / `3aa279193bf67b50a75ad5490a8cd2e22ffb32d36f6de1e5befe0a11368fe743` |

Exact package ownership is 124,987 / 87,714 / 4,213,361
source/generated/opaque bytes for Apple and 126,868 / 87,653 / 4,213,361 for
Linux. The overlay configuration contains 640 functions, 589 patch sites, and
71 relocated leaves; the canonical manifest tiles 890 regions.

Qualification authorizes no signing, flashing, or hardware execution.
