# GPIO pad configuration foundation

Two unchanged public Ambiq SDK5.1.0 bodies now compile in an isolated source module: `am_hal_gpio_pinconfig_get` and `am_hal_gpio_pinconfig`. The original BSD-3-Clause notice, exact function text hashes, and pinned configuration type are retained. Table declarations use an explicit seven-word bound; their bytes match the locked Apollo firmware.

```sh
make -C g2 ambiq-gpio-config-simulator
make -C g2 ambiq-gpio-config-simulator-test SCB_SIM_PYTHON=/Users/kalani/.local/share/opencfw/venv/bin/python GPIO_CONFIG_SIM_REPORT=build/foundation/ambiq-gpio-config-simulator/comparison-new.json
```

Reports are exclusive-create; choose a new report path on rerun. This builds a callable source-only Thumb2 module, not a linked firmware image. It depends only on the actual shared PRIMASK helper, not the unresolved optimized scheduler simulation.

The recovered ABI is a four-byte configuration word passed by value. Bits10–12 hold drive strength;13–15 hold pull selection. Other fields are passed to the register unchanged. Pin indices0–223 are accepted by the range guard; this logical range is not a physical-pad inventory. On normal pads, the validation considers only the low two drive bits, leaving the third bit as slew configuration. Additional drive values2/3 require a per-pin capability bitmap. On extended-drive pads, allowed pull values are0,1,6; the setter does not restrict the drive field. The stock bitmap has sparse holes: comments describing contiguous pad ranges are not authoritative.

A valid setter saves and masks PRIMASK, writes PADKEY0x73 at0x40010400, writes one complete configuration word at0x40010000+4*pin, clears PADKEY, then restores the incoming mask. It does not restore a previous nonzero PADKEY value. Invalid pins return5; unsupported drive/pull combinations return7 without MMIO. The getter returns5 for invalid pin before checking output nullness; null output on a valid pin returns6. A valid getter reads one volatile word, writes caller-owned output, and leaves PRIMASK unchanged.

Concrete stock consumers are the radio shutdown helper's pin138/raw0x3 configuration, display power helper's product-revision-dependent pins143/128 and unconditional pin142/raw0x183, and flash setup's pin103 configuration snapshot. These callers are static context; no complete board sequence was implemented or executed by this component.

The verifier compares authenticated stock instructions, compiled source and an independent capability/final-state model. It retains ordered MMIO accesses, mask-at-access, output writes, full register state, output guards, stack and callee-saved registers. Only MMIO and output-memory hooks are installed; no call is stubbed. This avoids depending on the scheduler's affected repeated insertion pattern without removing ordering evidence. Physical pad capabilities, clocks, NVIC, electrical behavior, concurrent access, board bring-up/shutdown and production byte equality remain unproven.

See [the analysis report](../../../analysis/ambiq-gpio-config-2026-10-05/REPORT.md) for exact hashes, source comparison, consumer evidence, independent review and cumulative coverage. Full optimized tick validation remains blocked separately.
