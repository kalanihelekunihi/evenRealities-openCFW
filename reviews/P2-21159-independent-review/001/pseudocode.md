# Frameless index/bit-mask and checked word-table query pair

Partial/unaccepted;52 instruction bytes480ED8..480F0C. Routine480ED8: fullentryR0 unsignedindex→R3=index>>5;storeword[entryR1]=R3 before nextstore. R1=1;R0=index&31;R0=1<<R0 using32bitshift;storeword[entryR2]=R0;return0BXLR. No indexlimit,nullcheck,orframe;aliasedoutputpointers cause secondstore tooverwritefirst. Fullindex retained untilmask operation.

Routine480EEE: loadR2 tablepointerliteral48173C beforevalidations. FullentryR0>=224unsigned→return5 (takes precedence overnulloutput). ElsefullentryR1null→return6. Elsefreshword[table+4*index]→word[entryR1],return0. Nooutputwriteonerror;nohelpercall;BXLRframeless. Tablecontentandownershipremainexternalrecoveryrequirements;referencewordretained. No C/freeze/fullcoverage/equality claim.
