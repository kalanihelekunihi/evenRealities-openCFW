# P2-21089 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x47FF26..0x47FFBA (148 bytes); instruction/reference outputs match candidate. Mode 2’s BFI update and two mode-3 write sequences use ordered fresh reads. Mode 3 helper calls retain fifth argument 1, with full-result error routing into FFB6; ignored results do not stop later calls. The shared FFB4 tail returns the retained full R4 status, while early FFB6 routes preserve their own R0. Stack SP0/SP4/SP8 mutations and ADD16/POP24 aliases are retained. Adjacent 0x47FFBA..0x47FFBC padding is excluded.
