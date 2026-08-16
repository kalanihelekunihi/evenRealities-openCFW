#ifndef OPENR1_POWER_ZEPHYR_H
#define OPENR1_POWER_ZEPHYR_H

#include <stdbool.h>

/* Binds the stock BLE-startup REG1 enable action to the nRF52840 POWER
 * peripheral. This controls the main DC/DC converter; it is not a CPU clock
 * control or a measurement of physical regulator state. */
int openr1_power_zephyr_initialize(void);

/* Applies the normalized system-settings type-zero action. The glasses-wear
 * automatic policy remains unbound until its typed wear/power lifecycle is
 * available. */
int openr1_power_zephyr_set_reg1(bool enabled);
int openr1_power_zephyr_get_reg1(bool *enabled);

#endif
