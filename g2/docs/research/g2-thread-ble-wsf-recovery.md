# G2 BLE WSF thread recovery

This note closes the product translation unit identified by the retained path

```text
D:\01_workspace\s200_ap510b_iar_git\platform\threads\thread_ble_wsf.c
```

in the authenticated G2 `s200_v2.2.6.10` OTA. The original product source has
not been recovered and no vendor implementation was copied. Three new
MIT files now implement the twelve-entry behavioral surface with
injectable provider and diagnostic seams. No production bytes are replaced.

## Result

The complete physical TU is `[0x004D0A4C,0x004D0D24)`, 728 bytes, SHA-256
`497f72ef17c0ae3607a255057bcfe4bc9f0599ebfab9fea8d40b56923db94e49`.
It contains twelve functions / 656 code bytes followed by one 72-byte literal
pool. The next unrelated function begins at `0x004D0D24`; preceding syscall
and product bodies end before `0x004D0A4C`.

| Function | Stock range | Bytes | SHA-256 | Name status |
|---|---:|---:|---|---|
| `threadBleWsfTask` | `[0x004D0A4C,0x004D0A68)` | 28 | `212af394032df8abae02bbdecc982905309fc63478aa0c590e05ec63eca1a98f` | inferred from task-entry ABI |
| `threadBleWsfStart` | `[0x004D0A68,0x004D0A70)` | 8 | `0f67a90b5f86e6f08ad48153e5379562cc2e34454b76e5c9fdf25d0de1e3817d` | inferred wrapper |
| `_thread_resource_init` | `[0x004D0A70,0x004D0AE0)` | 112 | `13d7c0fe434b5f98ff72c255cfaabca64257f6395e81430419c2728455aa3d7a` | exact retained name |
| `threadBleWsfLoopInit` | `[0x004D0AE0,0x004D0AE2)` | 2 | `c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8` | inferred lifecycle role |
| `threadBleWsfEnter` | `[0x004D0AE2,0x004D0AEC)` | 10 | `c324ea6fd1d7bca8c1bcb61f5048ee346f97f665c63bffa57ad8bbc52849f7be` | inferred lifecycle role |
| `threadBleWsfReady` | `[0x004D0AEC,0x004D0AF6)` | 10 | `6f42cf1049dc9a1ff119de4bc5269cf5ef4ad6ceca3d7cd56bf34246143751e6` | inferred lifecycle role |
| `threadBleWsfInit` | `[0x004D0AF6,0x004D0B1C)` | 38 | `1e43ba9e9c0aacb205409392d2c963d6eb2d30554d96febb96b6d9cfbc685de9` | inferred public lifecycle name |
| `threadBleWsfDeinit` | `[0x004D0B1C,0x004D0B36)` | 26 | `a14fb6c1d8ad086fd051734b88bde37423c8690d4a345fe29facf89282e5552b` | inferred public lifecycle name |
| `threadBleWsfTakeTxReady` | `[0x004D0B36,0x004D0B64)` | 46 | `bebc400de5be8b2d37039b6ed7e9a2d3a02739541f98f1f2a5046f5a21869c98` | inferred private helper |
| `thread_ble_wsf_wait_tx_ready` | `[0x004D0B64,0x004D0C2C)` | 200 | `3a213ff23a1f6a470149f8aca60d7fccd5af2ffb27bf11e388ea6646c19f344e` | exact retained name |
| `threadBleWsfWaitOnce` | `[0x004D0C2C,0x004D0C36)` | 10 | `b90ccc851d1ba4063be591d8c122082647ee34c9f4b442ea42fd1834302d7fcb` | inferred wrapper |
| `thread_ble_wsf_tx_complete_notify` | `[0x004D0C36,0x004D0CDC)` | 166 | `ccc45829df3264820dc0de6fb1fdbe1e3cb1119cd6706313323e8a5818075fe3` | exact retained name |

