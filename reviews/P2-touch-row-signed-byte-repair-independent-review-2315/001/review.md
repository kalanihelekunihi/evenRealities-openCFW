# Independent review 2315

**Result:** PASS_SCOPED.

Isolated replay regenerated all 480 fixtures. Source and both bodies [0x6330,0x6352) and [0x6352,0x6384), plus candidate file hashes, match. Decode confirms 6330 forwards the four registers to 6270 and maps budget thresholds (>3, >7, >15) to categories 1/2/3, otherwise 0. 6352 reads row halfword14, row byte135, context config byte78, and row byte122; validity 1/10 selects deduction8, otherwise0. It calls 6330 and ORs 0x80 into the result. Exact division arguments, result, bit7 and R4-R6/SP preservation pass.

**Limits:** Cases use selected counts/percentages/shifts and validity values; arbitrary inputs and physical field meaning remain open. This packet verifies the signed-bit-setting behavior despite its provisional “repair” label, not semantic validity of that naming. No canonical admission.
