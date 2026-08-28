# G2 touch CAT2 source admission: Flash, GPIO, and SCB-I2C

This second isolated Apache-2.0 batch admits nine additional CAT2 functions
against `mtb-pdl-cat2` commit
`35f1714623cfea682d5e285af80d50416b4c7bbc`.

Seven contiguous functions match `cy_flash.c` source order and register/caller
topology:

| Entry | Symbol |
|---:|---|
| `0x58f4` | `ProcessStatusCode` |
| `0x5974` | `Cy_Flash_ValidAddr` |
| `0x59a8` | `Cy_Flash_GetRowNum` |
| `0x59c4` | `Cy_Flash_ClockBackup` |
| `0x5a00` | `Cy_Flash_ClockConfig` |
| `0x5a20` | `Cy_Flash_ClockRestore` |
| `0x5a50` | `Cy_Flash_WriteRow` |

Evidence includes the CPUSS SYSARG/SYSREQ SROM register family, the shipped
20-entry status switch table, the public helper order, and the write-row call
graph over validation, row calculation, clock backup/config/restore, copy, and
critical-section operations.

Two further exact public entries are admitted:

- `0x5be4` is `Cy_GPIO_Pin_Init`, reached by six pin-configuration call sites
  and invoking the ordered write/drive/HSIOM/edge/vtrip/slew helper sequence.
- `0x680c` is `Cy_SCB_I2C_SlaveInterrupt`, reached from the touch slave ISR and
  branching across the receive, address, transmit, stop, and acknowledgement
  helper topology.

The Apache adapter exposes fail-closed Flash-write, GPIO-init, and slave-I2C
interrupt provider routes. Host tests do not execute MMIO, SROM calls, or
interrupt hardware. The adapter also passes a freestanding Cortex-M0+ build.

The CAT2 gap falls from 45 to 36 and the overall semantic/source gap from 210
to 201. Mixed CAPSENSE/CAT2, Em_EEPROM EULA, application/startup, and
system/DFU rows remain unchanged and non-concrete.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 g2/tools/analyze_g2_touch_cat2_source_admission2.py --write-manifests --json
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest g2.tests.test_analyze_g2_touch_cat2_source_admission2
```
