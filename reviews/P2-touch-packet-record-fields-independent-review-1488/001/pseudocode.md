# Packet record fields at 51BC

The 250-byte body [51BC,52B6) is followed by alignment and mask literal. Index pair halfwords select a stride144 record and its stride10 item. OR decremented-nonzero row-configuration halfword +54, shifted16 and masked0FFF0000, into output word12.

Start output word16 at00400000. Record modes1/2/10 with matching context enable byte90/91/92 equal1 instead use00C00000 OR record-config byte51 shifted28 masked70000000. Descriptor word4 pointing to word+8 with bit12 set bypasses further fields. Otherwise combine config byte46 and byte48 shifted16 masked001F0000; mode1 with record byte58<=subindex uses bytes47/49 instead. Mode1 also ORs item byte9 shifted8. Store word16, return0 and restore frame.

The192 original-instruction fixtures distinguish source fields and cover enable,bypass,threshold,index andhalfwordcases, with no helpercontrols. Global ownership, pointervalidity andphysicalmeaningremainopen. No canonical admission or C implementation.
