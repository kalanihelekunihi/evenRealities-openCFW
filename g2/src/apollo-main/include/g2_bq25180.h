/* TI BQ25180 1-cell linear charger driver (stock driver\chg\drv_bq25180.c,
 * native 0x53a670..0x53af4b, literal pool 0x53af4c..0x53afbf).
 *
 * The charger sits on product I2C bus 7 at 7-bit address 0x6a. Register and
 * field names follow the TI datasheet register map; the values are the ones
 * the stock code programs. */
#ifndef G2_BQ25180_H
#define G2_BQ25180_H

#include <stdint.h>

#define G2_BQ25180_I2C_BUS  7u
#define G2_BQ25180_I2C_ADDR 0x6au

/* Register map (datasheet 0x00..0x0c). */
#define BQ25180_REG_STAT0       0x00u
#define BQ25180_REG_STAT1       0x01u
#define BQ25180_REG_FLAG0       0x02u
#define BQ25180_REG_VBAT_CTRL   0x03u /* [6:0] VBATREG = 3500 mV + 10 mV * code */
#define BQ25180_REG_ICHG_CTRL   0x04u /* [7] CHG_DIS, [6:0] ICHG */
#define BQ25180_REG_CHARGECTRL0 0x05u /* [6] IPRECHG, [5:4] ITERM, [3:2] VINDPM, [1:0] THERM_REG */
#define BQ25180_REG_CHARGECTRL1 0x06u /* [7:6] IBAT_OCP, [5:3] BUVLO, [2:0] interrupt masks */
#define BQ25180_REG_IC_CTRL     0x07u /* [7] TS_EN, [6] VLOWV_SEL, [5] VRCH, [4] 2XTMR_EN, [3:2] SAFETY_TIMER, [1:0] WATCHDOG_SEL */
#define BQ25180_REG_TMR_ILIM    0x08u /* [7:6] MR_LPRESS, [5] MR_RESET_VIN, [4:3] AUTOWAKE, [2:0] ILIM */
#define BQ25180_REG_SHIP_RST    0x09u
#define BQ25180_REG_SYS_REG     0x0au /* [7:5] SYS_REG_CTRL, [3:2] SYS_MODE, [1] WATCHDOG_15S_EN, [0] VDPPM_DIS */
#define BQ25180_REG_TS_CONTROL  0x0bu
#define BQ25180_REG_MASK_ID     0x0cu /* [7:4] TS/TREG/BAT/PG interrupt masks, [3:0] DEVICE_ID */

#define BQ25180_DEVICE_ID 0x0u /* MASK_ID[3:0] */

/* FLAG0 copied bit-for-bit (DRV_Bq25180ReadEvent). */
typedef struct {
    uint8_t bat_ocp_fault : 1;   /* bit 0 */
    uint8_t buvlo_fault : 1;     /* bit 1 */
    uint8_t vin_ovp_fault : 1;   /* bit 2 */
    uint8_t thermreg_active : 1; /* bit 3 */
    uint8_t vindpm_active : 1;   /* bit 4 */
    uint8_t vdppm_active : 1;    /* bit 5 */
    uint8_t ilim_active : 1;     /* bit 6 */
    uint8_t ts_fault : 1;        /* bit 7 */
} g2_bq25180_event_t;
_Static_assert(sizeof(g2_bq25180_event_t) == 1, "FLAG0 image is one byte");

/* STAT0 in the low byte, STAT1 in the high byte (DRV_Bq25180ReadStatet).
 * STAT1 bit 5 (reserved) is dropped and bit 15 stays zero. */
typedef struct {
    uint16_t vin_pgood : 1;        /* bit 0  STAT0[0] */
    uint16_t thermreg_active : 1;  /* bit 1  STAT0[1] */
    uint16_t vindpm_active : 1;    /* bit 2  STAT0[2] */
    uint16_t vdppm_active : 1;     /* bit 3  STAT0[3] */
    uint16_t ilim_active : 1;      /* bit 4  STAT0[4] */
    uint16_t chg_stat : 2;         /* bits 5-6 STAT0[6:5]: 0 not charging, 1 CC, 2 CV, 3 done */
    uint16_t ts_open : 1;          /* bit 7  STAT0[7] */
    uint16_t wake2_flag : 1;       /* bit 8  STAT1[0] */
    uint16_t wake1_flag : 1;       /* bit 9  STAT1[1] */
    uint16_t safety_tmr_fault : 1; /* bit 10 STAT1[2] */
    uint16_t ts_stat : 2;          /* bits 11-12 STAT1[4:3] */
    uint16_t buvlo : 1;            /* bit 13 STAT1[6] */
    uint16_t vin_ovp : 1;          /* bit 14 STAT1[7] */
    uint16_t reserved : 1;         /* bit 15 */
} g2_bq25180_state_t;
_Static_assert(sizeof(g2_bq25180_state_t) == 2, "STAT0/STAT1 image is two bytes");

int32_t DRV_Bq25180ReadEvent(g2_bq25180_event_t *p);
int32_t DRV_Bq25180ReadStatet(g2_bq25180_state_t *p);
void DRV_Bq25180SetChargeEnabled(uint8_t enable);
void DRV_Bq25180SetTsEnabled(uint8_t enable);
void DRV_Bq25180SetSafetyTimer(uint8_t setting);
void DRV_Bq25180SetWatchdog(uint8_t setting);
void DRV_Bq25180SetBatteryRegulationVoltage(uint16_t millivoltage);
void DRV_Bq25180SetBatteryOvercurrent(uint8_t setting);
void DRV_Bq25180SetBatteryUnderVoltage_lockout(uint16_t millivoltage);
void DRV_Bq25180SetPrechargeThreshold(uint16_t millivoltage);
void DRV_Bq25180SetPrechargeRatio(uint8_t ratio);
void DRV_Bq25180SetFastchargeCurrent(uint16_t milliampere);
void DRV_Bq25180SetTerminationPercent(uint8_t percent);
void DRV_Bq25180SetVindpm(uint8_t setting);
void DRV_Bq25180SetVdppmEnabled(uint8_t enable);
void DRV_Bq25180SetInputCurrentLimit(uint16_t milliampere);
void DRV_Bq25180SetSystemMode(uint8_t setting);
void DRV_Bq25180SetSystemVoltage(uint8_t setting);
void DRV_Bq25180SetTsAutoEnabled(uint8_t enable);
int32_t DRV_Bq25180RefreshStatus(void);
int32_t DRV_Bq25180HwInit(void);

#endif
