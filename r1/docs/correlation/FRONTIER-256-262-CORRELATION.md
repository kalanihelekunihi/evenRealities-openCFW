# 256...262-byte frontier correlation

The five largest unresolved application functions after the 264...274-byte closure, plus eight
exclusive provider helpers, are now source-routed from immutable body hashes, direct-call scans,
function-pointer evidence, and local control-flow review.

| Recovered function | Bytes | SHA-256 | Disposition |
| --- | ---: | --- | --- |
| `0x00081744..<0x00081854` | 272 | `2b61c1a9d01a3eab9eb560558798972795e00249c8c72211d8b44d73cb8772e2` | R1/Goodix diagnostic adapter |
| `0x0007CA94..<0x0007CB98` | 260 | `601cceb77f1e3a94d5c4bbe9223d1cfd267638a6277eb03fe27d013db18949d7` | owner-authorized transparent GoMore pooling executor |
| `0x00084524..<0x00084628` | 260 | `eae704a3150d3880f21815ed4517e5a3367af3b8f7b2766106f4449998478fdc` | R1 system-settings/REG1 planner |
| `0x0007244E..<0x00072550` | 258 | `ac1c79308e186202e3fb298ef473010525cf680e1d1ac65e4251edc93283116a` | owner-authorized transparent sleep/history reducer |
| `0x0004B718..<0x0004B818` | 256 | `08780302207c762a1a7ba9ee59e1c614ae89578c60b700013d9602aee5eda657` | R1 temperature-mode transition planner |

The Ghidra CSV reports 262 bytes for `0x00081744`, while its inclusive end and recovered
instruction stream continue through the final two-byte back-edge at `0x00081852`. Its corrected
executable extent is 272 bytes. The five frontier functions therefore total 1,306 executable bytes
(1,296 inventory bytes). Eight related GoMore helpers at `0x00074C48`,
`0x0005D370`, `0x0007266A`, `0x00072572`, `0x00072024`, `0x0006476C`, `0x00068354`, and
`0x00069500` add 794 bytes. The complete closure is thirteen functions / 2,100 executable bytes
(2,090 inventory bytes): two R1
product policies, one R1/Goodix adapter, and ten GoMore-provider functions.

## Product-owned behavior

System command `01/00/0F` points to `0x00084525` at registration word `0x0009A530`. Read returns
exactly twelve zero-initialized bytes with normalized persisted REG1 enable in byte 5. Set emits
its success acknowledgement first, accepts only switch type zero in byte 4, compares raw byte 5
with the stored normalized Boolean, persists a changed normalized value, and requests S140
`sd_power_dcdc_mode_set`. `r1_system_settings_plan_command` reproduces only that deterministic
response/action policy with an exact twelve-byte safe input gate. It does not write persistence or
invoke the regulator SVC.

`0x0004B718` is called at `0x0004BAC2` by the temperature sleep/mode route. An unchanged mode is
inert. A changed mode unregisters an existing old stream; leaving mode one stops its existing
timed source; entering mode one creates that source with recovered period 600 when none exists.
`r1_temperature_mode_plan_transition` returns these actions without touching the unidentified
sensor-stream/timer providers or live acquisition.

## Goodix adapter boundary

Callback table word `0x0009A5A4` contains Thumb pointer `0x00081745`. The stock adapter refreshes
its provider snapshot no more often than every 500 ticks, then serves selectors 1, 2, 3, 4, 5, 7,
8, and 9 with exact output lengths 4, 6, 2, 10, 124, 24, 12, and 12 bytes. Selector 3 consumes a
one-shot byte. `r1_goodix_diagnostic_refresh_due` and `r1_goodix_diagnostic_select` preserve only
this bounded R1 adapter behavior over a caller-supplied provider snapshot. They perform no live
Goodix access, do not synthesize biometric values, and cannot operate a sensor without the licensed
provider and board binding.

## GoMore provider boundary

`0x0007CA94` is installed by the private descriptor constructor at `0x00074C48`; that constructor
is called only by the still-gated GoMore graph builders at `0x0002874C` and `0x0002966C`. The
executor's complete floating-point max/average pooling behavior is now represented by bounded
`gomore_tensor_pool_1d`, with explicit tensor extents and a typed maximum binding. It embeds no
graph, model, descriptor pointer, or executable address.

`0x0007244E` is called only from wrapper `0x0005D370`, itself called only by the still-gated GoMore
force-wake path at `0x0006B50C`. Instruction-level recovery has since admitted the reducer, its
wrapper, and all listed direct helpers as transparent typed C: weighted merge `0x00072024`,
snapshot selector `0x00072572`, tail reconciliation `0x0007266A`, timestamp setter `0x0006476C`,
two-bit range extraction `0x00068354`, and lookup `0x00069500`. The pooling executor is likewise
transparent; classifier/model graphs and the force-wake root remain gated. No opaque model data or
firmware bytes are incorporated by the admitted interval closure.

Reproduce with:

```sh
python3 tools/evidence/summarize_r1_frontier_256_262.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```

The system-settings, temperature-mode, and Goodix selector APIs link at `0x00036048`,
`0x000360A8`, and `0x00036DC0`. The unsigned Nordic application contains 94,804 bytes of text,
236 bytes of data, and 132,544 bytes of BSS. The 95,040-byte BIN has SHA-256
`421a42cf37dad04dadcff5d3b1742efcba4ba50fd1d2e52f26bcf00e5df24d35`; the standalone HEX has
SHA-256 `48e1b3fadfdb956fbdf5f637d48c9a5808db5394848fb4538450c0ff98be80cf`.
Code signing, deployment authorization, private keys, security-enforcement bypasses, live
regulator control, and device programming remain outside this closure.
