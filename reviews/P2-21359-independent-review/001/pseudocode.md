# Format parser flags, width and precision prefix

Partial/unaccepted;130 instructionbytes4839DE..483A60,continuation88-byteframe483960. Plus entryORR8bit2;spacebit3;hashbit4. Each freshSP48cursorincrementstore,R0=1→483A0A. Otherentry483A08R0=0. IfR0nonzero repeatflagdispatch4839AA. ElseR7width=0;freshcursorbyte→digitpredicate483032;nonzero call483044(&SP48),R7=result,branch483A48. Zero predicate freshcursorbyte again;not42star→483A48. Star: loadword[R9]→R7,R9+=4wrap; signedR7negative→R8|=2,R7=-R7wrap;freshSP48cursor++store. INT_MIN remains its wrapped negation.

483A48R4precision=0;freshSP48cursorbyte compare46dot;NE→483A8Eunresolved;EQ R8|=1024, freshcursor++store, independentlyreloadcursorbyte→R0. Fallthrough483A60 precisionparseunresolved. Preserve repeated cursor reads, pointer progression, fullword vararg width and signed-negative handling. No C,freeze,wholecoverage or equalityclaim.
