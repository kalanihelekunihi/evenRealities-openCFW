# Format parser precision and l/h length modifiers

Partial/unaccepted;128 instructionbytes483A60..483AE0,continuation88-byteframe483960. EntryR0=currentbyte afterdot;digitpredicate483032;nonzero decimalparser483044(&SP48)→R4precision,branch483A8E. Zero predicate freshcursorbyte not42star→483A8E;star word[R9]→R4,R9+=4wrap; signedR4<1 clamps0,else retains;freshcursor++storeSP48. Precision-present flag remains set even for negative star clamped0.

483A8E freshcursorbyte dispatch h104→483AC6,j106→483AF0,l108→483AA8,t116→483AE4,z122→483AFC;otherwise483B08. l:R8|=256;freshcursor++store;freshcursorbyte comparel;equalR8|=512 thenfreshcursor++store;both→483B08. h:R8|=128;freshcursor++store;freshcursorbytecompareh;NE→483AE2 unresolved;EQ R8|=64;freshcursor→R0,R0++ at483ADE,store pending483AE0. Keepbothflagsforll/hh, full signed starprecision clamp and repeated reads. No C,freeze,wholecoverage or equalityclaim.