The ordered body concatenation SHA-256 is
`514c822a09a496897861fd8f81603e95b07c83e7b8c401779f5ad4973d611d9f`.

## Task and state ABI

The IAR/CMSIS `osThreadAttr_t` object occupies
`[0x0075B838,0x0075B85C)`, 36 bytes, SHA-256
`3de23514e8e1fec1c26809144605f5bdb8cee48f949a5a78839f756627d8d715`.
Its decoded fields are:

| Field | Value |
|---|---:|
| name | `"ble_wsf"` at `0x0078EBA4` |
| attribute bits | `0` |
| static thread control block | `0x20072140` |
| control-block bytes | `0x70` |
| static stack | `0x20043A98` |
| stack bytes | `0x4000` |
| priority | `0x31` |
| trust-zone module | `1` |
| reserved | `0` |

The product control block is rooted at `0x20004068`. Two offsets are proven:

- `+0x08`: CMSIS thread handle;
- `+0x14`: transmit-ready semaphore handle.

No exact whole-structure size is claimed from these two uses alone.

`threadBleWsfInit` passes task entry `0x004D0A4D`, null argument, and the
attribute object to stock `osThreadNew` at `0x004490E2`, stores the returned
handle at `+0x08`, and enters the product fatal loop if creation fails.
`threadBleWsfDeinit` invokes the paired product resource hook, terminates a
non-null thread with `osThreadTerminate` at `0x004491FE`, and clears the
handle. Neither lifecycle wrapper has a surviving direct caller or stored
entry in this image; both remain linked as part of the product object.

## Startup and dispatch

The task entry performs this exact sequence:

1. enter product lifecycle state `9` through `0x004C9B86`;
2. initialize the semaphore and paired resource through
   `_thread_resource_init`;
3. call the one-instruction `appBleStart` wrapper at `0x004D0A68`;
4. call the retained no-op lifecycle hook;
5. mark lifecycle state `9` ready through `0x004C9BE2`;
6. call `WsfOsDispatcher` at `0x0052B9D0` forever.

This closes the previously exterior `appBleStart` call at `0x004D0A6A` and
places the product BLE startup under a concrete CMSIS task root.

## Transmit-ready flow control

`_thread_resource_init` calls
`osSemaphoreNew(max_count=1, initial_count=1, attr=NULL)` at `0x0044989A`
and stores the result at control-block `+0x14`. A null return is fatal. Its
retained diagnostic is source line 108, after which a second product resource
initializer at `0x004ABCB0` runs.

The private acquire helper passes a zero-extended 16-bit timeout to stock
`osSemaphoreAcquire` at `0x0044994E`. It returns true only for CMSIS status
zero; null handles, timeout `-2`, and all other errors return false.

`thread_ble_wsf_wait_tx_ready`:

- records `osKernelGetTickCount` through `0x004490CC`;
- first tries timeout zero;
- on failure performs at most twenty acquisitions with timeout 10;
- after each failed timed acquisition, delays 10 ticks through `osDelay` at
  `0x00449376`;
- emits the retained 400-ms bound diagnostic at line 211;
- records elapsed ticks and retry count at line 217.

`thread_ble_wsf_tx_complete_notify` reads the current semaphore count through
`osSemaphoreGetCount` at `0x00449A0E`. It releases through
`osSemaphoreRelease` at `0x004499B8` only when the count is zero. A release
failure is diagnosed at line 242; a nonzero count is diagnosed as already at
the maximum at line 245 and deliberately not released. This prevents the
binary semaphore from accumulating duplicate transmit-completion credits.

## Ingress closure

There are 27 direct BL sites to exact entries: eight are intra-TU and nineteen
are exterior. The packed address/target digest is
`982c8ddf0171814ac78a0ba6b65da5c5127a9ca7513945fb9859c5f65c619284`.

Exterior call distribution is:

- five callers of `thread_ble_wsf_wait_tx_ready` at `0x004BDD96`,
  `0x004BE0A8`, `0x004BE5F0`, `0x004BE90A`, and `0x004C4BFE`;
