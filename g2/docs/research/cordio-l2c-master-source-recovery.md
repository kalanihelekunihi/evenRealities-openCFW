# Cordio L2CAP master source recovery

Status date: 2026-08-09  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

All three `l2c_master.c` functions survive in the complete 700-byte object
`[0x00536FBC,0x00537278)`, SHA-256
`1cdae8cc0feb879079330aad4ba53141ce701314d0be844fde9c61a2f90a9536`.
The functions contribute 658 code bytes; a two-byte alignment word and a
40-byte literal/trace pool account for the remainder. Three direct calls,
one registered receive callback, and zero interior pointers close ingress.

The selected Apache-2.0 source is Packetcraft r20.05c blob
`0f6c8c0594c0cd877f9c4fe22e42ef656863bbc4`, 5,222 bytes, SHA-256
`040a732f615345250d2cee7c8293c2e2c420b5bbaf264f65e7ec65117e0c0be3`.
Its three definition bodies are identical to Packetcraft r19/AmbiqSuite 2.x,
so this translation unit does not independently discriminate releases. Its
use with the already-proven r20/R4 connection-update component qualifies the
selection without making a false whole-release claim.

The receive function validates and decodes an L2CAP connection-parameter
update request, rejects malformed/range-invalid requests, and forwards valid
parameters to `DmL2cConnUpdateInd`. Initialization stores its Thumb entry at
`0x00537228`; the response function builds and sends the six-byte signaling
response. Production ownership remains zero and compiler reproduction is
deferred.

```sh
python3 tools/analyze_g2_cordio_l2c_master.py --json
```

The next translation unit begins at `0x00537278`; retained diagnostics identify
it as the SMP/L2CAP integration path. The companion `l2c_main.c` closure is now
complete, and `l2c_coc.c` is positively excluded from the stock image.
