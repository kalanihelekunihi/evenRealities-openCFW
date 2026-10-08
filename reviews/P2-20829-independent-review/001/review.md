# P2-20829 independent review

Status: **partial / unaccepted**.

Fresh replay passed for the 36-byte function at 0x47CBC4..0x47CBE8; locked-image SHA and all source receipt hashes match, and decoded instructions tile the range with the loop branch landing on an instruction boundary. The routine reads the initial state, loops while unsigned index < length, combines each input byte with the state high byte, indexes a word table, updates state with the byte lookup result XOR state<<8, then writes state once. For length zero it still reads and writes the state word. R0 remains the input pointer; the 12-byte frame is popped before BX LR. Table contents and polynomial meaning are not inferred.
