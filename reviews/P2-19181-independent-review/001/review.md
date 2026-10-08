# Independent review: P2-19181

Status: partial / unaccepted. No source or gate changes.

Fresh replay of `0x46A23A..0x46A2AA` (112 bytes) matches candidate instruction/reference records. The first mode call distinguishes full result 1 (R1=0) from other values (R1 from the separately loaded global word); each path loads the shared global argument freshly. Later child calls occur in the listed order with fresh global-word reloads between calls. The `MVN` constant produces `0x00FFFFFF` for the forwarding call, whose result is then passed on separately. No inferred mode or layout contract is added.
