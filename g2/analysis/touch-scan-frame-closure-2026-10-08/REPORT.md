# MSCLP frame loading and scan trigger

Independent source ../../components/touch/scan_frame_offline closes9178 and6928. Original/native MMIO reads/writes match in60 comparisons (30 direct loader cases,30 start cases; mode values unused in start cases are deliberately repeated). Synthetic registers have no hardware sideeffect model; no function-call stubs are used.

9178 mode5 writeszero atHW+3020 then framewords0..4 to3024..3034. Mode11 writeswords0..4 to3000..3010, word5 to3020, thenwords6..10 to3024..3034. Allothermodevalues writewords0..5 to3020..3034. These modes select different frame widths; mode5 needsfive words, defaultneeds6, mode11needs11.

6928 enablesHWCTL bit31, writes0x01110011 toHW+120 withreadback, acknowledges pending interrupts via0xc1011111 at+100 withreadback, loads mode6 six-word frame, ORs6 then1 into+3034 in two separately observable read/write operations, thenwrites1 at+3800. The ordering is preserved by volatile accesses; combining those writes would not be justified by plain final-register equality.

This closes the frame/trigger dependency of the saturated scan. It does not prove physical excitation or IRQ/analog behavior. Hardware mode transition6ac0 remains an explicit boundary. No production image, index, commit, shared campaign, checkpoint or device write.
