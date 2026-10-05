# Transport pad routing prerequisite

Reconstructed dispatcher0x4c2e30, directly called by radio transport release0x52df12 before HAL disable/power/uninitialize. See [pseudocode and provider boundary](../../../analysis/radio-transport-pads-2026-10-05/pseudocode.md).

Build: `make -C g2 radio-transport-pads-simulator`. Run verify.py with `--elf g2/build/foundation/radio-transport-pads-simulator/transport_pads.elf --output <fresh-result-path>`. Links unchanged pinned Ambiq GPIO source and actual PRIMASK provider; notices/licenses remain in those providers. Volatile configuration word78ee48 is authenticated non-executable data.

No full transport-release, buffer-drain, NVIC or hardware shutdown proof.
