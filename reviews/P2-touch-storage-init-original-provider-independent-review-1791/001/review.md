# Independent review 1791: scoped pass

All 16 fixtures reproduce in isolated execution without function or return overrides. Original 486C builds the descriptor used by 898C; original A9D4 clears the 32-byte context, original capacity/geometry leaves return 128, original 4790 validates the synthetic numeric range, and original geometry/size/validation/row-selection code runs. Context bytes, return value, SP, stop PC and required PC-entry presence assertions match. Disabled initialization returns the pinned 0x093E0000 error; validation error remains the distinct 0x093E0002.

All memory regions are synthetic, so this does not establish physical storage behavior. No canonical acceptance or coverage change is made.
