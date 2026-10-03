# Independent review 6427

Disposition: **PASS_SCOPED**; `accepted:false`.

Receipt hashes and the EC0C..EC6E source slice match. GNU Thumb decoding confirms the first operation is a descriptor+4 load before null validation. Null or a fresh descriptor word failing the 0x01FFFFFF literal comparison returns 2. The valid descriptor is not bounds-checked here. Mode R1 is truncated to u8 and routes 0→EC36, 1→EC6E, 2→ECF2, 3→ED26, and other values→ED5C; those external mode bodies are outside this packet.

For mode 0, it freshly reads descriptor words at +4 and +8 and rejects either unsigned value >= 0x100000 with status 5. On success it rereads each word separately, masks each to its low 20 bits, and stores them to two distinct literal-backed words. It then freshly loads descriptor byte 0 and stores the full byte to a third literal-backed word, returning zero. The validation reads and publication reads are distinct; no atomic update is established.

This is local source-flow verification only. External mode targets and descriptor purpose remain unresolved; no canonical files or gates changed.
