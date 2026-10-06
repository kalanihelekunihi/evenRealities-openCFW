# Reconstruction provenance

Input: locked Apollo OTA `g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin`, SHA-256 36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863; strip32-byte header, runtime base438000. Stock bodies475014..47510e and47510e..475194; PC-relative SCB literals475198..4751c8 are data, not executable coverage. Authenticated consumer range template78d474..78d47c contains address0 and length3200.

Source/header are new MIT reconstructions of observed instructions and layout. Historical first-party link-order census labels are unverified; no authorship, SDK identity or source-byte equality is inferred from them. No upstream executable body or opcode array is retained. Original byte hashes, source/ELF bindings, failed oversized fixture and independently reviewed comparisons are in the analysis packet. Cortex-M4 emulator execution of the selected Thumb operations does not simulate the full Cortex-M55 cache/DMA/memory system.
