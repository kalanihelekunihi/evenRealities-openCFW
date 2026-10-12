# Image-A KWS task-word provenance boundary

The authenticated image-A XIP body `0x10206cb0..0x10206d7c` allocates a
32-byte task array after saving registers. Direct C-SKY disassembly (from
`binh_a_stage2_xip.bin`, loaded at `0x10203004`) shows `subi r14,r14,32`
at `0x10206cb2`, then exactly five writes into that frame:

| Stock instruction | Task word | Stack offset |
| --- | ---: | ---: |
| `0x10206cc4 st.w` | 1 | `+0x04` |
| `0x10206cdc st.w` | 2 | `+0x08` |
| `0x10206cf0 st.w` | 6 | `+0x18` |
| `0x10206d0a st.w` | 5 | `+0x14` |
| `0x10206d0e st.w` | 7 | `+0x1c` |

At `0x10206d76` the body passes the frame base (`mov r0,r14`) to
`0x10208c14`. That child passes all 32 bytes to resident memcpy at
`0x10025738`, destination `0x2002e85c`. No native write to frame offsets
`+0x00`, `+0x0c`, or `+0x10` occurs in this loader. Its sole retained direct
caller `0x10206d90` passes no pointer or values: it saves `r4,r15`, tests
its own argument, and directly calls `0x10206cb0` at `0x10206d98`.

The three words therefore originate from whatever bytes occupied the callee
stack frame before this invocation. That prior stack content is not established
by the retained caller or startup. The selected C imports
`gx8002_xip_kws_ambient_task_words` to capture the three values explicitly
before copying eight words. A source-owned constant/default or an uninitialized
C local would invent behavior or invoke undefined C behavior. Closing this
contract requires authenticated prior stack producer/precondition, or a
separately qualified machine-level ambient-stack model. The current one-import
candidate accurately exposes this boundary and is not a full runtime image.
