/* SPDX-License-Identifier: MIT
 * Named stock product inputs to the recovered Apollo startup consumers.
 * Locked input: ota_s200_bootloader.bin SHA-256 f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5.
 * Values are authenticated at 0x434024 (five shared-memory fields),
 * 0x434154 (conditional power register value), and 0x434160 (sleep fields).
 * They are configuration data, not executable bytes or inferred defaults.
 */
#include <stdint.h>

const uint8_t opencfw_boot_shared_memory_profile[5] = {7u, 0u, 0u, 0u, 7u};
const uint32_t opencfw_boot_conditional_power_value = 3u;
const uint32_t opencfw_boot_sleep_fields_initial = 0u;
/* Stock 0x43402c and 0x434170/174: ADC descriptor and power-mode inputs. */
const uint32_t opencfw_boot_adc_descriptor[2] = {0x401u, 0x1eu};
const uint32_t opencfw_boot_adc_power_initial = 0u;
const uint32_t opencfw_boot_adc_power_final = 3u;
/* Stock 0x43419c: post-bringup special register value. */
const uint32_t opencfw_boot_post_special_register_value = 3u;
/* Stock 0x434164/168: two SPOT state decoder configuration words. */
const uint32_t opencfw_boot_spot_config_values[2] = {0u, 0u};
