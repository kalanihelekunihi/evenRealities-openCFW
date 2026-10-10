# Archived C-SKY debugger: dependency resolved, simulator absent

**Dependency resolution PASS; instruction simulation unavailable in this archived GDB.** Official Docker Ubuntu22.04 amd64 image manifest sha256:5ec03bb3441e8b0bf3b4f9cd4629a1ae763010dc3035bb8da3ae6cf026486401 was pulled. Official Ubuntu archive/security sources supplied libncurses5 and libtinfo5, both6.3-2ubuntu0.3. They were installed only inside a disposable container, automatically removed afterwards; no host packages, security configuration or archived toolchain were modified.

Archived GDB now executes and identifies GNU GDB7.12/C-SKY Tools V3.10.15 Minilibc abiv2, targetcsky-elfabiv2. help target lists serial-board/JTAG/remote/core/record targets but no simulator. target sim explicitly reports Undefined target command. The process returns0 despite this command failure; outcome.json uses command output, not exit status, as the semantic verdict.

No instruction smoke test or numerical comparison was performed, and no unsupported instruction was recorded as a mismatch. CK804/DSP execution support cannot be established through this tool because it has no simulator target. A separate authenticated C-SKY instruction simulator/emulator supporting the selected DSP ISA and ABI/memory fixture remains required. Board/JTAG/remote alternatives were not used; device execution is not authorized here.

The previous ten-unit pure-C ELF compile/link proof and all prior receipts are unchanged. Numerical equivalence, original-source assembly byte reproduction and C link success remain separate. The earlier missing-libncurses execution blocker is now resolved additively; it is replaced by the proven absence of target-sim support in this debugger build, not a claim that no C-SKY simulator exists anywhere.

Evidence: apt-update.log, apt-install.log, package-versions.txt, official-package-sources.txt, gdb-ldd.txt, gdb-simulator-probe.txt, probe-receipt.json and replay probe.py. Prior complete-C seal verifies. No Git/Pigweed/production/canonical/device changes.
