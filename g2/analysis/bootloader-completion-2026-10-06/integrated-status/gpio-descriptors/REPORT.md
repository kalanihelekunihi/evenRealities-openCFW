# Bootloader GPIO descriptor registration and required children

Locked bootloader148599 bytes, load0x410000, SHA256 `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`. Candidate image `6bef4edbcece2022ee41b9670cd4eff295fc62bb697e00e180c4efce8812c259`; immutable shared-image validation is recorded separately. This report describes bootloader-only source, not a wider GPIO-driver replacement.

Reconstructed source: `g2/components/bootloader/initializer_callbacks/gpio_descriptors.c`, interfaces/layouts in `.h`, source-defined nonexecuting descriptor table in `gpio_descriptor_data.c`. Original disassembly/function hashes and decoded table are in this directory. The registrar430280..4303bc has316 original bytes. Directly required status41dcca, clear41de3c, callback-register41e000, control41da84 and priority43025c total1410 original bytes. NVIC430240 behavior reuses the already native context NVIC helper; pin-index41d8f8 is inlined in control. These extents are ownership evidence, not byte-identical compilation or an implementation percentage.

## Descriptor layout and call chain

| Offset | Width | Proven use |
|---|---|---|
|0|u32|Pin number|
|4|u8|Dispatch type|
|5|u8|Initial output: exactly1 selects set; other values select clear|
|6|u8|Interrupt mode: low2 bits patch pin-config bits6..7; full byte controls registration branch|
|7|u8|Not read by this registrar|
|8|u32|Callback address, checked nonzero before registration|

The stock table at42f674 contains97 rows/1164 bytes: type1=11, type2=6, type3=39, type4=41. It is reconstructed as ordinary C data at the original address; emitted bytes are checked against the locked table. No executable blob/opcode array is introduced.

Null table or zero count returns0xffffffff. Otherwise rows execute in order and the function returns0, ignoring child status codes:

* Type1: configure pin with0x183 (word originally referenced through434190); then set/clear output from byte5.
* Type2: start from0x93 (434194), **replace** bits6..7 using byte6 low2 bits, rather than OR with them. Thus mode0 yields0x13. If byte6 and callback are both nonzero, take the IRQ branch below.
* Type4: configure pin with3 (434198).
* Other types, including all39 stock type3 rows, do nothing in this routine.

Historical names `opencfw_bl_power_register_update`41d92c and `mode_register_update`41d9aa are reused native children. Here their actual effects are pin configuration/PADKEY and GPIO state-write, not proof of a separate power-controller operation.

IRQ branch: form a seven-word local mask; read **channel0 enabled pending status for all seven banks**, overwriting that local mask; clear those pending bits; register(channel0,pin,callback,arg0); enable(channel0,individual pin); set NVIC priority4; enable NVIC. The read/clear can include other enabled pins, not solely this descriptor's pin. All six stock type2 rows (pins4,27,29,37,38,156) have mode0/callback0, so none of these IRQ-registration steps executes in the seven-case startup. Synthetic direct fixtures exercise it separately.

The local signed-halfword IRQ map at43409c contains only56,57,58,59 followed by text. Registrar IRQ fixtures use pins0..127. No bank4..6 mappings are invented. The candidate emits only the four IRQ-table halfwords; adjacent original text is not part of this source section, so callback-enabled higher-bank descriptors are outside its validated input domain. This does not prove the callback branch is safe for arbitrary descriptors or that other firmware modules lack additional mappings.

## Child behavior and data ownership

Status41dcca truncates channel/selector to bytes. Channels0/1 read seven pending words under saved PRIMASK; nonzero selector snapshots all seven EN words first, then ANDs each STAT word. Invalid channel returns6 after restoring PRIMASK. There is no output-null guard on valid-channel paths.

Clear41de3c validates mask pointer, writes seven masks to channel0/1 or both under saved PRIMASK, then always reads fixed **0x40010604** (last channel1 status bank). Invalid channel byte performs no clear writes but still reads back and returns0. Null pointer returns6 before readback. W1C is not asserted by the RAM model.

Register41e000 validates the channel byte only. Callback/argument are separate448-word tables at20023600/20023d00; channel1 is offset224 words. It stores callback **before** argument, makes no copy of callback-owned data, does not mask interrupts, allocates/frees nothing and does not invoke the handler. There is no pin-range guard; caller must preserve callback/argument lifetimes and exclude concurrent dispatch where needed. This is not an owned-buffer or teardown mechanism.

Control41da84 accepts byte operations0individual-disable,1individual-enable,2mask-disable,3mask-enable; null/input-control errors return6 and individual pin>=224 returns5. Channel is not independently range-validated. Mask operations borrow seven input words synchronously and reread for each channel. NVIC priority uses signed low16 interrupt: nonnegative writes byte atE000E400+irq; negative selects SHPR byte atE000ED18+(irq&15)-4. It writes priority shifted4 with byte truncation and no additional interrupt-range guard.

## Tests and exact limitation

434 fresh-CPU original/source comparisons PASS on the candidate: stock97 rows, null/zero, descriptor types/initial-value truthness, IRQ branch pins0..127/modes1,2,3,4,255, channel/control truncation, status/mask clear/register/control paths, invalid pin/channel controls, and priority negative/positive cases. Ordered GPIO/NVIC reads/writes, mask output, table/state hashes, result and PRIMASK compare. Native pin-config/state/critical and GPIO children execute; there are no callback body calls.

**Explicit original-helper model:** installed Unicorn misexecutes the zero-fill415ff4->417c30 IT/STM carry loop. An independent original28-byte zero call reproduces underflow/nontermination with default and Cortex-M4 CPU selections. IRQ-registration fixtures therefore model exactly28 zeroed local stack bytes at that wrapper; the original wrapper/loop are excluded from instruction-footprint claims. The source zero initialization executes compiler instructions. No silent no-stub/all-original claim is made. Stock97 descriptors never take that branch, so seven-case startup needs no such zero-fill model.

GPIO/SCB registers and pending/index values are synthetic RAM; no physical W1C, real exception delivery, pin electrical behavior, ISR/task race or hardware-safe quiescence is proven. No changes to wider GPIO components, commits, flashes or IAR login.

Direct fixtures visit1720 of1726 new native body bytes. The6 unvisited bytes are the index-helper error arm (helper always returns0) and switch default after the control0..3 guard; they are separately identified in gpio-source-ownership-6bef4e.json, not counted as tested execution.
