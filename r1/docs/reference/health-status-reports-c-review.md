# R1 hardware health status reports in C

`native_health_status_reports.c` supplies the group-4 callback `0x43788` and
packet reporter `0x4c678` as ordinary C. The
[review receipt](health-status-reports-c-review.json) binds REA bytes, production
hashes, direct/integrated comparisons, rejected defects and qualification.
The recovered child name `r1_touch_status_report` is retained; its packet reports
hardware wear state.

The callback ignores its event argument and captures phone status as 1 for zero
mode or 2 for any nonzero mode. It logs that captured value using the stock fresh
mode queries, then calls phone operation 3 with the four-byte zero-extended status
word, first argument 1 and second argument 0. Phone errors do not suppress the
subsequent local report. That report initializes all twelve packet bytes, sets
`00 09 8c 00 <boolean-mode>` and sends length five. Mode is freshly captured after
the phone call, before connection queries. The first full-word handle equal to
`0xffff` suppresses sending; otherwise a second fresh handle is used without a
second sentinel check. A disconnect between reads therefore still reaches the
TX API with the newly read handle. The new routines introduce no assembly or RAM
ownership. The registration unit's callback declaration is refined; its object
remains unchanged.

Direct verification passes 6,192 paired cases covering mode values, changing log
modes, ignored null/invalid event pointers, full-word connection results, handle
changes between reads, phone failures, captured-versus-fresh status, mutable status
words and packet buffers, and interrupt masks. Another 3,840 cases execute actual
C phone-operation, response-header and phone/glasses connection-getter functions,
including invalid phone handles, header/payload mutations and live connection
field changes. Their existing ABI boundaries remain intact. Lower response-send,
TX queue and logging providers remain modeled.

The fixtures compare public state, provider arguments, all twelve initialized
packet bytes, the five-byte length, phone header/payload and the captured status
word, and check preserved registers/SP/masks/FPSCR. Existing subscriber invocation
uses a void boundary and ignores callback results. Void R0, caller-clobbered
registers, APSR and private stack are excluded. Eight compiled defects are rejected:
reversed phone mapping, wrong packet header, wrong length, cached handle, second
sentinel check, late status capture, phone-error short circuit and wrong structured
tag. Physical/concurrent execution and BLE delivery remain unverified.

All 652 units compile and both relocatable compositions pass without duplicate
strong symbols. All 651 earlier objects remain unchanged. The group-4 callback is
resolved without new imports, leaving application/bootloader imports at 169/34.
Manifest validation passes. Its 106-byte entry is added to the working inventory;
the child retains its 68-byte span. Neither body qualifies as exact, so the source
plan stays at 4,369 source-built bytes. A fresh hybrid matches the locked application
with 641,791 executable pull-through and 248 resource bytes. Complete source-only
linking and byte identity from C remain unfinished.
