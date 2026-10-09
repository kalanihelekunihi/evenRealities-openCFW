# C-SKY descriptor semantic reference follow-up

Official document repository: https://github.com/c-sky/csky-doc
Pinned commit: `9f7121f7d40970ba5cc0f15716da033db2bb9d07`.
Acquired only documents and Git metadata. No downloaded repository code executed.
No LICENSE file is provided: manuals retain publisher copyright/all-rights-reserved terms; acquisition is evidence, not an implementation redistribution license.

## Exact instruction definitions already present in registered decoder dependency

Existing ghidra-csky commit `0daaa056e8c570ba514fc0d0226384ecf9f9df05` contains the manufacturer-origin Chinese Xuantie E804 User Manual 2.0 (2024), and separately labeled Google/DeepL translations. These are existing dependency copies, not newly authenticated downloads from the manufacturer. Exact public manufacturer distribution URL was not verified. Do not call the translations official English editions.

- Chinese/Google PDF pages 307–308, printed 290–291, section 14.93 and Figure 14.144: MULA.32.L adds the low 32-bit product to destination, retaining low 32 bits. Formula is Rz[31:0] <- Rz[31:0] + {Rx[31:0] X Ry[31:0]}[31:0]. Manual labels it signed multiplication; signed/unsigned products have identical low 32 bits. No flag effects.
- Chinese/Google PDF pages 206–207, printed 189–190, section 14.25 and Figure 14.38: BNEZAD updates RX <- RX-1 unconditionally, then branches if RX > 0; taken PC is PC+sign_extend(offset<<1), otherwise PC+4. No flag effects. This is NOT a general nonzero test. Translation contains a contradictory generic sentence about nonzero, but both operation formula and detailed description use greater-than-zero. Owner should inspect original page/encoding for final signedness admission. For initial positive eight and decrements to zero, this distinction does not change the eight-iteration loop result. No physical CK803/CK804 support or execution proof follows.

Extracted complete matching pages with PDF hashes are in `csky-manual-semantic-extracts.json`. Extraction warns about malformed object pointers and missing fontTools for legacy PDFs; Chinese text is partly garbled. ASCII formulas and translated prose survive. No new raster-page validation claim is made.

## Official V2 ABI, newly acquired

C-SKY_V2_CPU_Applications_Binary_Interface_Standards_Manual.pdf, release 2.1 (2018), PDF page15 / printed10, Table2.4:
r0–r3 argument/return/scratch destroyed; r4–r11 preserved; r12–r13 destroyed; r14 SP preserved; r15 LR preserved; r16–r17 preserved; r18–r25 destroyed. r26/r27 reserved, r28 data/GOT reserved/preserved, r29 text base reserved, r30 handler base reserved, r31 TLS reserved.
PDF page16 / printed11, section2.2.1.3: scratch/argument registers need not be restored; preserved registers must be saved and restored if used. LR contains return address and needs preservation when modified. Stack pointer multiple of eight.

This is the generic C-SKY V2 ABI, not a separately authenticated CK803-specific compiler ABI/configuration. Formal source signature and chip identity remain owner/auditor findings. Full ABI text is `csky-official-abi-extract.json`.

## Remaining limits

Official architecture manual acquired from c-sky/csky-doc has no exact MULA.32.L/BNEZAD extraction hits; absence of hits is bounded text-search evidence, not proof of absence from pages. No additional DSP manufacturer manual newly found in this bounded official-source search. Existing E804 document is stronger semantic cross-check but not authentication of target CPU/configuration. No packet/reconstruction/canonical ledger changes were made.

## Document provenance
- `g2/analysis/source-discovery-parallel-2026-10-09/acquisitions/csky-doc/CSKY Architecture user_guide.pdf`: SHA256 `579bd296dbf88b0b6842a473432e65199b87c0c19fcf04bb214f67241c68d509`, 592 pages.
- `g2/analysis/source-discovery-parallel-2026-10-09/acquisitions/csky-doc/C-SKY_V2_CPU_Applications_Binary_Interface_Standards_Manual.pdf`: SHA256 `055d36544aae5ed7b4c8b8904c97c6b4386ad80a623320fbda1cb43ce9c73a56`, 78 pages.
- `third-party/tools/ghidra-csky/C-SKY_ISA_Reference_Guides/C-SKY ISA User Guide 1.15.12 (2014).pdf`: SHA256 `3d4bb9978e40eb9ee3741fcb21c8c319702925068672a6fa7280cda96b05a2be`, 592 pages.
- `third-party/tools/ghidra-csky/C-SKY_ISA_Reference_Guides/T-HEAD 800 Series ABI Standards Manual 2.2 (2021).pdf`: SHA256 `1c950ac9da8c2e53f9473e699b53bfeaea79adfa021ac36ef5047101aae94173`, 85 pages.
- `third-party/tools/ghidra-csky/C-SKY_ISA_Reference_Guides/Xuantie E804 User Manual 2.0 (2024) EN-Google.pdf`: SHA256 `44fca768ef54909b1d0ee27c3a2e7c1470b2f18a4cbc6b73dab0c853bb4550ec`, 616 pages.
- `third-party/tools/ghidra-csky/C-SKY_ISA_Reference_Guides/Xuantie E804 User Manual 2.0 (2024) CN.pdf`: SHA256 `20666b02f06e291ffe88912866d62d37885d16fd426b60754b5183922be0d0f9`, 616 pages.
- `third-party/tools/ghidra-csky/C-SKY_ISA_Reference_Guides/Xuantie E804 User Manual 2.0 (2024) EN-DeepL.pdf`: SHA256 `716f6a7d9b05d4d42b92bba672110777e02fcd7ef0de1e035bd3515980f906ea`, 1084 pages.
