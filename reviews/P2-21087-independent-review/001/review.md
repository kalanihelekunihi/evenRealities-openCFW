# P2-21087 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x47FEA0..0x47FF26 (134-byte prefix); instruction/reference outputs match candidate. Mode dispatch uses the unsigned compare after explicit mode-0/mode-2 handling: mode 1 reaches its own query path, while mode 3 and other values branch outside this prefix. Mode 0 performs ordered independent full-word RMWs with ignored helper returns. Mode 1 writes byte SP0, issues the query, then uses a fresh byte observation and full helper results to choose external labels. The 24-byte frame remains active; no final status/unwind claim.
