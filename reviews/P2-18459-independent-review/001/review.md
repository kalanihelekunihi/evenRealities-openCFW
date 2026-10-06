# Independent review P2-18459

Status: partial, unaccepted. No source or gate changes.

I independently replayed the candidate against the pinned firmware image (`19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`) and assembled the 136-byte interval at `0x460090..0x460118` with GNU ARM tools. The freshly generated instruction and PC-reference JSON matched the candidate byte-for-byte.

The three-function account is supported. In particular, the installer stores the incoming pointer through the global at `0x200746C8` before separately rereading the input object and storing that result via `0x200746CC`; this ordering allows alias effects. The search loop uses a low-16-bit index and fresh table/entry loads, has no visible count bound, passes the live R3 to `0x46CACC`, and on a zero child result reloads the selected entry before publishing it. There is no second null check after the child. The getter likewise performs a separate global reload before dereferencing, without a second null check. Child semantics and global/table ownership remain unresolved.

Independent evidence is preserved beside this report. No C implementation, firmware-source edit, gate change, or admission was made.
