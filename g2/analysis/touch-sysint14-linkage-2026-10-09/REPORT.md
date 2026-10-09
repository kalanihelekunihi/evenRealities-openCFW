# Authentic SysInt linkage

Unchanged public PDL objects link exactly to the original touch image:
`Cy_SysInt_SetVector` `[0xA274,0xA2A8)` (52 bytes) and `Cy_SysInt_Init`
`[0xA2A8,0xA2F0)` (72 bytes). The actual emitted CMSIS helper
`__NVIC_SetPriority` `[0xA214,0xA274)` also matches all 96 bytes; it is
outside the selected 54-function census and is not counted as a new selected
function. The two new candidates and 124 bytes await independent review.

Stock BL at `0xA2C0` targets the helper, and `0xA2D8` targets SetVector.
Source ABS32 relocations have zero addends. Actual stock PC-relative loads
bind `__RAM_VECTOR_TABLE=0x20000400` at three instruction references and
`__Vectors=0x3300` at the read-only fallback. These are linker symbol bindings,
not fabricated vector contents or executable stubs. `results.json` records
each original reference, relocation, input/output hash and linker command.

Readable behavior:

```c
handler set_vector(int irq, handler replacement) {
    if (SCB_VTOR != RAM_VECTOR_TABLE)
        return ROM_VECTORS[irq + 16];
    assert(replacement != NULL);
    handler previous = RAM_VECTOR_TABLE[irq + 16];
    RAM_VECTOR_TABLE[irq + 16] = replacement;
    return previous;
}
status init(config *cfg, handler replacement) {
    if (!cfg) return 0x560001;
    assert(cfg->priority <= 3);
    set_nvic_priority(cfg->irq, cfg->priority);
    if (SCB_VTOR == RAM_VECTOR_TABLE)
        set_vector(cfg->irq, replacement);
    return 0;
}
```

This recovers the initialization prerequisite: handler replacement occurs
only when VTOR already selects the RAM table. Static equality does not prove
which table was active, any vector values, IRQ delivery or board provenance.
No source/flag fitting, original-instruction execution, production change,
campaign admission or source-completion claim was made.
