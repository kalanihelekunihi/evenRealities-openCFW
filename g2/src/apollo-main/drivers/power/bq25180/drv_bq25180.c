/* TI BQ25180 charger driver, stock D:\01_workspace\s200_ap510b_iar_git\driver\chg\drv_bq25180.c.
 * Native 0x53a670..0x53af4b; literal pool 0x53af4c..0x53afbf.
 *
 * Every register access is a one-byte transaction on product I2C bus 7,
 * 7-bit address 0x6a. Field setters are read-modify-write through
 * bq25180_update_field. Callers outside this file: 0x4c6886 ->
 * DRV_Bq25180RefreshStatus and 0x509438 -> DRV_Bq25180HwInit. */
#include <stdint.h>
#include <stddef.h>
#include "g2_hal_i2c.h"
#include "g2_bq25180.h"
#include "g2_bq27427.h"

/* Charger runtime record reached through RAM 0x200744fc; only the two status
 * images at +0x14/+0x16 are touched here. */
typedef struct {
    uint8_t unknown_00[0x14];   /* +0x00 */
    g2_bq25180_event_t event;   /* +0x14 FLAG0 image */
    uint8_t unknown_15;         /* +0x15 */
    g2_bq25180_state_t state;   /* +0x16 STAT0/STAT1 image */
} g2_charger_runtime_t;
_Static_assert(offsetof(g2_charger_runtime_t, event) == 0x14, "stock event offset");
_Static_assert(offsetof(g2_charger_runtime_t, state) == 0x16, "stock state offset");

extern g2_charger_runtime_t *g2_charger_runtime;    /* RAM 0x200744fc */
extern g2_charger_telemetry_t g2_charger_telemetry; /* RAM 0x20073b18; +0 is the cached CHG_STAT */
extern void (*audio_uart_display_fatal_handler)(const char *, const char *, uint32_t); /* RAM 0x2007456c, elog assert hook */

extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* 0x43c0e4 */
extern void audio_ble_radio_ready_44b0ae(void);
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

uint32_t bq25180_write_register(uint8_t reg, uint8_t value);
int32_t bq25180_read_register(uint8_t reg);
void bq25180_update_field(uint8_t reg, uint8_t shift, uint8_t mask, uint8_t value);
void bq25180_configure_event_mask(uint8_t events, uint8_t enabled);
void bq25180_mask_events(uint8_t events);
int32_t bq25180_read_device_id(void);
int32_t bq25180_apply_defaults(void);

/* Field positions used by the setters. */
#define ICHG_CTRL_CHG_DIS_SHIFT      7u
#define ICHG_CTRL_ICHG_MASK          0x7fu
#define CHARGECTRL0_IPRECHG_SHIFT    6u
#define CHARGECTRL0_ITERM_SHIFT      4u
#define CHARGECTRL0_VINDPM_SHIFT     2u
#define CHARGECTRL1_IBAT_OCP_SHIFT   6u
#define CHARGECTRL1_BUVLO_SHIFT      3u
#define CHARGECTRL1_CHG_STATUS_INT_MASK_SHIFT 2u
#define CHARGECTRL1_ILIM_INT_MASK_SHIFT       1u
#define CHARGECTRL1_VDPPM_INT_MASK_SHIFT      0u
#define IC_CTRL_TS_EN_SHIFT          7u
#define IC_CTRL_VLOWV_SEL_SHIFT      6u
#define IC_CTRL_SAFETY_TIMER_SHIFT   2u
#define IC_CTRL_WATCHDOG_SEL_SHIFT   0u
#define TMR_ILIM_ILIM_SHIFT          0u
#define SYS_REG_CTRL_SHIFT           5u
#define SYS_REG_SYS_MODE_SHIFT       2u
#define SYS_REG_VDPPM_DIS_SHIFT      0u
#define MASK_ID_TS_INT_MASK_SHIFT    7u
#define MASK_ID_TREG_INT_MASK_SHIFT  6u
#define MASK_ID_BAT_INT_MASK_SHIFT   5u
#define MASK_ID_PG_INT_MASK_SHIFT    4u
#define MASK_ID_DEVICE_ID_MASK       0x0fu

