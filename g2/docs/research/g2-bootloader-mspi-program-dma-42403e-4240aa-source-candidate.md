# G2 bootloader MSPI high-priority DMA programming source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

The complete 108-byte `program_dma` body at `[0x0042403E,0x004240AA)` is
production-owned by
`components/bootloader/core_overlay/runtime_mspi_program_dma_42403e.c`. Both
reviewed Cortex-M55 compiler profiles generate the authenticated stock body
after resolving the sole `R_ARM_THM_CALL` relocation at body offset 42 to the
already source-owned clock/mode route at `0x004222F0`.

The identity closes against AmbiqSuite 5.1.0 `am_hal_mspi.c` at commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b`. The wrapper selects
`(last_hp_index + 1) % max_hp_transactions` from the 24-byte high-priority DMA
entry array, requests HFRC clock user `MSPI0 + module` through the stock
one-byte user-ID ABI, clears `DMACFG`, writes `DMATARGADDR`, `DMADEVADDR`, and
`DMATOTCOUNT`, then publishes the entry's final `DMACFG`. A nonzero clock
request status is returned without MMIO writes. The stock function performs no
additional module, divisor, entry-pointer, or bounds validation, and the source
does not invent any.

Evidence and gates:

- stock body SHA-256:
  `d075d73aba138735bc9229bcf8672cb6a1c2fadec21985d2159043534ad130e1`;
- unrelocated body SHA-256:
  `96f36a90d1f35ecee3a6a94eac7f4bf8bdda10b5db9da66949c335b84770f367`;
- authenticated direct callers: `0x0042410E` (`sched_hiprio`) and
  `0x00426620` (`am_hal_mspi_interrupt_service`);
- host tests cover next-entry selection, ring wrap, exact five-register order,
  clock failure, and the `uint8_t` clock-user conversion;
- `tools/analyze_g2_bootloader_mspi_program_dma_42403e.py` pins inputs,
  upstream identity, both reviewed compiler outputs, relocation, literal,
  callers, production placement, manifest split, component accounting, and
  the next sequential frontier;
- the source-owned image remains byte-identical to official
  `s200_v2.2.6.10`, and the builder performs no hardware operation.

Canonical bootloader accounting after this closure is 308 source-owned
functions: 179 relocated leaves, five authenticated caves, and 105 exact
in-place leaves. It owns 25,751 source bytes plus 16,528 generated patch bytes
and 16 alignment bytes, retaining 121,545 official bytes. The next sequential
executable frontier is the 118-byte `sched_hiprio` body at
`[0x004240AA,0x00424120)` with stock SHA-256
`dfbd51c61eba1ea51418a1faeaaa99df5aebb0ea900ed157a0c3a55a7b28d144`.

No signing, flashing, reset, boot, clock request, DMA write, MMIO access, or
other hardware operation was performed. Physical qualification remains
blocked by unavailable physical evidence; future authorized G2 capture evidence remains
an acceptance requirement, while the earlier right-temple disconnect was caused
by the charging case being bumped and is not evidence of a firmware fault;
future acceptance requires clock, DMA-register, queue-index, concurrency,
interrupt-service, and cold-boot observations.
