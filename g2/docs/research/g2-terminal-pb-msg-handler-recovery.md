# G2 `terminal_pb_msg_handler.c` recovery

Status: complete linked-object census and fail-closed behavioral analysis; no
historical source candidate and not production-routed. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

The retained path is
`app\gui\terminal\terminal_pb_msg_handler.c`. Ten path-bearing functions and
17 adjacent pathless functions form one closed 27-function object at
`[0x005E8178,0x005EA224)`. Function bodies contribute 7,688 bytes with
SHA-256 `908f4e8e9712ee5793cbe18868b676996b49dbcd59d9d7db3b29552b2e3b0be6`;
14 alignment/literal regions contribute 676 bytes with SHA-256
`7b9b04cd006de1b723e39877de953f335149d4110a8ecacc79059abcc4dfdca6`.
The complete 8,364-byte physical object has SHA-256
`935c32ef5f91486af8104652d24b97a29b2c5afb6dc3d1a3f952599cc7d740f1`.
The preceding bytes belong to a literal pool and an unrelated Thumb prologue
begins at `0x005EA224`, closing both boundaries.

Nineteen function names survive as diagnostic strings. The other eight names
in the function map are deliberately semantic labels. The most important
restorations are the state predicates and name mappers at
`0x005E8276..0x005E8346`, the callback at `0x005E8814`, five small tail action
handlers, the event-name mapper, and `terminal_machine_handler` at
`0x005EA028`. The exact byte ledger is pinned in
`tools/manifests/g2-terminal-pb-msg-handler-function-map.tsv`.

## Dispatch and ingress

The 13-entry table at `0x0072EB78` has a null event-zero slot followed by 12
Thumb pointers:

| Event | Action |
| ---: | --- |
| 0 | none |
| 1 | mode sync |
| 2 | host status |
| 3 | ASR result |
| 4 | session status |
| 5 | agent content |
| 6 | query |
| 7 | heartbeat |
| 8 | error message |
| 9 | session list |
| 10 | session-switch result |
| 11 | new-session result |
| 12 | session-ID changed |

`terminal_machine_handler(event, payload, length)` rejects event values above
12, logs the event name through a 13-entry name table, rejects a null action,
and otherwise invokes the selected action with `(payload, length)`. Invalid or
unhandled values return `-1`. Twelve direct external calls at
`0x005E4650..0x005E4718` feed the dispatcher. The action table supplies the
only entry for its 12 actions.

The runtime callback at `0x005E8814` has pointer cells at `0x005E47A8` and
`0x005E9348`. It accepts only `(status == 0 && payload != NULL)`, interprets
the first payload byte as a Boolean, clears two UI/session values when false,
and forwards the Boolean to `terminal_request_runtime_event_if_allowed`.

Across the image, 56 `BL` encodings target exact entries and 14 stored pointers
target exact entries. An all-byte pointer scan has 54 entry/interior numeric
windows; all remaining values are instruction or packed-data collisions. One
raw `BL` decoder candidate at `0x00569C28 -> 0x005E9D6E` is not control flow:
the site is the second halfword of the valid four-byte `UXTAB` instruction at
`0x00569C26`. There are no real strict-interior branches and no `B.W` entry or
interior targets.

## State and message behavior

The main terminal state object is based at `0x2006E0D0`. The recovered leaves
establish two state sets: runtime events are allowed in states
`{0, 2, 7, 11, 12}`, while states `{1, 2, 3}` are treated as processing. A
session lookup walks a counted table using a `0x90`-byte stride, compares the
session ID at record offset `0x9C`, and returns the cached status byte at
offset `0x122`. Session and host status mappers retain stable textual names
for diagnostics.

The mode-sync handler compares the requested mode with the current mode,
returns a status reply when no transition is needed, and otherwise performs
the complete terminal enter/exit sequence: running-app teardown, UI/session
reset, callback registration or removal, delayed startup, transport/display
notification, and synchronized mode state. Session-ID changes reset dependent
terminal state and reconcile the active session. Await-user and runtime-event
handlers gate requests against the current state instead of unconditionally
changing UI state.

Agent content is session-matched before use. In the main terminal state it
derives a runtime-event bit mask from content type and tool markers; duplicate
tool-start events inside 2,000 ms are dropped. Queries are ignored outside the
active main interface and otherwise emit runtime event `0x15`. Session-list
messages reconcile the current session, refresh the visible list when needed,
and log at most ten list entries. The remaining action functions handle host
and ASR status, heartbeat/error reporting, session switch/new-session results,
and the final session-ID update.

The historical source tree and license remain unavailable, so this closure is
binary evidence, not source ownership. No clean-room candidate exists, the
object is absent from `overlay.json`, and OpenCFW claims zero production bytes.
The next first-party retained-path target is selected by the refreshed frontier
census rather than inferred from address adjacency.
