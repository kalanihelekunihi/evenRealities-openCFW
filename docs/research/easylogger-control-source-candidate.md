# EasyLogger Apollo-main control source integration

## Result

Eight public EasyLogger control functions now form the first integrated
source replacement boundary for Apollo main. They use the authenticated
source-equivalent EasyLogger core at commit
`a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`, the recovered G2 configuration,
and the existing logger object at `0x20070BE8`. The G2 asynchronous transport
and uncertain port implementation remain stock seams.

The cluster is wired atomically into `overlay.json`. Its source and isolated
tests are:

- `components/apollo_main/core_overlay/runtime_easylogger_control.c`
- `tests/fixtures/runtime_easylogger_control_host.c`
- `tests/fixtures/runtime_easylogger_upstream_oracle_host.c`
- `tests/test_runtime_easylogger_control.py`

The host oracle compiles the pristine vendored `src/elog.c` and
`src/elog_utils.c` directly. Candidate state transitions, format masks,
bounded tag copying, lock transitions, and port-call ordering match that
oracle. The candidate also compiles freestanding for
`thumbv7em-none-eabi` with the reviewed overlay flags.

## Firmware corpus

The reviewed official Apollo-main corpus is:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `ota_s200_firmware_ota.bin` wrapper | 3,523,396 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| Installed image after the 32-byte preamble | 3,523,364 | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` |

All ranges below are installed-image addresses and use an exclusive end.

## Replacement functions

| Function | Stock range | Bytes | Stock SHA-256 | Candidate symbol |
|---|---:|---:|---|---|
| `elog_set_output_enabled` | `[0x0043D260, 0x0043D2CE)` | 110 | `34e10d7a43f9f578deadcb826f515aff9af06d607d5e79355901c74b1ce0adea` | `open_cfw_easylogger_set_output_enabled` |
| `elog_set_text_color_enabled` | `[0x0043D2CE, 0x0043D33C)` | 110 | `30d6f6b942386065bbd82a097450efe06d7d50a26a71b8b12690c0a2beb3f48c` | `open_cfw_easylogger_set_text_color_enabled` |
| `elog_set_fmt` | `[0x0043D33C, 0x0043D3A6)` | 106 | `819c008ba3c645a4d711ccec7eaca6cd6b573db2f27b188ae279c23f7464ea89` | `open_cfw_easylogger_set_format` |
| `elog_set_filter_lvl` | `[0x0043D3A6, 0x0043D406)` | 96 | `dc6524c43cb10777aa81332adc7b0e02b9f152afa4250077799308a1b951d06a` | `open_cfw_easylogger_set_filter_level` |
| `elog_set_filter_tag` | `[0x0043D406, 0x0043D416)` | 16 | `9885baca1970ff465b03c64473ca6737d6e801c604eee63aac14eef5d0494218` | `open_cfw_easylogger_set_filter_tag` |
| `elog_output_lock` | `[0x0043D416, 0x0043D438)` | 34 | `4d87d1bcc02e66513c6774076ff4ba4c1024c5592013439d7e8dfdf53bb483b0` | `open_cfw_easylogger_output_lock` |
| `elog_output_unlock` | `[0x0043D438, 0x0043D45A)` | 34 | `86bff518c98f24bd440f5ebe4150c5d66c0e0090e844c3af3c446ab53e4799ea` | `open_cfw_easylogger_output_unlock` |
| `elog_output_lock_enabled` | `[0x0043DA24, 0x0043DA60)` | 60 | `7e1cf06caefa3b03995700b9fb4ff7c42ae51d056a36bac00dd47960147a5864` | `open_cfw_easylogger_output_lock_enabled` |

The eight stock bodies total 566 bytes. They are redirected as one reviewed
control cluster so logger state and lock-transition semantics change
atomically.

The first four functions contain the upstream `ELOG_ASSERT` behavior.
Disassembly confirms the G2 assertion-hook global at `0x2007456C` and the
downstream assertion line constants 278, 290, 321, and 347. When a hook
returns, upstream continues and performs the requested assignment; the host
tests cover that sometimes-surprising behavior.

`elog_set_filter_tag` passes exactly 30 bytes to the retained `strncpy`
implementation and therefore does not guarantee a new terminator when its
input is at least 30 bytes. The candidate preserves this upstream behavior.

## Recovered configuration and object ABI

The selected functions need no private heap or newly allocated BSS. They
operate on the existing global logger object at `0x20070BE8`.

| Configuration item | G2 value |
|---|---|
| `ELOG_OUTPUT_LVL` | `ELOG_LVL_VERBOSE` |
| `ELOG_LINE_BUF_SIZE` | 1,024 |
| `ELOG_LINE_NUM_MAX_LEN` | 5 |
| `ELOG_FILTER_TAG_MAX_LEN` | 30 |
| `ELOG_FILTER_KW_MAX_LEN` | 16 |
| `ELOG_FILTER_TAG_LVL_MAX_NUM` | 5 |
| `ELOG_NEWLINE_SIGN` | `"\n"` |
| Color output | enabled |
| Directory/function/line formatting | enabled |
| Default assert format mask | `0xFF` |
| Default error-through-verbose format mask | `0x87` |
| Application filter after setup | `ELOG_LVL_INFO` |
| Core initialization filter | `ELOG_LVL_VERBOSE` |

The recovered 32-bit layout is:

| Field | Offset / size |
|---|---:|
| `ElogFilter.level` | `+0x00` |
| `ElogFilter.tag[31]` | `+0x01` |
| `ElogFilter.keyword[17]` | `+0x20` |
| Five 33-byte tag-level records | `+0x31...+0xD5` |
| `sizeof(ElogFilter)` | `0xD6` |
| Alignment padding | `+0xD6...+0xD7` |
| Six 32-bit format masks | `+0xD8...+0xEF` |
| `init_ok` | `+0xF0` |
| `output_enabled` | `+0xF1` |
| `output_lock_enabled` | `+0xF2` |
| `output_is_locked_before_enable` | `+0xF3` |
| `output_is_locked_before_disable` | `+0xF4` |
| `text_color_enabled` | `+0xF5` |
| Field extent / padded object size | `0xF6` / `0xF8` |

Compile-time assertions in the candidate pin every offset used by this
increment.

## Explicit stock seams

The candidate emits no undefined ELF symbols. Each retained seam is a typed
Thumb function pointer or fixed global, making the dependency visible in the
source and relocation-free after compilation.

| Seam | Address | Reviewed stock span / SHA-256 |
|---|---:|---|
| Assertion-hook global | `0x2007456C` | 32-bit function pointer |
| `elog_output` for the no-hook assertion path | `0x0043D575` | `[0x0043D574,0x0043D976)`, `d7c5fd89997fc677ecce543af7c33cd08614b832a47602f1fd895bb7ab45f90c` |
| Assertion fail-stop wait wrapper | `0x0044B0AF` | `[0x0044B0AE,0x0044B0B6)`, `5f9a6b47f08eb58759df839c742eeae1a6c396a5731d2aa80cb635be744cc64f` |
| `strncpy` | `0x0044B5A1` | `[0x0044B5A0,0x0044B610)`, `97b8f3f453cf4f85bd079916e7bbffcc11f7bef676034c2cb10911e2b9e74a1d` |
| Apollo logger port lock | `0x0044AA99` | `[0x0044AA98,0x0044AAA0)`, `2fb6d2601c395c6a59bc3845d47ec72d8969de2f06cdccc24472e5b5bee226ca` |
| Apollo logger port unlock | `0x0044AAA1` | `[0x0044AAA0,0x0044AAA8)`, `8ad0605e5a4ff829a0aa5a4aee5ae94860868616a3b45ae015ab959ad62fbe91` |
| Retained assertion source-file string | `0x006E3098` | stock read-only data |

The assertion output seam is reached only for invalid input when the
application has installed no assertion hook. The ordinary valid control path
does not enter the opaque output core.

## Standalone target artifact

With Apple clang 21.0.0 and the existing overlay target flags, compiling only
the candidate produces:

| Section / artifact | Bytes | SHA-256 |
|---|---:|---|
| `.text` | 762 | `af25a8aaa450531f66c6be2fb31d10e6a3d3c3ef7ba08bc7e40b8ac53b3dc2b0` |
| merged read-only data | 190 | `2b992fa589c355dcb3e8582aa45e16c894fd60ee56d3fea5154835f6a826e4e5` |
| extracted standalone overlay | 952 | `46fec4899d5c2652466284cdc037743d069a09673b8fe4bcce8e4b4abcbf0fb9` |

The source SHA-256 is
`4b310d835604b409dec3d404b7fcd48d28839a9b2807aef339549a7563d39bbe`.
The compiler emits 48 local read-only-data relocations: 24
`R_ARM_MOVW_PREL_NC`/`R_ARM_MOVT_PREL` pairs. The overlay extractor resolves
all 48. There are no undefined symbols, external ELF relocations, or
candidate-to-candidate call relocations.

Standalone function placement is:

| Candidate symbol | Offset | Bytes | Body SHA-256 |
|---|---:|---:|---|
| `open_cfw_easylogger_set_output_enabled` | 0 | 152 | `ee7a6eca7ee74265fc26720efc052efcb4a36ae360a7da32ce524d62a5240731` |
| `open_cfw_easylogger_set_text_color_enabled` | 152 | 152 | `71f33d42ed76745d989b8cafe6b9cc98808aa59609146ff664181d6555ee96f3` |
| `open_cfw_easylogger_set_format` | 304 | 160 | `7ad0fc369be4616e37a77b8054264f5ea3d56bea91fbecaaeb77f6240b39f8b1` |
| `open_cfw_easylogger_set_filter_level` | 464 | 152 | `f3be6c106be7c0e0a2c50b8ba57d433f4240d1cab9e1894e752fab6d00aaab7a` |
| `open_cfw_easylogger_set_filter_tag` | 616 | 22 | `20a788141ba9ef4a2434cbc60ed8bab16f9f78e6e04b3531752e290e0cd9fa13` |
| `open_cfw_easylogger_output_lock` | 640 | 36 | `e82a70b837847d145ef23c4039952e870da88e12844495cf909f55d789ec0e9a` |
| `open_cfw_easylogger_output_unlock` | 676 | 36 | `dad258a6c864670206666feb8aab2c980c5bd03981a9add24c6e0d10f74fe47c` |
| `open_cfw_easylogger_output_lock_enabled` | 712 | 50 | `420ec208e99c2fc5bdc40f3550725aea88a46feede67a74161207eefc26b80ca` |

In the complete source overlay, the linked placements and body hashes are:

| Integrated symbol | Offset | Bytes | Body SHA-256 |
|---|---:|---:|---|
| `open_cfw_easylogger_set_output_enabled` | 107,348 | 152 | `042bd063b711f15ca05725528f7e4866d731ca4169b9a3c35b8d4d7fd08eb900` |
| `open_cfw_easylogger_set_text_color_enabled` | 107,500 | 152 | `347d78dae7a0c540cfc424800c3bb7505ee541745a9dbcc70bc840845f50ec45` |
| `open_cfw_easylogger_set_format` | 107,652 | 160 | `1e9a464fde89983d162ae4eae24b7d43413c22e42123d6c639c20edf7379b358` |
| `open_cfw_easylogger_set_filter_level` | 107,812 | 152 | `01a5e363125505fd198503bd2b28ac262e2c1bd58011a8d59d6eb4a92e29ac03` |
| `open_cfw_easylogger_set_filter_tag` | 107,964 | 22 | `20a788141ba9ef4a2434cbc60ed8bab16f9f78e6e04b3531752e290e0cd9fa13` |
| `open_cfw_easylogger_output_lock` | 107,988 | 36 | `e82a70b837847d145ef23c4039952e870da88e12844495cf909f55d789ec0e9a` |
| `open_cfw_easylogger_output_unlock` | 108,024 | 36 | `dad258a6c864670206666feb8aab2c980c5bd03981a9add24c6e0d10f74fe47c` |
| `open_cfw_easylogger_output_lock_enabled` | 108,060 | 50 | `420ec208e99c2fc5bdc40f3550725aea88a46feede67a74161207eefc26b80ca` |

## Installed `overlay.json` records

The installed source record is:

```json
{
  "path": "components/apollo_main/core_overlay/runtime_easylogger_control.c",
  "sha256": "4b310d835604b409dec3d404b7fcd48d28839a9b2807aef339549a7563d39bbe",
  "license": "MIT",
  "origin": "bounded Apollo-main adaptation of the authenticated EasyLogger 2.2.99-labeled control and output-lock boundary",
  "upstream": "https://github.com/armink/EasyLogger/blob/a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24/easylogger/src/elog.c",
  "upstream_commit": "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24",
  "evidence": "docs/research/easylogger-control-source-candidate.md"
}
```

The following symbols are installed in `functions`:

```json
[
  "open_cfw_easylogger_set_output_enabled",
  "open_cfw_easylogger_set_text_color_enabled",
  "open_cfw_easylogger_set_format",
  "open_cfw_easylogger_set_filter_level",
  "open_cfw_easylogger_set_filter_tag",
  "open_cfw_easylogger_output_lock",
  "open_cfw_easylogger_output_unlock",
  "open_cfw_easylogger_output_lock_enabled"
]
```

The following fail-closed patch records are installed in `patch_sites`:

```json
[
  {
    "name": "replace_easylogger_set_output_enabled",
    "runtime_address": 4444768,
    "expected_size": 110,
    "expected_sha256": "34e10d7a43f9f578deadcb826f515aff9af06d607d5e79355901c74b1ce0adea",
    "branch": "b_w",
    "target_function": "open_cfw_easylogger_set_output_enabled"
  },
  {
    "name": "replace_easylogger_set_text_color_enabled",
    "runtime_address": 4444878,
    "expected_size": 110,
    "expected_sha256": "30d6f6b942386065bbd82a097450efe06d7d50a26a71b8b12690c0a2beb3f48c",
    "branch": "b_w",
    "target_function": "open_cfw_easylogger_set_text_color_enabled"
  },
  {
    "name": "replace_easylogger_set_format",
    "runtime_address": 4444988,
    "expected_size": 106,
    "expected_sha256": "819c008ba3c645a4d711ccec7eaca6cd6b573db2f27b188ae279c23f7464ea89",
    "branch": "b_w",
    "target_function": "open_cfw_easylogger_set_format"
  },
  {
    "name": "replace_easylogger_set_filter_level",
    "runtime_address": 4445094,
    "expected_size": 96,
    "expected_sha256": "dc6524c43cb10777aa81332adc7b0e02b9f152afa4250077799308a1b951d06a",
    "branch": "b_w",
    "target_function": "open_cfw_easylogger_set_filter_level"
  },
  {
    "name": "replace_easylogger_set_filter_tag",
    "runtime_address": 4445190,
    "expected_size": 16,
    "expected_sha256": "9885baca1970ff465b03c64473ca6737d6e801c604eee63aac14eef5d0494218",
    "branch": "b_w",
    "target_function": "open_cfw_easylogger_set_filter_tag"
  },
  {
    "name": "replace_easylogger_output_lock",
    "runtime_address": 4445206,
    "expected_size": 34,
    "expected_sha256": "4d87d1bcc02e66513c6774076ff4ba4c1024c5592013439d7e8dfdf53bb483b0",
    "branch": "b_w",
    "target_function": "open_cfw_easylogger_output_lock"
  },
  {
    "name": "replace_easylogger_output_unlock",
    "runtime_address": 4445240,
    "expected_size": 34,
    "expected_sha256": "86bff518c98f24bd440f5ebe4150c5d66c0e0090e844c3af3c446ab53e4799ea",
    "branch": "b_w",
    "target_function": "open_cfw_easylogger_output_unlock"
  },
  {
    "name": "replace_easylogger_output_lock_enabled",
    "runtime_address": 4446756,
    "expected_size": 60,
    "expected_sha256": "7e1cf06caefa3b03995700b9fb4ff7c42ae51d056a36bac00dd47960147a5864",
    "branch": "b_w",
    "target_function": "open_cfw_easylogger_output_lock_enabled"
  }
]
```

No `relocations` records are needed. All retained stock calls are indirect
fixed-address seams, and the extractor resolves the local read-only-data
relocations.

## Integration limits and next audit

This increment does not claim source ownership of:

- `elog_init`, `elog_start`, or `elog_stop`;
- variadic `elog_raw_output`, `elog_output`, or `elog_hexdump`;
- tag-level mutation/query helpers;
- the G2 `elog_async_api.c` queue/event transport;
- the CMSIS mutex construction and task/time port; or
- the bootloader EasyLogger instance.

The next low-risk core increment is the private five-slot default initializer
at `[0x0043D45A,0x0043D4B0)` plus `elog_get_filter_tag_lvl` at
`[0x0043D4B0,0x0043D574)`. That increment should first source-own the
30-byte compare/memory-clear dependencies or keep them as equally explicit
stock seams. The variadic output core should wait until the G2 async
255-byte record policy and all formatting/runtime dependencies have isolated
host oracles.
