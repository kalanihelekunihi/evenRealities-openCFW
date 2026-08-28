# liblc3 LTPF production overlay notice

This component incorporates the LTPF analysis implementation from Google
liblc3 v1.1.3, commit `96a3af0beb5487aca3b98a4b992a539a1f6d80d1`.
Google liblc3 and the openCFW adapter/runtime sources are licensed under the
Apache License 2.0. The complete retained terms are in
`g2/third_party/liblc3/LICENSE`; the upstream copyright/license header is also
retained in `g2/third_party/liblc3/src/ltpf.c`.

The component replaces only the call from the authenticated stock
`lc3_encode` caller to `lc3_ltpf_analyse`. It does not individually route the
historical 16 kHz body at `0x00438400` or the historical 48 kHz body at
`0x00438604`; maintained upstream source supplies those dispatch semantics as
part of one closed analysis subsystem.
