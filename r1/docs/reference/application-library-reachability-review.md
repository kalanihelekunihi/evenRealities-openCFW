# R1 application algorithm-library reachability

The recovered application linker script previously used `KEEP` for every
text and constant section in `goodix_primitives.c.o` and
`gomore_primitives.c.o`. Both complete C source units still compile, but the
blanket retention included many functions that no current application entry
or function table calls. `r1/config-recovered/openr1_sdk.ld` now gives these
two objects normal section reachability. Explicit firmware entry roots and
the `.openr1_goodix_api` registry remain retained. Any relocation from live
code or data into either library retains its target section.

The ignored substitution probe at `build/r1-vendor-gc-probe-20261110/`
first changed only those two `KEEP` directives. The permanent linker edit was
then checked through `tools/build/r1_application_link.py`, using the same
975-unit source report. Its receipt is
`build/sources-r1-vendor-reachable-20261110/app-link/report.json`.

| Strict application measure | Before | After |
| --- | ---: | ---: |
| Full flash load (`TotalFlashUsed`) | 724,376 bytes | 602,872 bytes |
| Configured flash capacity | 696,320 bytes | 696,320 bytes |
| Overflow | 28,056 bytes | 0 bytes |
| Unresolved functions | 24 | The same 24 |

The change saves 121,504 bytes in the currently reachable graph and leaves
93,448 bytes of measured headroom. All registry-size and reset-placement
assertions still pass. The linker still returns failure on the 24 genuine
undefined functions; this is not an application executable. Implementing
those functions can make additional library sections reachable, so final
memory fit must be measured again after the imports are closed. This change
does not remove reconstructed C source or establish stock byte identity.
