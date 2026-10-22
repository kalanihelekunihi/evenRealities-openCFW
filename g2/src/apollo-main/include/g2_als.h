/* Ambient-light-sensor driver (stock D:\01_workspace\s200_ap510b_iar_git\driver\sensor\als\als.c,
 * log tag "sensor_als"), native 0x4ad9b8..0x4ae94c.
 *
 * Sensor: TI OPT3007 on product I2C bus 2, 7-bit address 0x45 (register
 * accessors 0x513748/0x513780). Manufacturer ID register 0x7E must read 0x5449
 * ("TI") and device ID register 0x7F must read 0x3001. Init sets M = 3
 * (continuous conversions) and CT = 0 (100 ms); RN keeps its reset value.
 *
 * Units: a raw reading is mantissa << exponent (0.01 lux per LSB by the
 * datasheet). DRV_ALSReadData divides by 10 without a production calibration,
 * else multiplies by the calibration word and divides by 1,000,000, so the
 * driver value is in 0.1 lux steps scaled by calibration / 100000.
 *
 * The stock placeholder names als_function_NN are the qualify anchors; the
 * comment on each prototype states the real role (stock name when a log
 * string gives it). */
#ifndef G2_ALS_H
#define G2_ALS_H

#include <stdbool.h>
#include <stdint.h>

#define G2_ALS_I2C_BUS 2u
#define G2_ALS_I2C_ADDR 0x45u
#define G2_ALS_OPT3007_MANUFACTURER_ID 0x5449u
#define G2_ALS_OPT3007_DEVICE_ID 0x3001u
#define G2_ALS_SYNC_MESSAGE 0x10eu /* handled by ALSSyncHandler 0x4ae73c */

/* Timer-handler state machine, RAM 0x200741c4. */
enum {
    G2_ALS_STATUS_CLOSED = 0u,
    G2_ALS_STATUS_START = 1u,   /* first read, 110 ms after open */
    G2_ALS_STATUS_ADJUST = 2u,  /* ramp brightness toward target, 200 ms */
    G2_ALS_STATUS_POLLING = 3u, /* steady sampling, 1000 ms */
};

/* One bit field of an OPT3007 register: {msb, lsb, register}. */
typedef struct {
    uint8_t msb; /* +0 */
    uint8_t lsb; /* +1 */
    uint8_t reg; /* +2 */
} g2_opt3007_field_t;
_Static_assert(sizeof(g2_opt3007_field_t) == 3, "stock field triple");

/* Register map filled by ti_opt3007_assignRegistermap 0x5135e0. */
typedef struct {
    g2_opt3007_field_t result_mantissa;  /* +0x00 R[11:0], reg 0x00 */
    g2_opt3007_field_t result_exponent;  /* +0x03 E[15:12], reg 0x00 */
    g2_opt3007_field_t range_number;     /* +0x06 RN[15:12], reg 0x01 */
    g2_opt3007_field_t conversion_time;  /* +0x09 CT[11], reg 0x01 */
    g2_opt3007_field_t mode;             /* +0x0c M[10:9], reg 0x01 */
    g2_opt3007_field_t overflow;         /* +0x0f OVF[8] */
    g2_opt3007_field_t conversion_ready; /* +0x12 CRF[7] */
    g2_opt3007_field_t flag_high;        /* +0x15 FH[6] */
    g2_opt3007_field_t flag_low;         /* +0x18 FL[5] */
    g2_opt3007_field_t latch;            /* +0x1b L[4] */
    g2_opt3007_field_t polarity;         /* +0x1e POL[3] */
    g2_opt3007_field_t mask_exponent;    /* +0x21 ME[2] */
    g2_opt3007_field_t fault_count;      /* +0x24 FC[1:0] */
    g2_opt3007_field_t low_exponent;     /* +0x27 reg 0x02 [15:12] */
    g2_opt3007_field_t low_mantissa;     /* +0x2a reg 0x02 [11:0] */
    g2_opt3007_field_t high_exponent;    /* +0x2d reg 0x03 [15:12] */
    g2_opt3007_field_t high_mantissa;    /* +0x30 reg 0x03 [11:0] */
    g2_opt3007_field_t manufacturer_id;  /* +0x33 reg 0x7e [15:0] */
    g2_opt3007_field_t device_id;        /* +0x36 reg 0x7f [15:0] */
} g2_opt3007_regmap_t;
_Static_assert(sizeof(g2_opt3007_regmap_t) == 0x39, "stock register map");

/* Brightness curve row of ROM table 0x730e24: lux threshold -> percent. */
typedef struct {
    uint32_t threshold; /* +0 */
    uint32_t percent;   /* +4 */
} g2_als_curve_step_t;
#define G2_ALS_CURVE_STEPS 6u
extern const g2_als_curve_step_t g2_als_curve_table[G2_ALS_CURVE_STEPS]; /* ROM 0x730e24 */

