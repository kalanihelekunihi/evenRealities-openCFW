# Second repeated mode-selected signed scaled parameter

Partial/unaccepted. Exact130 instruction bytes484D20..484DA2, continuing open32B frame484A98 with objectR4. First selector: fresh byte+40==1 selects14; otherwise separately reread byte+40==2 selects12; otherwise10. Zero test branches to R1=0 at484D3E then484D9A, locally unreachable because all selected constants are nonzero.

Nonzero branch repeats selector with fresh byte reads and freshly loads word+44. R0=wrap32(selector*word+80), then signed SDIV by160 truncating toward zero. Signed quotient<2 yieldsR1=1; otherwise perform selector again with fresh reads, reload word+44, repeat wrap multiply/add and signed division intoR1. At484D9A call4D489E(object+64,R1,liveR2/R3). This mirrors prior map21870 selection but uses the distinct second helper4D489E; preserve repeated accesses and call separation. Frame remains open; next word+44 signed divide begins484DA2. Helper contracts unresolved. No C,freeze,wholecoverage or equalityclaim.