#define MIN_BAT_REG_mV           3500u
#define MAX_BAT_REG_mV           4650u
#define MIN_BAT_UNDERVOLTAGE_mV  2000u
#define MAX_BAT_UNDERVOLTAGE_mV  3000u
#define MIN_IN_CURR_mA           5u
#define MAX_IN_CURR_mA           1000u

static const char module_tag[] = "bp25180"; /* ROM 0x78d464 (stock spelling) */
static const char elog_tag[] = "elog"; /* ROM 0x78d45c */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\chg\\drv_bq25180.c"; /* ROM 0x70ad24 */
static const char assert_format[] = "(%s) has assert failed at %s:%ld."; /* ROM 0x7538ac */
static const char cond_not_null[] = "p != NULL"; /* ROM 0x78a8b0 */
static const char cond_bat_reg[] = "millivoltage >= MIN_BAT_REG_mV && millivoltage <= MAX_BAT_REG_mV"; /* ROM 0x7021d4 */
static const char cond_bat_uv[] = "millivoltage >= MIN_BAT_UNDERVOLTAGE_mV && millivoltage <= MAX_BAT_UNDERVOLTAGE_mV"; /* ROM 0x6e7630 */
static const char cond_in_curr[] = "milliampere >= MIN_IN_CURR_mA && milliampere <= MAX_IN_CURR_mA"; /* ROM 0x70ad64 */
static const char fn_read_event[] = "DRV_Bq25180ReadEvent"; /* ROM 0x776ab4 */
static const char fn_read_state[] = "DRV_Bq25180ReadStatet"; /* ROM 0x776acc */
static const char fn_read_device_id[] = "bq25180_read_device_id"; /* ROM 0x776ae4 */
static const char fn_set_bat_reg[] = "DRV_Bq25180SetBatteryRegulationVoltage"; /* ROM 0x749344 */
static const char fn_set_bat_uv[] = "DRV_Bq25180SetBatteryUnderVoltage_lockout"; /* ROM 0x73e0b4 */
static const char fn_set_ichg[] = "DRV_Bq25180SetFastchargeCurrent"; /* ROM 0x75f570 */
static const char fn_hw_init[] = "DRV_Bq25180HwInit"; /* ROM 0x77eec4 */
static const char id_fail[] = "[CHG] Read device id fail,Because i2c error "; /* ROM 0x733224 */
static const char id_fail_short[] = "[bp25180][CHG] Read device id fail,Because i2c error "; /* ROM 0x71dff0 */
static const char id_report[] = "[CHG]: bq25180 MASK_ID:0x%02x DEVICE_ID:0x%02x"; /* ROM 0x733254 */
static const char id_report_short[] = "[bp25180][CHG]: bq25180 MASK_ID:0x%02x DEVICE_ID:0x%02x"; /* ROM 0x71e028 */
static const char init_start[] = "\n[CHG]: bq25180 hardware init start "; /* ROM 0x74936c */
static const char init_start_short[] = "[bp25180]\n[CHG]: bq25180 hardware init start "; /* ROM 0x733284 */
static const char init_bad_id[] = "[CHG]: device id is not BQ25180 or i2c read fail: ret!"; /* ROM 0x71e060 */
static const char init_bad_id_short[] = "[bp25180][CHG]: device id is not BQ25180 or i2c read fail: ret!"; /* ROM 0x70ada4 */
static const char init_done[] = "[CHG]: BQ25180 hardware init done !"; /* ROM 0x7538d0 */
static const char init_done_short[] = "[bp25180][CHG]: BQ25180 hardware init done !"; /* ROM 0x7332b4 */

/* elog ASSERT: hand the failure to the registered hook, or log and reset
 * forever when none is registered. Execution continues after the hook. */
