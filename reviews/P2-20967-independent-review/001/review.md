# P2-20967 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed in isolated output; fresh extraction matches candidate data exactly. 12 bytes at 0x78B648..0x78B654; three template words (1, 0, 0), all consumer loads in 21362. Pointer at 0x47E614. Literal values and consumer records were retained from the locked artifact; ownership/exhaustiveness is not claimed.