/* ALS state cells owned by existing units (names kept for unification). */
extern uint32_t audio_als_scale_clamped;       /* RAM 0x20000060 learned scale reset value */
extern uint32_t audio_als_scale_active;        /* RAM 0x20000064 curve scale, Q10 */
extern uint32_t audio_als_scale_shadow;        /* RAM 0x20000068 */
extern uint32_t audio_als_manual_ready;        /* RAM 0x200741c0 driver opened */
extern uint32_t audio_als_manual_sample;       /* RAM 0x200741c8 peak window index */
extern uint32_t audio_als_manual_accumulator;  /* RAM 0x200741cc peak window count */
extern uint8_t audio_als_manual_window[20];    /* RAM 0x20073c98 peak window, 5 words */
extern uint32_t audio_als_default_previous;    /* RAM 0x200741dc last accepted reading */
extern uint32_t audio_als_active_previous;     /* RAM 0x200741e0 filtered (peak) reading */
extern uint32_t audio_als_curve_index;         /* RAM 0x200741e4 */
extern uint32_t audio_als_curve_nominal;       /* RAM 0x200741e8 unscaled curve percent */
extern uint32_t audio_als_curve_adjusted;      /* RAM 0x200741ec target brightness */
extern uint32_t audio_als_manual_level;        /* RAM 0x200741f0 current brightness */
extern uint32_t audio_als_manual_level_copy;   /* RAM 0x200741f4 */
extern uint32_t audio_als_manual_pending;      /* RAM 0x200741f8 last notify_app flag */
extern uint32_t audio_als_manual_target_count; /* RAM 0x200741fc */
extern uint32_t audio_als_recompute_pending;   /* RAM 0x20074200 */

/* ALS state cells owned by als-driver/als_driver_state.c. */
extern uint32_t g2_als_process_status;      /* RAM 0x200741c4 */
extern uint32_t g2_als_dark_window_index;   /* RAM 0x200741d0 */
extern uint32_t g2_als_dark_window_count;   /* RAM 0x200741d4 */
extern uint32_t g2_als_dark_window[20];     /* RAM 0x20072948 */
extern uint32_t g2_als_extreme_dark_active; /* RAM 0x200741d8 */
extern g2_opt3007_regmap_t g2_als_opt3007_regmap; /* RAM 0x20073134 */

/* Existing ALS units called by this driver. */
uint32_t audio_als_first_curve_percent_4ad9e2(void); /* 0x4ad9e2 */
void audio_als_manual_recalculate_4adcd8(void);      /* 0x4adcd8 reset peak window */
void audio_als_apply_previous(uint32_t lux);         /* 0x4add8c recompute target */

void als_function_01(uint8_t level, uint8_t notify_app); /* ALS sync send, 0x4ad9b8 */
uint32_t als_function_03(uint32_t percent);   /* clamp to [first curve %, 100], 0x4ad9ea */
void als_function_04(uint32_t lux);           /* push 5-sample peak window, 0x4ada02 */
void als_function_05(uint32_t lux);           /* push 20-sample dark window, 0x4ada30 */
void als_function_06(void);                   /* reset dark window, 0x4ada5e */
bool als_function_07(void);                   /* dark window says extreme dark, 0x4ada80 */
uint32_t als_function_08(uint32_t lux);       /* DRV_ALSFilterValueByPitch, 0x4adab8 */
uint32_t als_function_09(void);               /* newest peak-window sample, 0x4adb50 */
uint32_t als_function_10(void);               /* peak-window maximum, 0x4adb60 */
void als_function_11(uint32_t lux);           /* DRV_ALSUpdateTargetWithExtremeDarkMode, 0x4adb9a */
bool als_function_12(void);                   /* peak-window spread > 300, 0x4adc84 */
uint32_t als_function_14(uint32_t lux);       /* curve index for reading, 0x4add02 */
uint32_t als_function_15(uint32_t index);     /* curve percent at index, 0x4add24 */
uint32_t als_function_16(uint32_t lux);       /* curve percent for reading, 0x4add30 */
uint32_t als_function_17(uint32_t percent, uint32_t scale_q10); /* scaled percent, 0x4add3c */
uint32_t als_function_18(uint32_t index);     /* scaled target at index, 0x4add6a */
void als_function_22(void);                   /* reset learned scale, 0x4adec4 */
void als_function_23(uint32_t level, uint8_t notify_app); /* set + sync brightness, 0x4adf04 */
bool als_function_24(void);                   /* use the slow ramp step, 0x4adf34 */
int32_t als_function_25(void);                /* DRV_ALSInit, 0x4adf74 */
void als_function_26(void);                   /* sensor power off, 0x4ae076 */
uint32_t als_function_27(void);               /* DRV_ALSReadData, 0x4ae082 */
int32_t als_function_28(void);                /* DRV_ALSOpen, 0x4ae10a */
int32_t als_function_29(void);                /* DRV_ALSClose, 0x4ae218 */
uint32_t als_function_30(uint32_t target, uint32_t current, uint32_t step); /* ramp, 0x4ae282 */
void als_function_31(void);                   /* DRV_ALSTimerHandlerStart, 0x4ae2b6 */
void als_function_32(void);                   /* DRV_ALSTimerHandlerAdjust, 0x4ae3c8 */
void als_function_33(void);                   /* DRV_ALSTimerHandlerPolling, 0x4ae4f8 */
void als_function_34(void);                   /* DRV_ALSTimerHandler, 0x4ae6d0 */

#endif