#define BQ_ASSERT(cond, text, fn, line)                                              \
    do {                                                                             \
        if (!(cond)) {                                                               \
            if (audio_uart_display_fatal_handler == NULL) {                          \
                audio_log_extended(0u, elog_tag, source_file, (fn), (line),          \
                                   assert_format, (text), (fn), (uint32_t)(line));   \
                for (;;)                                                             \
                    audio_ble_radio_ready_44b0ae();                                  \
            }                                                                        \
            audio_uart_display_fatal_handler((text), (fn), (line));                  \
        }                                                                            \
    } while (0)

/* Register then value as one joined write; the bus result is ignored. */
uint32_t bq25180_write_register(uint8_t reg, uint8_t value) {
    (void)hal_i2c_transfer_joined(G2_BQ25180_I2C_BUS, G2_BQ25180_I2C_ADDR, &reg, 1u, &value, 1u);
    return 0u;
}

/* The receive byte is not pre-cleared, so a failed transfer returns stack
 * contents. */
int32_t bq25180_read_register(uint8_t reg) {
    uint8_t value;
    (void)hal_i2c_transfer_full(G2_BQ25180_I2C_BUS, G2_BQ25180_I2C_ADDR, &reg, 1u, &value, 1u);
    return value;
}

/* value is shifted without first being masked. */
void bq25180_update_field(uint8_t reg, uint8_t shift, uint8_t mask, uint8_t value) {
    int32_t current = bq25180_read_register(reg);
    current = (current & ~((int32_t)mask << shift)) | ((int32_t)value << shift);
    (void)bq25180_write_register(reg, (uint8_t)current);
}

/* Event bits 0..6 map to CHARGECTRL1[2], [1], [0] and MASK_ID[7], [6], [5],
 * [4]; a mask bit of 1 suppresses the interrupt, so enabled is inverted. */
void bq25180_configure_event_mask(uint8_t events, uint8_t enabled) {
    if (events & 0x01u)
        bq25180_update_field(BQ25180_REG_CHARGECTRL1, CHARGECTRL1_CHG_STATUS_INT_MASK_SHIFT, 1u, enabled == 0u);
    if (events & 0x02u)
        bq25180_update_field(BQ25180_REG_CHARGECTRL1, CHARGECTRL1_ILIM_INT_MASK_SHIFT, 1u, enabled == 0u);
    if (events & 0x04u)
        bq25180_update_field(BQ25180_REG_CHARGECTRL1, CHARGECTRL1_VDPPM_INT_MASK_SHIFT, 1u, enabled == 0u);
    if (events & 0x08u)
        bq25180_update_field(BQ25180_REG_MASK_ID, MASK_ID_TS_INT_MASK_SHIFT, 1u, enabled == 0u);
    if (events & 0x10u)
        bq25180_update_field(BQ25180_REG_MASK_ID, MASK_ID_TREG_INT_MASK_SHIFT, 1u, enabled == 0u);
    if (events & 0x20u)
        bq25180_update_field(BQ25180_REG_MASK_ID, MASK_ID_BAT_INT_MASK_SHIFT, 1u, enabled == 0u);
    if (events & 0x40u)
        bq25180_update_field(BQ25180_REG_MASK_ID, MASK_ID_PG_INT_MASK_SHIFT, 1u, enabled == 0u);
}

void bq25180_mask_events(uint8_t events) {
    bq25180_configure_event_mask(events, 0u);
}

