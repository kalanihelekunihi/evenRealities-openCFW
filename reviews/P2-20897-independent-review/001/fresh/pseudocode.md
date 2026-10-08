# Six-way shared low-byte flag tail explicit zero return

Partial/unaccepted;98instructionbytes;inherited40frame,R4caseflag. D7B6 R4=LOW8R4;zero→D812. NonzeroD7BCquery43D0CEbit1zero→D7E0;else47D8CE(liveargs),LOW8result→SP8,literal47D9AC→SP4,244→SP0;43D574(4,literal47D918,literal47D914,literal47D910,244,literal47D9AC,LOW8helperResult).
D7E0freshquerybit0one→D7F0;elseanotherquerybit2zero→D804. D7F0independently47D8CE(liveargs);LOW8result→R3;43CE9E(0x10400000,literal47D9B0,same,LOW8independentResult).
D804independently47D8CE(liveargs);LOW8result→R1;4ABD60(0,R1,liveR2/R3). D812R0=0;ADD SP20 discards16locals+savedentryR3;POP R4,R5,R6,R7,PC20 completes40frame. Explicitzero returnonallnormallyreturningpaths,caseflagnotreturned. Retainuptothreeindependenthelpercallsanddiagnosticstatuscalls. No C/freeze/wholecoverageclaim. RoutineendsD818.
