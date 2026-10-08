# P2-21069 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x47FAE8..0x47FB78 (144-byte prefix); instruction/reference outputs match candidate. The 24-byte frame first overwrites SP4 and the low byte of SP0, then performs ordered independent fresh word RMW operations through the listed global pointers. The byte-zero path calls query/enable helpers and proceeds despite ignored results; subsequent bit clears use fresh word reads. Independent bit tests guard the optional query and enable path. Final wrapper calls also have ignored results, and control continues at FB78 with the frame active. SP0/SP4 aliasing and potential helper writes are preserved; no return behavior or helper contract inferred.
