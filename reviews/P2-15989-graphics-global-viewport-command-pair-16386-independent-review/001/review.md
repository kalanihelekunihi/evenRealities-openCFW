# Independent review 15989

Partial, accepted:false. Fresh decode replay passed for 64 bytes. Loads global object pointer and all four coordinate words before first child; computes wrapped endpoints before clipping starts, packs low16 values, issues 272 then restores frame and tail-branches 276. Entry R0 is ignored; no null validation or post-child rereads.

Child/global/hardware effects remain unqualified; no admission or gate change.
