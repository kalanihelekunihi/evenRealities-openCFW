# G2 bootloader state-register initializer source closure

The authenticated interval `[0x0042D3BC,0x0042D562)` is production-routed from
`runtime_state_register_initialize_42d3bc.c`. Apple clang 21 and Homebrew clang
22 reproduce all 422 stock bytes after two strict delay-provider relocations.
The sole caller is `0x0042D59C`; no interior or stored-pointer ingress exists.
The Apollo-main analogue at `0x005A05E0` matches 414 of 422 bytes. Sixteen
literal cells pin the relevant retained-state and MMIO addresses.

The portable model covers the non-active saved-field restore, bounded ten-bit
delta selection, temporary low-six-bit mode, ordered 5/10-microsecond delays,
four-bit power mask, five register-field tuning groups, optional saturated trim
adjustments, saved-field restoration, control-bit clearing, low-six-bit final
selection, and unconditional power-mask cleanup.

Offline compilation, portable behavior, provider identity, manifest ownership,
and unsigned firmware assembly are verified. Live MMIO semantics, clock/power
stability, delay accuracy, trim effects, peripheral response, interrupt races,
reset, and cold boot are blocked by unavailable physical evidence. No signing,
flashing, reset, or hardware access occurred; functional completeness is not
claimed.
