# G2 teleprompt file-list recovery

Status: production-routed clean-room C closure of stock 2.2.6.10
`app\gui\teleprompt\teleprompt_file_list.c`.

## Result

The single 144-byte `teleprompt_file_list_update` anchor expands to the exact
`[0x0058BCE0,0x0058BDA8)` translation unit. Two four-/eighteen-byte helpers
missed by baseline Ghidra return and reset the global record. The three
functions contribute 166 body/instruction bytes; a 34-byte alignment and
literal pool brings the physical object to 200 bytes. The already-closed
`teleprompt_page_data.c` pool bounds its start, while retained `exit_prompt.c`
code bounds its end.

Six exterior BL sites reach exact entries. The three bodies contain twelve
direct calls, no internal or indirect call, and no stored entry pointer,
strict-interior BL decode, or unknown object target.

## Storage contract

The object owns a single `0xF52`-byte record at `0x201093D4`. Its first two
bytes are the file count logged by the update path, leaving `0xF50` payload
bytes. A null update is diagnosed and ignored. A non-null update copies the
entire record byte-for-byte; the getter returns the live global address; and
the reset helper zeros the complete record. Nanopb decoding occurs in the
first-party caller object rather than here, so this closure does not claim a
recovered private schema declaration.

## Dependency result

Ten calls are diagnostics at the admitted EasyLogger 2.2.99-equivalent
selected commit `a596b264…`. The remaining two are bounded/source-recreated
IAR DLIB `memcpy` and `memset` primitives. No third-party implementation is
embedded, no new family or version discriminator appears, and there is no
direct nanopb call.

The historical source and producing commit remain unavailable. A clean-room
implementation now supplies all three functions from compilable C, with an
explicit public record ABI and retained `memcpy`/`memset` provider seams.
Complete-span guarded branches replace all 166 stock body bytes in both
supported compiler profiles. The reviewed Apple and Linux builds each produce
52 bytes of leaf text with two strict relocations and generate complete Apollo
firmware images and packages. The 34-byte stock diagnostic/literal pool remains
retained because it is not executed by the redirected entries.

This is a software closure. Native tests cover null update, full-record copy,
live-pointer getter, reset, and compile-time layout assertions. End-to-end
device qualification is blocked by unavailable physical evidence; the storage
implementation itself performs no hardware operation.

## Reproduction

```sh
make teleprompt-file-list-closure
```

The target authenticates the stock image, complete object, ingress, provider
surface, production source, both compiler routes, live package consistency,
and the native behavior oracle without hardware access.
