# CASE source candidate, 2026-10-10 round 2

Run `python3 build.py` from any directory. The script compiles eleven previously bounded CASE reconstruction modules for ARM Cortex-M0+ Thumb, soft float, and creates an archive under the ignored `build/` directory. It writes exact source hashes, commands, compiler version, archive hash, and unresolved symbols to `../../../analysis/case-source-candidate-round2-20261010/receipt.json`. The complete symbol listing is `nm.txt` there.

This is a source-only composition artifact. It has no reset vector, linker script, original HAL/RTOS providers, firmware image, or hardware execution claim. Each member retains its earlier limited input contract; archive creation does not expand them. The earlier `uart_error_offline` member is deliberately excluded in favor of the corrected `uart_error_atomic_offline` version.