int32_t DRV_Bq25180ReadEvent(g2_bq25180_event_t *p) {
    BQ_ASSERT(p != NULL, cond_not_null, fn_read_event, 0x9cu);
    int32_t flag0 = bq25180_read_register(BQ25180_REG_FLAG0);
    if (flag0 < 0)
        return 0;
    audio_uart_buffer_zero(p, 1u, 0u);
    p->bat_ocp_fault = (uint8_t)flag0 & 1u;
    p->buvlo_fault = ((uint8_t)flag0 >> 1) & 1u;
    p->vin_ovp_fault = ((uint8_t)flag0 >> 2) & 1u;
    p->thermreg_active = ((uint8_t)flag0 >> 3) & 1u;
    p->vindpm_active = ((uint8_t)flag0 >> 4) & 1u;
    p->vdppm_active = ((uint8_t)flag0 >> 5) & 1u;
    p->ilim_active = ((uint8_t)flag0 >> 6) & 1u;
    p->ts_fault = ((uint8_t)flag0 >> 7) & 1u;
    return 1;
}

/* Packs STAT0/STAT1 and caches CHG_STAT (STAT0[6:5]) for the charge-state
 * consumers. */
int32_t DRV_Bq25180ReadStatet(g2_bq25180_state_t *p) {
    BQ_ASSERT(p != NULL, cond_not_null, fn_read_state, 0xbau);
    int32_t stat0 = bq25180_read_register(BQ25180_REG_STAT0);
    int32_t stat1 = bq25180_read_register(BQ25180_REG_STAT1);
    if (stat0 < 0 || stat1 < 0)
        return 0;
    audio_uart_buffer_zero(p, 2u, 0u);
    p->vin_pgood = stat0 & 1;
    p->thermreg_active = (stat0 >> 1) & 1;
    p->vindpm_active = (stat0 >> 2) & 1;
    p->vdppm_active = (stat0 >> 3) & 1;
    p->ilim_active = (stat0 >> 4) & 1;
    p->chg_stat = (stat0 >> 5) & 3;
    p->ts_open = (stat0 >> 7) & 1;
    p->wake2_flag = stat1 & 1;
    p->wake1_flag = (stat1 >> 1) & 1;
    p->safety_tmr_fault = (stat1 >> 2) & 1;
    p->ts_stat = (stat1 >> 3) & 3;
    p->buvlo = (stat1 >> 6) & 1;
    p->vin_ovp = (stat1 >> 7) & 1;
    g2_charger_telemetry.charge_status = p->chg_stat;
    return 1;
}

/* Returns MASK_ID[3:0], or -1 when the raw register reads below 1. */
int32_t bq25180_read_device_id(void) {
    int32_t mask_id = bq25180_read_register(BQ25180_REG_MASK_ID);
    if (mask_id < 1) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module_tag, source_file, fn_read_device_id, 0xe4u, id_fail);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x10000000u, id_fail_short, id_fail_short);
        return -1;
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, fn_read_device_id, 0xe8u, id_report,
                           mask_id, mask_id & MASK_ID_DEVICE_ID_MASK);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x10800000u, id_report_short, id_report_short,
                                  mask_id, mask_id & MASK_ID_DEVICE_ID_MASK);
    return mask_id & MASK_ID_DEVICE_ID_MASK;
}

/* ICHG_CTRL.CHG_DIS is active high. */
void DRV_Bq25180SetChargeEnabled(uint8_t enable) {
    bq25180_update_field(BQ25180_REG_ICHG_CTRL, ICHG_CTRL_CHG_DIS_SHIFT, 1u, enable == 0u);
}

void DRV_Bq25180SetTsEnabled(uint8_t enable) {
    bq25180_update_field(BQ25180_REG_IC_CTRL, IC_CTRL_TS_EN_SHIFT, 1u, enable);
}

void DRV_Bq25180SetSafetyTimer(uint8_t setting) {
    bq25180_update_field(BQ25180_REG_IC_CTRL, IC_CTRL_SAFETY_TIMER_SHIFT, 3u, setting);
}

void DRV_Bq25180SetWatchdog(uint8_t setting) {
    bq25180_update_field(BQ25180_REG_IC_CTRL, IC_CTRL_WATCHDOG_SEL_SHIFT, 3u, setting);
}

