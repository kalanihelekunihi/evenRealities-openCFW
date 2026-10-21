/* SPDX-License-Identifier: MIT
 * Source strings authenticated against locked ota_s200_bootloader.bin SHA-256
 * f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5.
 */
#include "startup_diagnostics.h"
/* Stock 0x43406c. */
const char opencfw_boot_elog_module[] = "elog";
/* Stock 0x430ec0. */
const char opencfw_boot_elog_source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\EasyLogger-master\\easylogger\\src\\elog.c";
/* Stock 0x433f38. */
const char opencfw_boot_elog_start_function[] = "elog_start";
/* Stock 0x432ac4. */
const char opencfw_boot_elog_started_format[] = "EasyLogger V%s is initialize success.";
/* Stock 0x434074. */
const char opencfw_boot_elog_version[] = "2.2.99";
/* Stock 0x433fd4. */
const char opencfw_boot_redirect_module[] = "redirect";
/* Stock 0x431258. */
const char opencfw_boot_redirect_source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\product\\s200\\bootloader\\config\\redirect.c";
/* Stock 0x433e68. */
const char opencfw_boot_redirect_init_function[] = "redirect_init";
/* Stock 0x432808. */
const char opencfw_boot_redirect_mutex_failed[] = "Failed to create redirect mutex for IAR.";
/* Stock 0x432bdc. */
const char opencfw_boot_redirect_mutex_ready[] = "redirect init with mutex protection.";
/* Stock 0x431ea4. */
const char opencfw_boot_adc_reservation_failed[] = "Error - reservation of the ADC instance failed.\n";
/* Stock 0x4325f8. */
const char opencfw_boot_adc_correction_format[] = "ADC correction offset = %.6f, gain = %.6f\n";
/* Stock 0x433140. */
const char opencfw_boot_adc_power_failed[] = "Error - ADC power on failed.\n";
/* Stock 0x432c7c. */
const char opencfw_boot_adc_config_failed[] = "Error - configuring ADC failed.\n";
/* Stock 0x4329d4. */
const char opencfw_boot_adc_slot_failed[] = "Error - configuring ADC Slot failed.\n";
/* Stock 0x433160. */
const char opencfw_boot_adc_enable_failed[] = "Error - enabling ADC failed.\n";
/* Stock 0x431ab8. */
const char opencfw_boot_adc_sample_format[] = "HwConfig ADC sample read=%d, measured voltage=%.5f mV\n";
/* Stock 0x4340a4. */
const char opencfw_boot_i2c_module[] = "hal.i2c";
/* Stock 0x43164c. */
const char opencfw_boot_i2c_source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\hal\\src\\hal_i2c.c";
/* Stock 0x433f74. */
const char opencfw_boot_i2c_init_function[] = "HAL_I2CInit";
/* Stock 0x4322c8. */
const char opencfw_boot_i2c_semaphore_failed[] = "Error - Failed to create semaphore for I2C4.";
