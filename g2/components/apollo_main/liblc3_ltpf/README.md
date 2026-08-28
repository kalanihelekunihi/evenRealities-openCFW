# Apollo-main liblc3 LTPF source overlay

This component routes the authenticated `lc3_encode` call at `0x0059145C` to
the maintained Google liblc3 v1.1.3 `lc3_ltpf_analyse` implementation. It is a
bounded source overlay for the official G2 2.2.6.10 Apollo-main base; it does
not claim historical byte identity. The standalone builder appends the
provider for qualification. The default canonical Apple build instead places
text and tables in two authenticated reclaimed NOP tails so the image remains
below the `0x007FE000` bootloader-update flag. The reviewed Linux profile has
sufficient headroom and retains appended placement.

The local linker is intentionally narrow. It accepts the complete LTPF
analysis text and constant closure, 16 absolute table-address relocations,
seven Thumb function-pointer dispatch relocations, and no external symbol.
The component supplies overlap-safe `memmove` source and an LTPF-specific
nonnegative Cortex-M55 square-root provider. Any new dependency, allocated
section, global ABI symbol, or relocation fails the build.

Build either reviewed profile with:

```sh
python3 g2/components/apollo_main/liblc3_ltpf/build_component.py \
  --profile apple-clang
python3 g2/components/apollo_main/liblc3_ltpf/build_component.py \
  --profile linux-clang
```

Run the software-only route and runtime qualification with:

```sh
python3 -m unittest g2.tests.test_runtime_liblc3_ltpf_overlay
```

The implementation, adapter, and runtime closure retain Apache-2.0 terms.
The complete license is `g2/third_party/liblc3/LICENSE`; `NOTICE.md` records
the selected commit and routing scope. The historical non-corpus 16/48 kHz
bodies remain individually unrouted and unchanged in the patched base.