- one caller of the one-shot wrapper at `0x00475402`;
- thirteen callers of `thread_ble_wsf_tx_complete_notify` at
  `0x004A07D2`, `0x004B7646`, `0x004B7734`, `0x004B77A6`, `0x004BDDF4`,
  `0x004BE144`, `0x004BE308`, `0x004BE376`, `0x004BE37C`, `0x004BE68C`,
  `0x004BE9A6`, `0x004C4A04`, and `0x004C4C5C`.

The twelve bodies issue 50 decoded direct calls; packed digest
`2e9e033e128c8fb0d50a1b4dc03d801bf3063c542f58cd5fd63a90b75033662f`.

The whole-image bytewise word scan finds two values that normalize to a TU
entry:

- accepted: aligned literal `0x004D0CF8 = 0x004D0A4D`, the task Thumb entry;
- rejected: odd-address window `0x007940DD = 0x004D0AF7`, bytes overlapping
  unrelated packed data rather than a pointer cell.

The accepted-entry digest is
`7b5af863fef7e426c36016829833856998635f2757cc55dd1e860c2815ee2029`;
the rejected-window digest is
`9ee9d3ccef7d5fa2a5728732a5d9b39b6c89d76cb2cdf8e32f738c61178cd326`.
There is no stored strict-interior pointer, direct BL to a strict interior,
wide branch to any entry, or wide branch to a strict interior.

## Literal ownership

The owned tail `[0x004D0CDC,0x004D0D24)` is 72 bytes, SHA-256
`d6c4a22566c5d0bd523bf5723afb6b13919b210c88e365d63ca04e0d2d72be17`.
It contains the product control block, retained diagnostics/function names,
the retained source path, the `task.ble.wsf` category, task attributes, task
entry, and prefixed diagnostic variants. It is data, not executable code.

## Clean-room candidate

The independently authored candidate is split across `ble_wsf_task.c`,
`ble_wsf_lifecycle.c`, and `ble_wsf_flow.c`. It preserves the recovered task
startup order, lifecycle index 9, one-credit semaphore construction, static
thread attributes, paired resource hooks, null-safe semaphore take, immediate
then bounded retry policy, tick accounting, and saturating completion notify.
All retained diagnostic decisions are explicit injectable seams; the default
freestanding build does not embed the stock logger implementation or strings.

`tests.test_ble_wsf_reconstruction` exercises startup/lifecycle ordering,
16-bit timeout truncation, three-success and twenty-retry paths, elapsed-tick
accounting, duplicate completion suppression, release failure, and task
creation/destruction. It also authenticates the candidate source hashes and
compiles all three sources for `thumbv7em-none-eabi`, requiring exactly the
twelve recovered global text symbols.

## Provenance boundary

The task implementation is G2 product code, not an upstream Cordio TU. The
authenticated AmbiqSuite R2.5.1 `radio_task.c` is useful only as a related WSF
dispatch-topology oracle. CMSIS-FreeRTOS v10.5.1 commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53` identifies the provider ABI for
thread, tick, delay, and semaphore calls; it does not supply this product
task's source. Searches of the authenticated local archives and public
official source mirrors found no `thread_ble_wsf.c` copy.

Consequently this increment is fully bounded and now has a clean-room
behavioral candidate, but it is not production-integrated and does not claim
instruction or stock-diagnostic identity. Placement, redirect guards, and
package-level validation remain future integration work.

## Reproduction

```sh
python3 tools/analyze_g2_thread_ble_wsf.py
python3 -m unittest \
  tests.test_analyze_g2_thread_ble_wsf \
  tests.test_ble_wsf_reconstruction
```

The analyzer authenticates the OTA, all body and data hashes, the static task
configuration, retained strings, 27-entry direct closure, 50-call provider
closure, stored-entry classification, and absence of strict-interior ingress.
