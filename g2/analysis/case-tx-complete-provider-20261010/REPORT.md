# CASE TX-completion lower provider

The fixed CASE image is SHA-256 `36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374`. Its lower target at `0x08006776` consists of the complete two-byte Thumb instruction `70 47` (`bx lr`). It is the weak TX-completion callback reached after the IRQ's TCIE clear, ready-state write and `TxISR` reset. It does not modify the UART handle or peripheral state.

`tx_complete_provider.c` expresses the complete no-op body. `verify.py` compiles the **archive source** with the archive's Cortex-M0+ `-Os`, soft-float and section flags, and verifies that `.text.case_tx_complete_provider` is exactly the stock two bytes. `results.json` retains fixed-image, source and object hashes. This body has no hidden lower call or branch; the handle argument is ignored.

`case-dma-abort-20261010/verify_irq_native_dma.py` was then rerun with the source TX-completion body and **native stock `0x08006776`**, without the earlier common lower fixture. All **1,264** public-entry stock/source IRQ cases pass with source-owned DMA abort and TX completion providers. Common compiled synthetic RX/TX ISR callbacks are still explicit test boundaries, and physical UART/DMA timing is not established.

The deterministic CASE whole-archive relocatable link passes with **43 objects, 70 provided symbols and three unresolved imports**: direct `case_legacy_command`, direct `case_binary_command`, and lower `case_vformat`. Archive SHA-256 is `3fd6b453372e695c75fbb4a057217031809c5fd989dead729b1d43f18c0f9951`; relocatable SHA-256 is `8355fc1647031b0812be4047033708df55261726cff3f574852792eaa3a80248`. Direct CASE completion stays **10/12**.
