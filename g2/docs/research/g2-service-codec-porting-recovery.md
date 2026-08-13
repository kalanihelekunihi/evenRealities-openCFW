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
body, while UART lifecycle and callback ownership remain first-party. The
object is not yet production-routed.
