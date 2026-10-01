# Packet builder base flow at 56A4

The complete 452-byte body [56A4,5868) begins with the two-list mask described by 1467. Select a context mapping: mode +117 equal 2 uses +100, equal 5 uses +109, otherwise +99. Retain +100 separately. A second mapping uses +100 for mode +116 equal 2, +107 for mode 4, otherwise +99.

Group 1 selects descriptor output word +44, index-table word +52 and four iterations; other groups select words +40/+48 and five iterations. Each iteration calls 5548(group,index,currentOutput,descriptor). Read two halfwords from indexTable +4*index: the first selects a stride-144 record, the second selects its subrecord. Record mode +122 equal 1 uses the second mapping; mode 2 uses the first mapping; other modes use context +100. Group 1 advances output by 20 before 5188(mask,mapping,output), then by 24, giving stride44. Group0 stride is28. Extra list/subrecord mask paths remain outside these fixtures.

Eighteen original-instruction fixtures use record mode zero and empty lists, checking exact two-helper call sequences, mode selection setup, both iteration counts/strides, incidental R0 from the last controlled helper, and restored frame. 5548/5188 remain controlled. Full extra-mask behavior and their contracts remain open. No canonical admission or C implementation.
