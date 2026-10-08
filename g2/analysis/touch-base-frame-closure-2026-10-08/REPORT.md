# Generated base, mode and pin-function frames

Independent C in `g2/components/touch/base_frame_offline/base.c` closes GeneratePinFunctionConfig0x50e4, GenerateModeConfig0x52bc and GenerateBaseConfig0x5378. **2,304 original-instruction comparisons passed** (768 each), without function-entry stubs. Every case compares all256 destination bytes and128 internal-context bytes. Tests use reproducible randomized preexisting contents, dither values0/1/2/255, inactive CSD states0/1/2/4/5/255, inactive CSX0/5, and zero/nonzero field branches. Writes to dead stack scratch and memory-write chronology are outside this comparison.

## Recovered layout and behavior

Base frame is context+36's pointer. It occupies a256-byte configuration structure. The three mode records begin at offset144, each seven32-bit register fields: senseDutyCtl, swSelCdacFl, swSelTop, swSelComp, swSelSh, swSelCmod1, swSelCmod2. Defaults at ROM0xb41c and dither variants0xb470/0xb48c/0xb4a8 are typed register data. They are retained as independently named numeric configuration constants, not executable instruction arrays.

Internal bytes90/91/92 select dither only when equal1; values2/255 select defaults. Inactive CSX byte117==5 additionally sets bit0x100 in mode1's swSelSh after selecting its template. SDK semantics associate this switch with VDDA/2; physical voltage behavior is not established.

Pin function assignments initialize internal99..112 to255 and set active CSD map104=0. Inactive CSD byte116==1 assigns map99=1; ==2 assigns map100=1; other states allocate neither. Shield map107 gets the next available index. Internal98 records the resulting count2 or3. Mapped entries copy the register words from ROM0xb4c4 into base+112; unassigned destination words retain their prior contents. Maps107 and104 are reused by closed all-slot generation.

Base generation explicitly writes selected fields. **Offset52 (word13) remains untouched**, as do unassigned pin-function words and trailing bytes beyond the mode records. Zero epilogue delay fields at internal66/68 substitute1 before packing; nonzero fields are masked, not validated/clamped. IMO divider byte81 is decremented unsigned before mask0x03ff0000, so zero yields all divider bits set. Selector6 is a configuration value; this does not prove a measured oscillator frequency.

Pseudocode: construct selected base fields; copy default mode records; replace modes with dither templates when flags==1; overlay CSX shield bit; reset logical pin mappings; assign active/inactive/shield indices; write only assigned function words; return0. Stock mode-template function has no API status contract; return-register residue is intentionally not interpreted.

The public LP generator reference remains CapSense6.10 pin247a9a0f79eb976f144f5fbeb29488c1c2606517. Installed gitlink3.0.1 is a different reference. Exact stock-generated cycfg and producer compiler remain absent; semantic reconstruction is validated, exact compiled equality of this new independent C is not claimed.
