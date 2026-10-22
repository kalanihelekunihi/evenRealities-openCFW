/* TI BQ27427 fuel gauge (stock driver/chg/drv_bq27427.c, native 0x53afc0..0x53c1c3).
 *
 * The gauge sits on product I2C bus 7 at 7-bit address 0x55 and is only used
 * on charger family 2 boards (board-config byte == 2), next to the BQ25180.
 * Callers outside the driver: 0x5093d4 (board power init) -> DRV_Bq27427HwInit
 * and 0x4c6810 (device manager poll) -> bq27427_init_wrapper. */
#ifndef G2_BQ27427_H
#define G2_BQ27427_H

#include <stdint.h>

/* Charger telemetry record at RAM 0x20073b18 shared with the charger drivers.
 * Word +0 is written by the BQ25180 driver (see drv_bq25180.c); the gauge
 * refresh writes +4..+0x10. */
typedef struct {
    uint32_t charge_status;  /* +0x00 BQ25180 CHG_STAT */
    int32_t soc;             /* +0x04 StateOfCharge(), % */
    int32_t voltage_mv;      /* +0x08 Voltage(), mV */
    int32_t avg_current_ma;  /* +0x0c AverageCurrent(), signed mA */
    int32_t temperature;     /* +0x10 (Temperature() - 2731) * 10 */
} g2_charger_telemetry_t;

int32_t bq27427_status_update(void);
int32_t bq27427_init_wrapper(void);
int32_t DRV_Bq27427HwInit(void);

#endif
