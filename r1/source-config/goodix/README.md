# R1 Goodix source configuration

`gh_demo_config.h` restores the exact overlay from commit `832137ec`, formerly
`r1/port/goodix_gh3x2x/config/gh_demo_config.h`. It chains to the pinned public
header and selects `__DRIVER_OPEN_ALL_SOURCE__=1` for the driver units, matching
the recovered FIFO driver bodies. Kernel units still include their sibling
vendor header. Other vendor defaults remain candidates rather than stock facts.

`make -C r1 goodix-candidate` compiles 16 units from the pinned public C tree:
the historical 15 driver/demo/module/configuration units plus the public
`gh3x2x_demo_algo_config.c` source. The latter is supported by exact per-function
attributions at `0x29F88`, `0x2A630`, `0x2ACF4`, `0x2AEDC` and other entries in
`GOODIX-DEMO-DRIVER-MAPPING-2026-08.md`. The historical clean-room build excluded
the algorithm-call/configuration layer as a group. The current whole-image
reconstruction instead compiles this attributable configuration source while
retaining explicit unresolved algorithm dependencies. Its vendor-default
branch selection and channel-map ABI are not automatically admitted as stock.
No private algorithm body, archive implementation or PC-tool protocol source
is supplied as a substitute. Remaining runtime, algorithm, upload-protocol and
R1 HAL references are listed in the report and are not stubbed.

## Stock calibration delta

The public 36-byte HR and 24-byte HRV configuration objects match stock exactly.
The public 76-byte SpO2 object has the same version tag and layout but different
calibration coefficients. A version tag therefore does not establish complete
data identity. The authenticated application at `0xAD160..<0xAD1AC` requires:

| Field | Byte offset | Public value | Stock value |
|---|---:|---:|---:|
| `cali_coef_a2` | 16 | -124026 | -156022 |
| `cali_coef_a1` | 20 | -59505 | -42041 |
| `cali_coef_a0` | 24 | 1043941 | 1066184 |

The build verifies the complete application and configuration-region hashes,
then applies those three typed constant changes to a generated source copy.
Static assertions check the public structure size and field offsets. The
upstream file remains unchanged. The reviewable delta is
`r1/patches/goodix/stock-spo2-calibration.patch`; it includes the layout assertions.
The generated version timestamp is deterministic and explicitly candidate-only.

`make -C r1 goodix-config-oracle` (Python with Unicorn) compares all 136 compiled
configuration bytes to stock, recompiles the original public SpO2 source to
verify the three-field delta, and runs six pointer/size getters from a linked
ARM configuration-only ELF. Receipts are under
`r1/research/source-build/goodix/`. These checks establish data identity and
those getter results, not algorithm output, physical calibration suitability,
stock instruction identity or a complete firmware link.
