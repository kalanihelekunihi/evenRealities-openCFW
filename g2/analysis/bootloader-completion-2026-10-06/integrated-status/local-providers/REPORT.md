# Native local platform providers

Reconstructed `41ac44` (CPACR access and barriers), `41ac5a` (FPCCR lazy mode with critical state restore), `41f9d8` (multiply delay argument by 1000 modulo 2^32), and `41f9e6` (raw delay forwarding) in `g2/components/bootloader/platform_startup/local_providers.S`.

Original/source differential validation: **144 cases, 92 distinct original instruction bytes**, including low-byte mode truncation, preexisting control bits, both PRIMASK values, delay argument wrap, callee-saved registers and the original unusual pop-to-r0/r1 results. Source invokes controlled critical-save and HAL delay callbacks; physical FPU exception behavior and delay accuracy remain unverified.

Reproduce from repository root:

```sh
clang --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -c g2/components/bootloader/platform_startup/local_providers.S -o /tmp/opencfw-local-providers.o
arm-none-eabi-ld -T g2/components/bootloader/platform_startup/local_providers.ld -o /tmp/opencfw-local-providers.elf /tmp/opencfw-local-providers.o
/Users/kalani/.local/share/opencfw/venv/bin/python g2/components/bootloader/platform_startup/verify_local_providers.py --elf /tmp/opencfw-local-providers.elf --output g2/analysis/bootloader-completion-2026-10-06/integrated-status/local-providers/comparison.json
```

The `source-image-compatible` target now binds these four local bodies instead of stock-address aliases. Integrated normal/update and malformed-update evidence is recorded separately against that ELF hash.
