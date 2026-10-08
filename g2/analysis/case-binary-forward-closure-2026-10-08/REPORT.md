# Case binary command validation and shared forwarding buffer

**2,160 fresh PASS original/independent comparisons**. [forward.c](../../components/case/binary_forward_offline/forward.c) reconstructs selected nonlocal handler08000E1C contract: destination byte+2 is **not2**, command byte+0 is **not3D**. Local commands/aging side effects explicitly excluded. Actual original event-set wrapper/kernel and independent byte copy execute, with no entry stubs. Source early returns for excluded branches are contract bounds, not their stock implementation.

## Layout and checks

Handler reads destination+2 **before length guard**; tests provide allocated300-byte inputs even when logical length0/1/2, so no arbitrary pointer/buffer safety is proved. Nonlocal path requires n>=5,reserved/direction byte+1=0,destination+2<=1. Mode0 requires unsigned byte+3 +5 ==n and posts20. Any nonzero mode requires LEu16 at+3/+4 +6 ==n and posts400. Modes0/1/2; lengths0/1/2/4/5/6/7/8/31/32/260/262; malformed/valid length fields, directions/destinations and NULL/coherent empty event groups tested. No checksum/trailer validation is established by this branch.

Accepted branch posts flag **before** copying alln bytes into shared200001B4. Ordered event/copy observation and guarded destination/input compare. Posting return is ignored: withNULL event, actual wrapper returns parameter error, **the payload still copies**. With allocated empty-wait-list event, real event bits update then copy follows. No producer/consumer context switch or live packet race is demonstrated; empty event wait list prevents waiter wake in this fixture. Thread consumer can subsequently use this shared mutable buffer; no ownership/generation token/deep copy transfer is supplied by the notification.

Outer consumer previously passes header length+1 to this handler; these are separate nested length checks. Do not call the extra byte a CRC/checksum without its actual consumer. Destination2 local parser and command3D aging paths remain next concrete analysis targets. All selected input/output capacities allocated; maximum tested262, no proof of actual full forwarding-buffer capacity or safe large-frame handling. Receiver-side classification is not a hardware acceptance guarantee.

Practical app/CFW implications: use correct nested length/destination/reserved fields; treat flags as readiness hints and retain protected payload ownership until actual consumer copy/use. The observed post-before-copy and ignored error order are real selected instructions; runtime scheduling or an owned-buffer patch's safety is not verified.

Build/run build_offline.py/verify.py. Source/tool/image/ELF hashes, exact cases and explicit limits sealed. All872 prior entries,110 audit inputs and4 checkpoints verified unchanged; no commits,index,production/device writes. Available local-command/trailer and forwarding-consumer paths remain actionable; no project-wide source-exhaustion claim.
