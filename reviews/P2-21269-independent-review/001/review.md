# P2-21269 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x482900..0x482946 (70 bytes); candidate instruction/reference outputs match. The reverse copy uses signed index termination with fresh source-byte reads and four-byte-back destination stores. Count is loaded independently for increment and later key/value address calculations; byte count wraps through UXTB storage. The quarter-clamp helper result drives the register-shift mask construction and bitmap update. The shared 32-byte POP returns saved entry R1/R2/R3 into R0/R1/R2, potentially modified by earlier SP0/SP4 diagnostic writes; it does not return the helper/status result.
