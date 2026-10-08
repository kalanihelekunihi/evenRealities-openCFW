# Native initializer interrupt helper

The subsequent source-linked test ELF is `bcc057db988238f1209f2e9aead5e699156b7050402ad6c08b9f667d1c964da7`. It replaces the numerical initializer alias at original entry `0x42c63a` with `opencfw_boot_context_interrupt_enable` at source `0x33a1c`. Source body: `g2/components/bootloader/initializer_callbacks/context_interrupt.c`. The shared linker selects the object with explicit alignment;332 Thumb mappings pass. All seven normal/malformed/stop-and-reboot cases PASS on this exact image. Both interruption phases and both reboot runs match;563 input files and135 objects remain unchanged. No prior-image result is inherited.

## Recovered behavior and ABI

The function receives `(const uint32_t *handle, uint32_t mask)` and returns uint32 status. Null handle or `(handle[0] & 0x01ffffff) != 0x01123456` returns2. If mask bit1 (value2) is set, it returns6. Otherwise it ORs the mask into `*(volatile uint32_t *)(0x40050200 + handle[1] * 0x1000)` and returns0. The original does not add a module-index bounds check. This is separate from the NOR interrupt-number helper; names are deliberately distinct.

The platform-finish caller at original4305ca passes context row4's transfer field, not instance field, with mask0xff. That mask includes forbidden bit1, so even an accepted handle returns6; this caller does not use the return. This source closure therefore does not establish successful interrupt activation. The current shared context-claim dependency is still modeled and does not establish real handle initialization. Both normal integration cases pass actual arguments `(0, 255)`; original trace executes the null-handle branch and returns2, with one native entry visit per case on both sides. Valid handle/module register writes are covered only by the separate52-case comparison with simulated MMIO.

## Evidence

Locked bootloader SHA256: `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`, load0x410000, payload148599 bytes. Locked56-byte body SHA256: `4bb8cd7875f57a46da8764a7c89f6058ce9f5aac52f707e5c86dc7a66c20d775`.

`context-interrupt-bcc057.json`:52 comparisons PASS on exact shared ELF;22 original PCs /56 instruction bytes. Cases distinguish bad/null handles, mask2 rejection, mask4 success, high masked magic bits, modules0..3 and existing register values. Original instructions and compiled C execute in Unicorn; no external-call return stub is used for this leaf. Source compiles to54 bytes. The test receipt also hashes its isolated module linker as verifier context; actual shared linkage is the pinned snapshot `startup_source_image.ld`, not that isolated linker.

`implementation-inventory-bcc057.json` inventories444 linked defined function symbols (including aliases/local/veneer symbols),73366 deduplicated compiled bytes and a partial explicit original-entry map. These bytes are not original implemented coverage and are not a firmware completion percentage.

## Remaining boundary

Context claim/configuration/retry, NVIC enable, ADC and service/kernel children still require source closure. Simulated register writes do not prove physical interrupt delivery, timing, scheduler correctness or a bootable image. The immutable459804 checkpoint independently passed both before/after atomic modeled ROM-operation stops and both reboot phases; its durable seven-case receipt is `same-image-validation-459804.json`. bcc057 now has its own completed seven-case comparison in `same-image-validation-bcc057.json`; neither receipt establishes physical hardware recovery.
