# Independent review 1805: scoped pass

The 128 original-instruction fixtures execute 8058 with actual CRC, row selection and sequence-read code, without intercepted helpers. All 16 CRC-validity masks, both modes, mirror states and two current-row positions match output, status, selected pointer when reselection occurs and SP. Rows are synthetic 128-byte buffers with sequence words 1,3,2,4; the selection model applies strict unsigned greater-than and ignores CRC-invalid candidates.

This only establishes the tested synthetic four-row configurations; physical flash, concurrency and larger geometries remain unproved. No canonical acceptance or coverage change is made.
