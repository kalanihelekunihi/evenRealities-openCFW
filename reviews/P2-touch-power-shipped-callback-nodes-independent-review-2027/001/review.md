# Independent review 2027

**Result:** PASS_SCOPED.

- The source hash and both candidate-file pins match the receipt. The two stored direct-call candidates map to the decoded call sites 0x3CA8 and 0x4638; surrounding instructions load node pointers from literals 0x3CB0 and 0x4648, and the latter caller also loads the false-result literal 0x464C.
- Independently decoded the node records at source offsets 0x8298 and 0x861C as six-word records. They match the recorded callback pointers 0x3621/0xA1C1, index 1, skip 0, params 0x200009C0/0x20000CCC, zero links, priorities 2/255, and per-record hashes.
- The records lie in the stated initialized-data source span [0x828C,0x8650), mapped to RAM 0x200004C0 by the separately reviewed startup evidence. This confirms the static correspondence and is consistent with the startup composition that preloads these bytes.

**Limits:** This is a static candidate scan and record mapping; scanning halfword-aligned BL encodings can include data/second instruction halves, and it does not establish all callers or indirect closure. The startup composition supplies the data span as a fixture precondition rather than proving every copied byte in this packet. Callback bodies/parameters and runtime mutation remain separate. No canonical admission.
