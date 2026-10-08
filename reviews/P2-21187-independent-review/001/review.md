# P2-21187 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x48162C..0x4816C6 (154 bytes); instruction and literal-reference outputs match. The code keeps the full quotient `index >> 5`, adds seven for the second bank, uses a 128-byte bank stride and the low-five-bit slot, and performs full-word stores in the recorded order. Selector 0 writes the first pair, selector 1 the second pair, and selector 2 performs all four stores in A/B order for each bank. Other selector bytes return 6 without stores. There is no index bound or helper call; the 16-byte saved-register frame excludes LR, and BX LR returns after POP. Array identity/ownership remains unproven.
