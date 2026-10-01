# Private P2 recovery 1496: C-SKY controller byte sender

Scope: `[0x10000B5C,0x10000BBC)` under the conditional BINH-A mapping. Three direct callers and all controller writes/polls are pinned. Run `python3 verify.py` here. Fixtures control MMIO words and input bytes; they are not hardware execution. No canonical or firmware-source changes.
