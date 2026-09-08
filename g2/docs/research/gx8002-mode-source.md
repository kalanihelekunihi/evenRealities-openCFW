# GX8002 mode initialization and tick

The pinned NationalChip commit `8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`
provides `lvp/lvp_mode.c` and its actual `LVP_MODE_INFO` header. The recovered
firmware contains two entries, IDLE and TWS. Their callback objects and the
list are still retained dependencies; recovering control flow does not claim
ownership of those objects or callback implementations.

`LvpInitMode` initializes the loop flag, selects the first matching mode with
IDLE as fallback, calls buffer initialization, then calls mode initialization
with `LVP_MODE_INIT_FLAG`. It reloads the current index after each callback.
The source preserves the observed repeated selection store and shares that
store across the two successful branches. This fits the original 84-byte
interval with the original 12-byte frame using native macOS C-SKY GCC.

`LvpModeTick` invokes the selected callback only when non-null, then reads the
live loop flag. The compiled function takes 32 of the original 36 bytes and
retains the original 8-byte frame. Neither function caches state across a
callback. Their mode enum and callback signatures come from upstream.

Decoded stock and candidate executions agree with independently generated
read/write/call traces in 2,664 initialization and 480 tick cases. Checks
include unmatched mode values, signed-boundary bit patterns, callback-induced
mode changes, loop termination and caller-register clobbering. Eight regression
checks include incorrect flags, stride, stack frames and invalid indices.
Callback-produced indices outside the two-entry list are not qualified. No
hardware, interrupt timing, or whole-mode functionality claim follows from
these modeled returning callbacks.

The authenticated upstream IDLE and TWS source files are recorded separately
in `gx8002-mode-callback-source-identification.json`. IDLE's empty tick and
zero-return buffer initialization are original behaviors. TWS needs further
configuration and dependency recovery before source admission.

Integration completed with 292 passing tests and a verified native macOS
EVENOTA package. The source copyright/notice correction was followed by a
fresh targeted replay and unchanged machine-code assertion. Four notices are
now packaged. Codec ownership is 8,584 C bytes, 120 architecture assembly,
2,216 source data, 80 metadata, 334 fill and 314,758 retained bytes. This
remains an experimental hybrid and the full source-only goal is active.
