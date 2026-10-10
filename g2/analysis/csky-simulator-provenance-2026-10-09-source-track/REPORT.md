# Official CK804EF simulation source lead

New useful official source: https://github.com/XUANTIE-RV/qemu/tree/3287d345c7f5d60d5c8774d90752f5f710744f85 (verified xuantie-qemu-9.0 branch pin). Selected source and license files were acquired in acquisitions/; per-file URL, SHA256 and size are in ACQUISITION.json. No downloaded code was run or built. Existing container/GDB setup was not duplicated.

## Precise ISA support evidence

- target/csky/cpu.c:1003 registers `ck804ef` to e804df_cpu_initfn; lines636–650 initialize CPU_ABIV2, CPU_E804, ABIV2_DSP2, ABIV2_FPU_SINGLE, ABIV2_ELRW and MPU.
- translate_v2.c:4181–4182 handles bloop with DSP2/VDSP2 feature checking.
- Packed arithmetic: translate_v2.c:8368 emits paddh_s16; op_dspv2.c:118 defines saturated padd_s16_s; translate_v2.c:9401 emits pabs_s16_s; pasxh_s16 and pmax_u16 are also implemented.
- Complex arithmetic: translate_v2.c:10230/10233 emits mulca_s16_s/mulcax_s16_s;10245/10249 mulaca_s16_s/mulacax_s16_s;10261 mulacsx_s16_s;9995 defines mulcsx_s16. These are the DSP families actually present in the matched assembly sources, not merely a generic CPU-label claim.
- Memory postincrement and loop operations are present in the translator. Exact opcode-by-opcode execution and saturation/rounding edge behavior still require the kernel fixtures; source presence is not numerical validation.

The official c-sky/qemu master pin d74824cf7c8b352f9045e949dc636c7207a41eee has a complete nontruncated API tree with **no C-SKY path**. It is not the usable C-SKY simulator checkout. XUANTIE-RV xuantie-qemu-9.0 has target/csky and hw/csky including DSP helpers. Tree/head receipts retained. The PyPI RISC-V-only package should not be substituted.

## Smallest prospective numerical test route

Prefer owner archived-GDB simulator if its existing contract and DSP execution succeed. Otherwise build only qemu-system-cskyv2 from the above official pinned source, select `-M smartl -cpu ck804ef -nographic` with a standalone little-endian bare-metal ELF harness. smartl.c defaults to e804df and provides separate16MiB RAM regions at0,0x20000000,0x50000000,0x60000000. Use its RAM for code/stack/input/output and a bounded return/result observation through GDB; verify boot loader ELF entry/reset behavior and debugger launch options before claiming runnable execution. No GX8002 peripheral model or alias is needed for isolated pure DSP kernels, and none is established here. Do not interpret the smartl RAM as target physical memory layout.

The new route resolves a concrete source-level simulator candidate with CK804EF DSP2 support. Remaining contract: locally build/run the C-SKY target, verify each actual instruction encoding and deterministic halt/results in the harness, then evaluate numerical fixtures. No current installed QEMU binary or successful execution is claimed. Full source checkout/build was left to owner to avoid duplicate environment setup.

License: root LICENSE states QEMU emulator as a whole GPLv2 with per-file compatible licenses and separate bundled firmware terms. op_dspv2.c explicitly LGPLv2-or-later; keep per-file notices. COPYing and LICENSE retained. Proposed reference module if owner elects to register: third-party/tools/xuantie-qemu-csky, URL https://github.com/XUANTIE-RV/qemu.git, pin3287d345c7f5d60d5c8774d90752f5f710744f85. No module/index mutation occurred in this task.
