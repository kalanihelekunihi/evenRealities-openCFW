# ADC lookup and close read ordering

`adc/stock_named_adc.c` now explicitly reloads the live device-name pointer
before the record-name pointer for every open/close comparison. Native
close `0x547f4` and open `0x54864` use that order. The shared C lookup uses
volatile views with separate loads; the previous C expression allowed the
compiler to load the record name first. Close also uses volatile views for
the opened/input fields, the remaining-channel scan and initialization byte.

REA and raw instructions agree on the close sequence. Close retains the
native input selector passed to `nrfx_saadc_channel_uninit`, rather than
substituting the record index. It clears the chosen record after that call,
scans opened flags in order, always reads initialization after the scan,
and calls driver uninit only when every channel is closed and initialization
bit zero is set. The initialized byte is cleared after driver uninit.

The probe passes 20,577 stock/C comparisons: 20,481 close cases and 96
already-open lookup cases. It varies all triples of opened values from
0/1/2/255, initialization 0/1/2/3/255, three names plus a miss, and sixteen
callback mutation modes. The additional close case changes the device name
during the first record-name load. Stock captures the old device name and
closes input 6; the old compiled provider reads the new name and closes
input 4. The repaired C matches stock. This is a controlled reconstruction
regression, not a claim of an observed hardware failure.

Actual ADC adapter code executes; string comparison and Nordic uninit
callbacks are modeled and clobber caller-saved registers. Checks compare
exact watched CPU read addresses/widths/order/values, SDK arguments/callback
sequence, return value, all ADC state bytes and the live device-name pointer.
They verify callee-saved registers, SP, interrupt masks and eight-byte
callback alignment. Native close callbacks use caller SP-16; C uses SP-24.

ADC registration and sample function sections, configuration and operations
retain their exact bytes and relocation identities. The other 561 source
units are unchanged. All 562 R1 units compile without failures or duplicate
strong symbols. Manifest eligibility and imports remain unchanged at
211 application / 34 bootloader, and `make sources-check` passes.

Full open initialization/configuration and its delay path were not validated
by these already-open cases. Physical SAADC lifecycle, general concurrency,
private frames, arbitrary faults, exceptions, timing, final boot/linking,
qualification and whole-image byte identity remain unproven. No G2 gate
or source-plan selection changes.

Exact bindings are in [the machine-readable review](adc-c-close-read-order-review.json).
