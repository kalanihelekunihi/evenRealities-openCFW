# Packet builder nonempty mask paths

Extend 1471 with nonempty first and second pin lists and mode-1 subrecords. Both lists and each supplied subrecord reference the same bounded pin array, with counts zero, one or two. Pins begin at 0, 31 or 32. The independent mask model applies ARM register-shift semantics and checks every controlled 5188 argument.

When configuration byte +44 is nonzero, build its second-list mask and issue an additional 5188 call. Record mode 1 selects context byte +107 for this call; other modes retain the previously selected mapping. Mode 1 then builds its subrecord mask and issues another call using context byte +104. Group output pointer rules and iteration counts remain those documented in 1469.

The 486 original-instruction fixtures check exact full helper-call sequences, masks, mappings, incidental return and restored frame. 5548/5188 remain controlled; shared pin arrays and zero index halfwords constrain the fixture scope. Arbitrary nested indexing and real helper contracts remain unresolved. No canonical admission or C implementation.
