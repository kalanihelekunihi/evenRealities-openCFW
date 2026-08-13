# G2 teleprompt file-list recovery

Status: read-only, fail-closed closure of stock 2.2.6.10
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

The historical source and producing commit remain unavailable. This compact
storage object is not production-routed.

## Reproduction

```sh
make teleprompt-file-list-closure
```

The target authenticates the stock image, complete object, ingress, provider
surface, and aggregate retained-path frontier without hardware access.