/* Whole-register write of VBATREG = (mV - 3500) / 10 (bit 7 cleared). */
void DRV_Bq25180SetBatteryRegulationVoltage(uint16_t millivoltage) {
    BQ_ASSERT(millivoltage >= MIN_BAT_REG_mV && millivoltage <= MAX_BAT_REG_mV,
              cond_bat_reg, fn_set_bat_reg, 0x106u);
    (void)bq25180_write_register(BQ25180_REG_VBAT_CTRL,
                                 (uint8_t)((millivoltage - MIN_BAT_REG_mV) / 10u));
}

void DRV_Bq25180SetBatteryOvercurrent(uint8_t setting) {
    bq25180_update_field(BQ25180_REG_CHARGECTRL1, CHARGECTRL1_IBAT_OCP_SHIFT, 3u, setting);
}

/* BUVLO codes 2..7 = 3.0/2.8/2.6/2.4/2.2/2.0 V. */
void DRV_Bq25180SetBatteryUnderVoltage_lockout(uint16_t millivoltage) {
    uint8_t code;
    BQ_ASSERT(millivoltage >= MIN_BAT_UNDERVOLTAGE_mV && millivoltage <= MAX_BAT_UNDERVOLTAGE_mV,
              cond_bat_uv, fn_set_bat_uv, 0x117u);
    if (millivoltage >= 2801)
        code = 2u;
    else if (millivoltage >= 2601)
        code = 3u;
    else if (millivoltage >= 2401)
        code = 4u;
    else if (millivoltage >= 2201)
        code = 5u;
    else if (millivoltage >= 2001)
        code = 6u;
    else
        code = 7u;
    bq25180_update_field(BQ25180_REG_CHARGECTRL1, CHARGECTRL1_BUVLO_SHIFT, 7u, code);
}

/* VLOWV_SEL: 1 = 2.8 V, 0 = 3.0 V. */
void DRV_Bq25180SetPrechargeThreshold(uint16_t millivoltage) {
    uint8_t sel = 0u;
    if (millivoltage < 2801)
        sel = 1u;
    bq25180_update_field(BQ25180_REG_IC_CTRL, IC_CTRL_VLOWV_SEL_SHIFT, 1u, sel);
}

/* IPRECHG: 0 = 2 x ITERM, 1 = 1 x ITERM. */
void DRV_Bq25180SetPrechargeRatio(uint8_t ratio) {
    bq25180_update_field(BQ25180_REG_CHARGECTRL0, CHARGECTRL0_IPRECHG_SHIFT, 1u, ratio < 2);
}

/* 5..35 mA -> code mA - 5; above that mA / 10 + 27 saturated at 0x7f. */
void DRV_Bq25180SetFastchargeCurrent(uint16_t milliampere) {
    uint8_t code;
    BQ_ASSERT(milliampere >= MIN_IN_CURR_mA && milliampere <= MAX_IN_CURR_mA,
              cond_in_curr, fn_set_ichg, 0x143u);
    code = (uint8_t)(milliampere - 5);
    if (milliampere >= 36) {
        if ((uint8_t)(milliampere / 10 + 27) >= 128)
            code = 0x7fu;
        else
            code = (uint8_t)(milliampere / 10 + 27);
    }
    bq25180_update_field(BQ25180_REG_ICHG_CTRL, 0u, ICHG_CTRL_ICHG_MASK, code);
}

/* ITERM: 0 disabled, 1 = 5 %, 2 = 10 %, 3 = 20 %. */
void DRV_Bq25180SetTerminationPercent(uint8_t percent) {
    uint8_t code = 0u;
    if (percent >= 20)
        code = 3u;
    else if (percent >= 10)
        code = 2u;
    else if (percent >= 5)
        code = 1u;
    bq25180_update_field(BQ25180_REG_CHARGECTRL0, CHARGECTRL0_ITERM_SHIFT, 3u, code);
}

void DRV_Bq25180SetVindpm(uint8_t setting) {
    bq25180_update_field(BQ25180_REG_CHARGECTRL0, CHARGECTRL0_VINDPM_SHIFT, 3u, setting);
}

