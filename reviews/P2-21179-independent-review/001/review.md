# P2-21179 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x481468..0x4814F0 (136 bytes); instruction and literal-reference outputs match. The full input pointer is null-checked before selector dispatch. On the two-bank mode, the helper receives the full selector and low-byte selector value, and its full result is staged at SP0. The code then makes fourteen independent input-word reads and direct stores across the two seven-word target banks; there is no target read or read/modify/write. Since bank one writes before bank two reloads input, aliasing can affect later inputs. SP0 is reloaded for MSR PRIMASK. The return/status and unwind remain outside this prefix.
