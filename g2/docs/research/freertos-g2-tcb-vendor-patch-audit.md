# G2 FreeRTOS V10.5.1 TCB vendor-patch recovery

Status: minimal patch recovered, authenticated, and target-layout compiled;
not yet a wholesale `tasks.c` production admission  
Target: official G2 `s200_v2.2.6.10` Apollo-main application

## Result

The formerly opaque 112-byte TCB difference is now represented as a complete,
minimal source patch over the authenticated FreeRTOS-Kernel V10.5.1 base:

[`g2-tcb-v10.5.1.patch`](../../components/shared/freertos/g2-tcb-v10.5.1.patch)

The patch has exactly three semantic changes:

1. insert one `uint32_t` stack-depth word after `TCB_t.pcTaskName[32]`;
2. mirror that word in the opaque public `StaticTask_t` declaration;
3. assign the incoming creation depth in `prvInitialiseNewTask`.

Under the recovered G2 configuration, the pristine 108-byte structures become
112 bytes and reproduce every observed later field offset. No other TCB field,
alignment rule, or creator algorithm needs a vendor modification to explain
the stock layout.

This classifies the code accurately:

- base algorithms and structure conditionality: official FreeRTOS-Kernel
  V10.5.1, MIT, commit
  `def7d2df2b0506d3d249334974f51e427c17a41c`, tree
  `7496dfa815c3cea2f45a090c6e92d113f494b930`;
- four-byte addition and its assignment: vendor-derived semantic
  reconstruction from authenticated G2 machine code;
- original field name, comments, private repository, and vendor patch commit:
  unobservable and deliberately not invented.

The patch is 1,730 bytes with SHA-256
`cf8c457153b75ad6a3163b9b6e6873e476e03537bb4534c9c8e4557de0eb4eb3`.
It applies cleanly to the two pristine CRLF source files with
`git apply --ignore-space-change`.

## Upstream provenance boundary

The authenticated comparator is the official annotated `V10.5.1` tag:

| Input | Bytes | Git blob | SHA-256 |
|---|---:|---|---|
| `tasks.c` | 223,695 | `d97085d8736905c1eeb9d9e871c81e5970ee70ed` | `14020d617b96dd2814e1211f6e3b645bcf5e2bd3179c23fe7dd16bc666fe9463` |
| `include/FreeRTOS.h` | 51,577 | `4ac433230075cd13d8af0da1ae6c64b4b4153ab2` | `03e9c94aba57e3cf7f4f73bc2d3eb4a96ae38f3425eedb5450622ca286475a0b` |

Neither file contains an equivalent stored stack-depth member. As a negative
cross-check, official FreeRTOS-Kernel `main` at commit
`ce221a8bb468e462ca6b435cef66a9636e00baf4` (reviewed 2026-08-10) also has no
TCB member assignment from `uxStackDepth`; it only consumes the argument for
stack allocation, filling, bounds, and port initialization. This does not
prove that no public third-party fork ever implemented a similar diagnostic
field. It does prove that attributing the G2 word to official FreeRTOS would
be incorrect.

## Stock proof

The analyzer authenticates four contiguous stock functions:

| Function | Stock span | Bytes | SHA-256 |
|---|---|---:|---|
| `xTaskCreateStatic` | `[0x00454820,0x004548BA)` | 154 | `21c10ddaf25950d84acbcf302f2de18d3471dd5321c4cd7aa50dcc8a6f29debe` |
| `xTaskCreate` | `[0x004548BA,0x00454938)` | 126 | `d4210ea6c22d8fb0aee4d89d3a1666874a489e77516041d6946bef9a05058b21` |
| `prvInitialiseNewTask` | `[0x00454938,0x004549FC)` | 196 | `54a87da84dbcdf7871563962b44490d635a2a924225fed68b99ccce811b397b2` |
| `prvAddNewTaskToReadyList` | `[0x004549FC,0x00454AAE)` | 178 | `4e765b4faa584167eb8aa1e91ab46fb3383dbfb24ebe4adbd5a4909943706ff4` |

The static creator asserts a `0x70` object size, clears `0x70` bytes, stores
the stack base at `+0x30`, and writes allocation provenance at `+0x6D`. The
dynamic creator separately allocates and clears `0x70` bytes and uses those
same offsets.

The initializer fills `stack_depth * 4` bytes with `0xA5`, calculates and
aligns the descending-stack top, then stores the same depth argument at
`+0x54`. Only afterward does it copy at most 32 name bytes at `+0x34` and
force the terminator at `+0x53`. It bounds priority at 56 and initializes base
priority at `+0x60`. The following ready-list helper assigns the TCB number at
`+0x58`.

Those independent operations rule out `pxEndOfStack` at `+0x54`, padding,
or an unrelated four-byte configuration field. The word is the creation stack
depth, in `StackType_t` units.

## Reproduced layout

Applying the patch and compiling the actual patched `StaticTask_t` declaration
for Cortex-M55 produces:

| Offset | Field |
|---:|---|
| `+0x00` | top-of-stack pointer |
| `+0x04` | state `ListItem_t` |
| `+0x18` | event `ListItem_t` |
| `+0x2C` | current priority |
| `+0x30` | stack-base pointer |
| `+0x34` | task name, 32 bytes |
| `+0x54` | recovered G2 stack depth |
| `+0x58/+0x5C` | trace numbers |
| `+0x60/+0x64` | base priority / mutexes held |
| `+0x68/+0x6C` | notification value / state |
| `+0x6D` | static-allocation provenance |
| `+0x6E..+0x6F` | tail padding |

The compile probe asserts every listed public `StaticTask_t` offset and total
size `0x70`. Six focused tests also verify patch applicability, source and
stock identities, analyzer mutation rejection, and the target compile.

## Consequence for OpenCFW

The TCB size mismatch is no longer an opaque reverse-engineering blocker or a
reason to guess at a different FreeRTOS release. It is a bounded vendor patch
layer over the already selected V10.5.1 commit. That shortcut can now be used
when compiling additional task getters and task-core candidates: use the
official V10.5.1 algorithm, apply this one field delta, and separately bind
the recovered globals, trace hooks, port, and application hooks.

The patch is intentionally not production-linked yet. A full `tasks.c`
admission still requires fixed-address scheduler global migration or adapters,
Apollo STIMER tick/tickless glue, exact trace macros, application hooks, and a
complete resolution of the included API switches. Those are independent
integration seams rather than unknown third-party provenance.

## Reproduction

```sh
python3 openCFW/tools/analyze_g2_freertos_tcb_patch.py
make -C openCFW freertos-g2-tcb-patch
```

No package was signed or flashed and no hardware was accessed.