/* SYS_REG.VDPPM_DIS is active high. */
void DRV_Bq25180SetVdppmEnabled(uint8_t enable) {
    bq25180_update_field(BQ25180_REG_SYS_REG, SYS_REG_VDPPM_DIS_SHIFT, 1u, enable == 0u);
}

/* ILIM codes 0..7 = 50/100/200/300/400/500/700/1100 mA, rounded down. */
void DRV_Bq25180SetInputCurrentLimit(uint16_t milliampere) {
    uint8_t code = 0u;
    if (milliampere >= 1100)
        code = 7u;
    else if (milliampere >= 700)
        code = 6u;
    else if (milliampere >= 500)
        code = 5u;
    else if (milliampere >= 400)
        code = 4u;
    else if (milliampere >= 300)
        code = 3u;
    else if (milliampere >= 200)
        code = 2u;
    else if (milliampere >= 100)
        code = 1u;
    bq25180_update_field(BQ25180_REG_TMR_ILIM, TMR_ILIM_ILIM_SHIFT, 7u, code);
}

void DRV_Bq25180SetSystemMode(uint8_t setting) {
    bq25180_update_field(BQ25180_REG_SYS_REG, SYS_REG_SYS_MODE_SHIFT, 3u, setting);
}

void DRV_Bq25180SetSystemVoltage(uint8_t setting) {
    bq25180_update_field(BQ25180_REG_SYS_REG, SYS_REG_CTRL_SHIFT, 7u, setting);
}

/* Separate stock body with the same effect as DRV_Bq25180SetTsEnabled. */
void DRV_Bq25180SetTsAutoEnabled(uint8_t enable) {
    bq25180_update_field(BQ25180_REG_IC_CTRL, IC_CTRL_TS_EN_SHIFT, 1u, enable);
}

/* Charging is held off while the defaults are programmed. */
int32_t bq25180_apply_defaults(void) {
    DRV_Bq25180SetChargeEnabled(0u);
    DRV_Bq25180SetTsEnabled(0u);
    DRV_Bq25180SetFastchargeCurrent(91u);
    DRV_Bq25180SetInputCurrentLimit(1000u);
    DRV_Bq25180SetPrechargeRatio(2u);
    DRV_Bq25180SetTerminationPercent(10u);
    DRV_Bq25180SetBatteryOvercurrent(0u);
    DRV_Bq25180SetSystemVoltage(1u);
    DRV_Bq25180SetBatteryRegulationVoltage(4400u);
    DRV_Bq25180SetVindpm(1u);
    DRV_Bq25180SetBatteryUnderVoltage_lockout(2800u);
    DRV_Bq25180SetPrechargeThreshold(2800u);
    DRV_Bq25180SetSystemMode(0u);
    DRV_Bq25180SetVdppmEnabled(0u);
    DRV_Bq25180SetSafetyTimer(1u);
    DRV_Bq25180SetWatchdog(0u);
    DRV_Bq25180SetTsAutoEnabled(0u);
    bq25180_mask_events(0x7fu);
    DRV_Bq25180SetChargeEnabled(1u);
    return 0;
}

int32_t DRV_Bq25180RefreshStatus(void) {
    (void)DRV_Bq25180ReadEvent(&g2_charger_runtime->event);
    (void)DRV_Bq25180ReadStatet(&g2_charger_runtime->state);
    return 0;
}

int32_t DRV_Bq25180HwInit(void) {
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, fn_hw_init, 0x1e4u, init_start);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x10000000u, init_start_short, init_start_short);
    int32_t id = bq25180_read_device_id();
    if (id != (int32_t)BQ25180_DEVICE_ID) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module_tag, source_file, fn_hw_init, 0x1e9u, init_bad_id, id);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x10400000u, init_bad_id_short, init_bad_id_short, id);
        return -1;
    }
    (void)bq25180_apply_defaults();
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, fn_hw_init, 0x1efu, init_done);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x10000000u, init_done_short, init_done_short);
    return 0;
}
