# Packet builder record-mode paths

This extends complete-body packet 1469 with record modes 0, 1 and 2 across both groups and context selection modes. Record mode 1 chooses the second context mapping and invokes an additional 5188 call using a subrecord-derived mask and context byte +104. The supplied subrecord count is zero, so that extra mask is zero. Record mode 2 chooses the first context mapping. Other record modes use context byte +100.

Fifty-four original-instruction fixtures check exact 5548/5188 call sequences, mapping values, both output strides and frame restoration. Helpers remain controlled; pin lists and subrecord lists are empty. Nonempty extra-mask lists and real helper contracts remain unresolved. No canonical admission or C implementation.
