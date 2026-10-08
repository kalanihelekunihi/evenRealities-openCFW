# Node bounds early-zero and filtered next search return

Partial/unaccepted;80 instructionbytes48468E..4846DE continuing48465624Bframe. R2=nodeword+12signed>=1→48469E;elseR1=word[node+20],R0(previous44FAA8result)--wrap;signedR1<R0→48469E;otherwiseR0=0earlyreturn4846DC.

48469EentryR4cursornonnull→freshword[cursor]R4next;zero→freshheadword[R5+68]R4. Loopnode:statusword+80!=1skipnext;byte+88zeroacceptfilter;nonzerofreshbyte+88compareUXTB(R6entry2),unequalskip. FilterpassR1=nodeR4,R0=ownerR5;4848B2(liveR2/R3);zeroresult→freshnextword[node]repeat;nonzeroR0=nodeR4return. ExhaustedR0=0. POPR1savedentryR3,R4/R5/R6/R7/PC24B. Preserveearlyboundsreturnbeforesearch,begin-after-cursor,freshbyte/nextloads andcallbackresultpredicate. Helper4848B2contractunresolved. No C,freeze,wholecoverage or equalityclaim.
