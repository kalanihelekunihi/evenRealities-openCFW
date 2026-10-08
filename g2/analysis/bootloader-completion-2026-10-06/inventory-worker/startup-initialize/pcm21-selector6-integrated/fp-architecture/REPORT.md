# Floating-point comparison boundary

The locked classifier at 0x427e0c..0x427e84 executes VCMP (not VCMPE), followed by VMRS APSR_nzcv,FPSCR. Its input uses S0; the source bit helper uses R0. Stock bytes/disassembly and per-input output receipts are preserved here/adjacent.

152 default-mode bucket cases agree, but three signaling-NaN samples leave IOC set in stock and clear in source. This is an unclosed side effect, not an ignorable bucket mismatch. Expanded Unicorn testing records 108 fixtures and 44 exception/control differences without normalization. All requested FPSCR values read back initially; stock emulation then loses existing sticky/control bits in several cases. Those results cannot establish real FZ/DN behavior.

Independent QEMU 11.1.2 MPS3 Cortex-M55 scalar-instruction probes execute the same VCMP forms with six FPSCR configurations and eight inputs, 48 cases per comparison (96 total). They preserve incoming sticky flags/control bits, set IOC for signaling NaNs, and set IDC for FZ subnormal inputs. Comparing a negative subnormal with zero changes from less-than to equal when FZ is set. Thus the source integer comparison's mode blindness is a further potential semantic gap; whole-classifier FZ equality is not proven by the Unicorn result.

The first M55 compilation emitted DLS/LE and faulted with INVSTATE in this minimal fixture, which lacked valid LTPSIZE initialization. Its ELF/debug log remains. Compiling scalar Cortex-M33 instructions for the same M55 machine resolves the unrelated loop harness problem. No floating-point expectation was weakened.

Next implementation should use actual scalar FP comparison semantics or accurately model FPSCR controls and sticky effects, preserving the stock compare sequence. Simply forcing IOC or masking FPSCR comparisons is insufficient. The candidate was not modified to hide this gap. Whole-classifier/updater cross-emulator validation and nondefault trap behavior remain outstanding; no physical FPU or Apollo scheduling claim.
