# Configuration validator with original shift helper

Original 6384 executes the original 6262 shift-factor helper whenever the low original flag bits equal 1. The 216 fixtures inherit the row validator models and exact write/call checks from packet 1413, replacing its controlled factor of 3 with the true ARM shift result. This changes the computed minimum and can change the early range-error result. The parent model checks those results directly.

Helpers 623C, 6352 and 6294 remain controlled. Mixed-row mode/width checks are supplied separately by 1415. Physical meaning and real deeper-helper effects remain unresolved. No canonical admission or C implementation.
