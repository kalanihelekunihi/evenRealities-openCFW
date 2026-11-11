# Named ADC C wrappers

`r1/src/application/adc/stock_named_adc.c` replaces the naked open/sample
wrappers with ordinary C. Open supplies local configuration storage to the
existing body. Sample initializes local storage from the fourth registry
operation argument, preserving the low-halfword fallback when conversion
returns without writing. Neither wrapper introduces a new driver or claims
ownership of Nordic SAADC beyond the existing implementation.

The driver bodies retain identical allocated section bytes and relocation
records. Initialization remains 12-bit, interrupt priority 6, no oversampling;
channel initialization retains the record index and two 64000-cycle delay
calls. The unusual close selector remains unchanged.

Verification executes the normal compiled source object, the previous object
and the locked stock binary in Thumb emulation. All three match across 864
open and 864 sample cases. Cases vary record match, opened/initialized flags,
initialization/channel errors, callback mutations, incoming fallback values,
partial/nonwriting conversions, and interrupt masks. Comparisons include
return status, callback order and arguments, state and output bytes, preserved
registers, stack restoration and interrupt masks. Callback scratch pointers
are normalized to their contents. Caller-clobbered registers and private
frame addresses/bytes are excluded from the typed C contract; private-stack
aliasing by an external output pointer is not claimed.

Four independently compiled defects are detected: zeroed fallback, wrong
resolution, reopening an opened record and omitted sample copy. A final clean
baseline passes after the defect runs. Source execution is guarded against
entering stock instructions. ADC, string, error and delay callbacks are
modeled; this is not physical conversion, electrical or timing validation.

Fresh REA bytes at 0x54864 through 0x5493b match the locked application image.
The companion JSON records the evidence identifier, byte hash, build hashes,
probe results and audit. The normal R1 build compiles 784 units without
failures or duplicate strong symbols; imports remain 114 application and 22
bootloader linker metadata. The strict source bootloader link succeeds.
No source-plan qualification or byte-identity claim is made.
