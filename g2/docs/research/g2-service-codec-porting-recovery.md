# G2 codec UART-porting recovery

The retained `platform\audio\service_codec_porting.c` path is exactly two
functions / 342 body bytes plus a 72-byte pointer pool, for 414 physical bytes
at `[0x0058FB52,0x0058FCF0)`. The retained diagnostics give exact names
`uart_init` and `uart_close`. Seven entries, 24 body calls, four independent
path references, both neighboring boundaries, and zero stored, indirect, or
strict-interior targets are pinned.

`uart_init` performs one-time initialization of a 64-byte receive ring, installs
the UART3 receive callback, and resumes that port. `uart_close` suspends UART3
when active. Twenty calls are admitted EasyLogger diagnostics and three are
first-party UART-service operations. The remaining call is the exact
production-source-owned `ring_buffer_init` from AndersKaloer's dynamic
Ring-Buffer lineage. Stock behavior selects the already established compatible
commit interval `cda00e1…` through `190e30b…`; this call adds no narrower
discriminator.

No codec-vendor algorithm or opaque reusable implementation is present in this
porting object. The authenticated Ring-Buffer source supplies the only reusable
body, while UART lifecycle and callback ownership remain first-party.

The object is now production-routed through clean-room
`service_codec_porting.c`. Two selector-isolated Cortex-M55 leaves contribute
126 text bytes plus two alignment bytes with four strict relocations. Guarded
redirects replace both callable bodies (342 bytes) and preserve the 72-byte
authenticated diagnostic/literal pool. Host tests cover first initialization,
UART3/ring/callback arguments, active-state idempotence, resume failure, close
idempotence, suspend failure, and successful close. The canonical
overlay/component/package identities are 240,032 / 3,763,428 / 4,541,922 bytes
with SHA-256 values
`2db11ff707bf253280eb07667c3d76954347cc9e31796c7589faf788fed629ae`,
`b3ee7d2fb560f134bd5c4a27eb8203abdc0dd9482816319be0b03320fc2067ed`,
and `275a9e691c0bad851f7adbc80ed2abc1580e13d67f031912e198f984d18f7f85`.
The 2,567,304-byte flash plan has 3,683 placed, two unresolved, five
container-only, and six protected regions; SHA-256 is
`bfdbc3b09c31f281cabb3b31b95f80523c7cfdd62edc83677f5f9adc50aac60f`.

No image was signed or flashed. Live UART electrical behavior, callback timing,
and GX8002B interoperability remain explicitly blocked because no authorized
responsive G2 pair or live codec target is available. This porting-object
software gap is closed; the other Apollo codec-service objects and the wider
firmware remain incomplete.
