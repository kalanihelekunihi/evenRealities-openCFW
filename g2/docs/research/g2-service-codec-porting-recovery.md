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
`2def566dbf70594c89471066a7cd17f6d1fa94196f65ff48237385396e9cfd19`,
`7228edb650fe39bda63480691fe94ed59d0807ca5e30846d35ec08e134e08350`,
and `c146ea7977a5521aa1df24a1a285768d7e2396fab96f117315a5baa2dcb65998`.
The 2,567,304-byte flash plan has 3,683 placed, two unresolved, five
container-only, and six protected regions; SHA-256 is
`80d2f655555786d495d9df72b85013dee8e0076554b0d2deb82159a5c876e292`.

No image was signed or flashed. Live UART electrical behavior, callback timing,
and GX8002B interoperability remain explicitly blocked because no authorized
responsive G2 pair or live codec target is available. This porting-object
software gap is closed; the other Apollo codec-service objects and the wider
firmware remain incomplete.
