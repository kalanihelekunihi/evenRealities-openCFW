# Independent review — P2-21473

Status: partial; accepted: false.

Fresh replay passed for the exact 130-byte span, and regenerated instruction/reference records match the candidate. Selector choices 14/12/10 are made from separate fresh object+40 reads; the local compare-to-zero branch remains present even though these constants make it unreachable.

The nonzero branch repeats the selector reads, freshly loads object+44, performs wrap32(selector*word+80), then signed SDIV by 160. Signed quotient below two selects one; otherwise the selector and word are reread and arithmetic recomputed. The final helper is 4D489E(object+64,R1,live R2/R3), distinct from the prior map's 4D4892 call. The 32-byte frame remains open at the boundary.

Helper contract and subsequent word+44 processing are unresolved. Review remains partial/unaccepted.
