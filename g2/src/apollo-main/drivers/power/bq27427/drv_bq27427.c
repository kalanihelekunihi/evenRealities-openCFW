/* TI BQ27427 fuel-gauge driver, stock D:\01_workspace\s200_ap510b_iar_git\driver\chg\drv_bq27427.c.
 * Native 0x53afc0..0x53c1c3. Literal pools 0x53bb6c..0x53bb8b, 0x53bcdc..0x53bd0b,
 * 0x53be8c..0x53beb3, 0x53c018..0x53c023, 0x53c0d4..0x53c0f3, 0x53c1c4..0x53c2a3
 * (the gaps between functions hold only pools and two-byte pads, no helpers).
 *
 * Every access goes to product I2C bus 7, 7-bit address 0x55. Standard
 * commands are two-byte little-endian register pairs; Control() subcommands
 * are two-byte writes to register 0x00. Data memory is accessed one 32-byte
 * block at a time through DataClass() 0x3e, DataBlock() 0x3f, BlockData()
 * 0x40..0x5f, BlockDataCheckSum() 0x60 and BlockDataControl() 0x61; data
 * memory values are big-endian. The message texts follow the Zephyr bq274xx
 * driver, but the control flow is the vendor's own. */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include "g2_hal_i2c.h"
#include "g2_bq27427.h"

#define BQ27427_I2C_BUS  7u
#define BQ27427_I2C_ADDR 0x55u

/* Standard commands (TRM SLUUCD5). */
#define BQ27427_CMD_CONTROL        0x00u
#define BQ27427_CMD_TEMP           0x02u /* 0.1 K */
#define BQ27427_CMD_VOLTAGE        0x04u
#define BQ27427_CMD_FLAGS          0x06u
#define BQ27427_CMD_NOM_CAPACITY   0x08u
#define BQ27427_CMD_AVAIL_CAPACITY 0x0au
#define BQ27427_CMD_REM_CAPACITY   0x0cu
#define BQ27427_CMD_FULL_CAPACITY  0x0eu
#define BQ27427_CMD_AVG_CURRENT    0x10u
#define BQ27427_CMD_AVG_POWER      0x18u
#define BQ27427_CMD_SOC            0x1cu
#define BQ27427_CMD_INT_TEMP       0x1eu
#define BQ27427_CMD_REM_CAP_UNFL   0x28u
#define BQ27427_CMD_REM_CAP_FIL    0x2au
#define BQ27427_CMD_FULL_CAP_UNFL  0x2cu
#define BQ27427_CMD_FULL_CAP_FIL   0x2eu
#define BQ27427_CMD_SOC_UNFL       0x30u
#define BQ27427_EXT_DATA_CLASS     0x3eu
#define BQ27427_EXT_DATA_BLOCK     0x3fu
#define BQ27427_EXT_BLOCK_DATA     0x40u
#define BQ27427_EXT_CHECKSUM       0x60u
#define BQ27427_EXT_DATA_CONTROL   0x61u

/* Control() subcommands. */
#define BQ27427_CTRL_CHEM_ID       0x0008u
#define BQ27427_CTRL_SET_CFGUPDATE 0x0013u
#define BQ27427_CTRL_SEALED        0x0020u
#define BQ27427_CTRL_CHEM_B        0x0031u /* TRM: Chem ID 0x1202 */
#define BQ27427_CTRL_SOFT_RESET    0x0042u

#define BQ27427_FLAGS_CFGUPMODE_SHIFT 4u
#define BQ27427_CFGUPDATE_TRIES       100
#define BQ27427_CFGUPDATE_POLL_MS     25u
#define BQ27427_DM_BLOCK_SIZE         32u
#define BQ27427_KELVIN_OFFSET_DK      2731

/* One cached data-memory block (36 bytes on the stack). */
typedef struct {
    uint8_t subclass;                    /* +0x00 DataClass() */
    uint8_t block;                       /* +0x01 DataBlock() */
    uint8_t data[BQ27427_DM_BLOCK_SIZE]; /* +0x02 BlockData() image */
    uint8_t valid;                       /* +0x22 read and checksum matched */
    uint8_t dirty;                       /* +0x23 modified since read */
} g2_bq27427_dm_block_t;
_Static_assert(sizeof(g2_bq27427_dm_block_t) == 0x24, "stock DM block buffer is 36 bytes");
_Static_assert(offsetof(g2_bq27427_dm_block_t, valid) == 0x22, "stock valid offset");

/* Data-memory parameter descriptor; offset is the absolute subclass byte
 * offset (block = offset / 32). The trailing pair looks like a min/max range
 * but no stock code reads it. */
typedef struct {
    uint8_t subclass; /* +0 */
    uint8_t offset;   /* +1 */
    uint8_t size;     /* +2 1 or 2 bytes */
    uint8_t pad;      /* +3 */
    uint16_t min;     /* +4 unused */
    uint16_t max;     /* +6 unused */
} g2_bq27427_dm_desc_t;
_Static_assert(sizeof(g2_bq27427_dm_desc_t) == 8, "stock descriptor stride is 8");

/* Descriptor indices. The table is initialised data at RAM 0x200006ec
 * (decoded from SRAM init record 0x75d3f4); bytes per entry are listed as
 * subclass offset size pad min(le16) max(le16). Names follow TRM SLUUCD5 /
 * Zephyr bq274xx where they agree; the rest are left descriptive. */
enum {
    DM_DESIGN_CAPACITY = 0,  /* 52 06 02 00 0000 1f40: State 82 byte 6, I2, 0..8000 */
    DM_DESIGN_ENERGY = 1,    /* 52 08 02 00 0000 7fff: State 82 byte 8, I2 */
    DM_TERMINATE_VOLTAGE = 2,/* 52 0a 02 00 0bb8 1130: State 82 byte 10, I2, 3000..4400 */
    DM_REGISTERS_BYTE4 = 3,  /* 40 04 01 00 0000 00ff: Registers 64 byte 4, U1 */
    DM_UPDATE_STATUS = 4,    /* 52 02 01 00 0000 00ff: State 82 byte 2, H1 */
    DM_CURRENT_THRESH = 5,   /* 51 00 02 00 0000 07d0: Current Thresholds 81 byte 0, I2 */
    DM_CC_GAIN_BYTE5 = 6,    /* 69 05 01 00 0000 7fff: subclass 105 byte 5 (Zephyr: CC Gain sign byte) */
};

typedef struct {
    int32_t efd; /* +0 energy-full-design */
    int32_t cfd; /* +4 charge-full-design */
    int32_t vmd; /* +8 voltage-min-design */
} g2_bq27427_params_t;

extern uint32_t g2_bq27427_unseal_key;                       /* RAM 0x200006e8, initialised 0x80008000 */
extern g2_bq27427_dm_desc_t g2_bq27427_dm_desc_table[7];       /* RAM 0x200006ec, initialised data, read only here */
extern g2_charger_telemetry_t g2_charger_telemetry;          /* RAM 0x20073b18 */

extern void *audio_queue_copy_bytes(void *, const void *, uint32_t); /* 0x439be4 */
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);      /* 0x43c0e4 */
extern void audio_uart_lv_memzero_48949c(void *, uint32_t);
extern void g2_delay_ms_4910f4(uint32_t ms);
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

int32_t bq27427_i2c_read_reg(uint8_t reg, uint8_t one_byte);
uint32_t bq27427_i2c_write_reg(uint8_t reg, uint16_t value, uint8_t one_byte);
uint32_t bq27427_i2c_read_block(uint8_t reg, void *buf, uint32_t len);
uint32_t bq27427_i2c_write_block(uint8_t reg, const void *data, uint32_t len);
int32_t bq27427_read_flags(void);
int32_t bq27427_read_soc(void);
int32_t bq27427_read_temperature(void);
int32_t bq27427_read_battery_voltage(void);
int32_t bq27427_read_charge(uint8_t reg);
int32_t bq27427_read_nom_capacity(void);
int32_t bq27427_read_avail_capacity(void);
int32_t bq27427_read_rem_capacity(void);
int32_t bq27427_read_full_capacity(void);
int32_t bq27427_read_ai(void);
int32_t bq27427_read_ap(void);
int32_t bq27427_read_int_temp(void);
int32_t bq27427_read_rem_cap_unfl(void);
int32_t bq27427_read_rem_cap_fil(void);
int32_t bq27427_read_full_cap_unfl(void);
int32_t bq27427_read_full_cap_fil(void);
int32_t bq27427_read_soc_unfl(void);
int32_t bq27427_seal(void);
int32_t bq27427_unseal(void);
uint8_t bq27427_checksum_dm_block(const g2_bq27427_dm_block_t *blk);
int32_t bq27427_read_dm_block(g2_bq27427_dm_block_t *blk);
void bq27427_update_dm_block(g2_bq27427_dm_block_t *blk, uint8_t index, int32_t value);
int32_t bq27427_cfgupdate_priv(uint8_t enter);
int32_t bq27427_set_cfgupdate(void);
int32_t bq27427_soft_reset(void);
int32_t bq27427_execute_control_word(uint8_t subcommand);
int32_t bq27427_write_dm_block(g2_bq27427_dm_block_t *blk);
void bq27427_configure_from_params(const g2_bq27427_params_t *params);
int32_t bq27427_change_chemistry_profile(void);
void bq27427_settings(void);

static const char module_tag[] = "charge"; /* ROM 0x78d46c */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\chg\\drv_bq27427.c"; /* ROM 0x70ade4 */
static const char fn_write_block[] = "bq27427_i2c_write_block"; /* ROM 0x776afc */
static const char fn_read_flags[] = "bq27427_read_flags"; /* ROM 0x77eed8 */
static const char fn_read_soc[] = "bq27427_read_soc"; /* ROM 0x77eeec */
static const char fn_read_temperature[] = "bq27427_read_temperature"; /* ROM 0x76af88 */
static const char fn_read_battery_voltage[] = "bq27427_read_battery_voltage"; /* ROM 0x75f5f0 */
static const char fn_read_charge[] = "bq27427_read_charge"; /* ROM 0x77ef00 */
static const char fn_read_ai[] = "bq27427_read_ai"; /* ROM 0x785c00 */
static const char fn_read_ap[] = "bq27427_read_ap"; /* ROM 0x785c10 */
static const char fn_seal[] = "bq27427_seal"; /* ROM 0x785c20 */
static const char fn_unseal[] = "bq27427_unseal"; /* ROM 0x785c30 */
static const char fn_checksum_dm_block[] = "bq27427_checksum_dm_block"; /* ROM 0x76afdc */
static const char fn_read_dm_block[] = "bq27427_read_dm_block"; /* ROM 0x776b44 */
static const char fn_update_dm_block[] = "bq27427_update_dm_block"; /* ROM 0x776b5c */
static const char fn_cfgupdate_priv[] = "bq27427_cfgupdate_priv"; /* ROM 0x776b74 */
static const char fn_set_cfgupdate[] = "bq27427_set_cfgupdate"; /* ROM 0x776b8c */
static const char fn_soft_reset[] = "bq27427_soft_reset"; /* ROM 0x77ef14 */
static const char fn_write_dm_block[] = "bq27427_write_dm_block"; /* ROM 0x776ba4 */
static const char fn_change_chemistry_profile[] = "bq27427_change_chemistry_profile"; /* ROM 0x7539a8 */
static const char fn_settings[] = "bq27427_settings"; /* ROM 0x77ef28 */
static const char fn_status_update[] = "bq27427_status_update"; /* ROM 0x776bbc */
static const char fn_hw_init[] = "DRV_Bq27427HwInit"; /* ROM 0x77ef3c */
static const char msg_bulk_write[] = "FG: bulk write ret:%d "; /* ROM 0x776b14 */
static const char msg_bulk_write_short[] = "[charge]FG: bulk write ret:%d "; /* ROM 0x75f590 */
static const char msg_flags[] = "FG: error reading flags"; /* ROM 0x776b2c */
static const char msg_flags_short[] = "[charge]FG: error reading flags"; /* ROM 0x75f5b0 */
static const char msg_soc[] = "FG: error reading State-of-Charge "; /* ROM 0x7538f4 */
static const char msg_soc_short[] = "[charge]FG: error reading State-of-Charge "; /* ROM 0x73e0e0 */
static const char msg_temp[] = "FG: error reading temperature"; /* ROM 0x75f5d0 */
static const char msg_temp_short[] = "[charge]FG: error reading temperature"; /* ROM 0x749394 */
static const char msg_voltage[] = "FG: error reading battery voltage"; /* ROM 0x753918 */
static const char msg_voltage_short[] = "[charge]FG: error reading battery voltage"; /* ROM 0x73e10c */
static const char msg_register[] = "FG: error reading register.[REG:%02x]: [ERR_NO:%d]"; /* ROM 0x728b64 */
static const char msg_register_short[] = "[charge]FG: error reading register.[REG:%02x]: [ERR_NO:%d]"; /* ROM 0x71447c */
static const char msg_seal[] = "FG: bus error on seal: %d"; /* ROM 0x76afa4 */
static const char msg_seal_short[] = "[charge]FG: bus error on seal: %d"; /* ROM 0x75393c */
static const char msg_unseal_key[] = "FG: unseal failed due to missing key"; /* ROM 0x7493bc */
static const char msg_unseal_key_short[] = "[charge]FG: unseal failed due to missing key"; /* ROM 0x7332e4 */
static const char msg_unseal[] = "FG: bus error on unseal: %d"; /* ROM 0x76afc0 */
static const char msg_unseal_short[] = "[charge]FG: bus error on unseal: %d"; /* ROM 0x753960 */
static const char msg_checksum[] = "[FG] Calculated Checksum:%d "; /* ROM 0x75f610 */
static const char msg_checksum_short[] = "[charge][FG] Calculated Checksum:%d "; /* ROM 0x7493e4 */
static const char msg_read_mem[] = "FG: bus error reading chip memory: %d"; /* ROM 0x749434 */
static const char msg_read_mem_short[] = "[charge]FG: bus error reading chip memory: %d"; /* ROM 0x733344 */
static const char msg_dm_param[] = "[FG][Data Memory Parameter][ClassId:%d]:  "; /* ROM 0x73e138 */
static const char msg_dm_param_short[] = "[charge][FG][Data Memory Parameter][ClassId:%d]:  "; /* ROM 0x728b98 */
static const char msg_read_checksum[] = "[FG] Read From Register: Checksum:%d "; /* ROM 0x74940c */
static const char msg_read_checksum_short[] = "[charge][FG] Read From Register: Checksum:%d "; /* ROM 0x733314 */
static const char msg_update[] = "[FG][UPDATE]: reg_id:%d subclass_id:%d offset:%d setVal:%d(0x%02x)"; /* ROM 0x702218 */
static const char msg_update_short[] = "[charge][FG][UPDATE]: reg_id:%d subclass_id:%d offset:%d setVal:%d(0x%02x)"; /* ROM 0x6f3058 */
static const char msg_update_1[] = "[FG][UPDATE]: offset:%d data:(0x%02x)"; /* ROM 0x74945c */
static const char msg_update_1_short[] = "[charge][FG][UPDATE]: offset:%d data:(0x%02x)"; /* ROM 0x733374 */
static const char msg_update_2[] = "[FG][UPDATE]: offset:%d data:(0x%02x)(0x%02x)"; /* ROM 0x7333a4 */
static const char msg_update_2_short[] = "[charge][FG][UPDATE]: offset:%d data:(0x%02x)(0x%02x)"; /* ROM 0x71e098 */
static const char msg_update_size[] = "[FG][UPDATE]: unsupport bytes number !"; /* ROM 0x749484 */
static const char msg_update_size_short[] = "[charge][FG][UPDATE]: unsupport bytes number !"; /* ROM 0x7333d4 */
static const char msg_cfgupdate[] = "[FG] cfgupdate:%d, retries:%d "; /* ROM 0x75f630 */
static const char msg_cfgupdate_short[] = "[charge][FG] cfgupdate:%d, retries:%d "; /* ROM 0x7494ac */
static const char msg_set_cfgupdate[] = "FG: bus error on set_cfgupdate: %d"; /* ROM 0x753984 */
static const char msg_set_cfgupdate_short[] = "[charge]FG: bus error on set_cfgupdate: %d"; /* ROM 0x73e164 */
static const char msg_soft_reset[] = "FG: bus error on soft_reset: %d"; /* ROM 0x75f650 */
static const char msg_soft_reset_short[] = "[charge]FG: bus error on soft_reset: %d"; /* ROM 0x7494d4 */
static const char msg_write_dm[] = "[FG][FUNC][Write Data Memory Block][dirty:%d][class:%d][block:%d]"; /* ROM 0x70225c */
static const char msg_write_dm_short[] = "[charge][FG][FUNC][Write Data Memory Block][dirty:%d][class:%d][block:%d]"; /* ROM 0x6f30a4 */
static const char msg_write_mem[] = "FG: bus error writing chip memory: %d"; /* ROM 0x7494fc */
static const char msg_write_mem_short[] = "[charge]FG: bus error writing chip memory: %d"; /* ROM 0x733404 */
static const char msg_chem_id[] = "[FG]: error reading chem id."; /* ROM 0x75f670 */
static const char msg_chem_id_short[] = "[charge][FG]: error reading chem id."; /* ROM 0x749524 */
static const char msg_chem_before[] = "[FG]: before change chemistry_profile:0x%04x."; /* ROM 0x733434 */
static const char msg_chem_before_short[] = "[charge][FG]: before change chemistry_profile:0x%04x."; /* ROM 0x71e0d0 */
static const char msg_chem_after[] = "[FG]: after change chemistry_profile:0x%04x."; /* ROM 0x733464 */
static const char msg_chem_after_short[] = "[charge][FG]: after change chemistry_profile:0x%04x."; /* ROM 0x71e108 */
static const char msg_settings[] = "[FG][FUNC] bq27427_settings efd:%d cfd:%d vmd:%d "; /* ROM 0x728bcc */
static const char msg_settings_short[] = "[charge][FG][FUNC] bq27427_settings efd:%d cfd:%d vmd:%d "; /* ROM 0x7144b8 */
static const char msg_bad_efd[] = "FG: invalid battery:energy-full-design-microwatt-hours %d"; /* ROM 0x7144f4 */
static const char msg_bad_efd_short[] = "[charge]FG: invalid battery:energy-full-design-microwatt-hours %d"; /* ROM 0x7022a0 */
static const char msg_bad_cfd[] = "FG: invalid battery:charge-full-design-microamp-hours %d"; /* ROM 0x714530 */
static const char msg_bad_cfd_short[] = "[charge]FG: invalid battery:charge-full-design-microamp-hours %d"; /* ROM 0x7022e4 */
static const char msg_bad_vmd[] = "FG: invalid battery:voltage-min-design-microvolt %d"; /* ROM 0x728c00 */
static const char msg_bad_vmd_short[] = "[charge]FG: invalid battery:voltage-min-design-microvolt %d"; /* ROM 0x71456c */
static const char msg_flag_error[] = "bq27427 read flag error"; /* ROM 0x776bd4 */
static const char msg_flag_error_short[] = "[charge]bq27427 read flag error"; /* ROM 0x75f690 */
static const char msg_init_start[] = "[FG] bq27427 hardware init start: "; /* ROM 0x7539cc */
static const char msg_init_start_short[] = "[charge][FG] bq27427 hardware init start: "; /* ROM 0x73e190 */
static const char msg_init_failure[] = "bq27427 init failure !"; /* ROM 0x776bec */
static const char msg_init_failure_short[] = "[charge]bq27427 init failure !"; /* ROM 0x75f6b0 */
static const char msg_init_done[] = "[FG] bq27427 hardware init done!"; /* ROM 0x7539f0 */
static const char msg_init_done_short[] = "[charge][FG] bq27427 hardware init done!"; /* ROM 0x73e1bc */

/* Level-n log code for compress_log_output: level << 26 | argument count << 22. */
#define FG_LOG_CODE(level, nargs) (((uint32_t)(level) << 26) | ((uint32_t)(nargs) << 22))

/* Reads one register, or the little-endian pair reg/reg+1. The HAL status is
 * ignored, so the result is never negative even though every caller checks. */
int32_t bq27427_i2c_read_reg(uint8_t reg, uint8_t one_byte) {
    uint8_t rx[2];
    uint8_t tx[2];
    int32_t value;

    audio_uart_buffer_zero(tx, 2u, 0u);
    audio_uart_buffer_zero(rx, 2u, 0u);
    tx[0] = reg;
    (void)hal_i2c_transfer_full(BQ27427_I2C_BUS, BQ27427_I2C_ADDR, tx, 1u, &rx[0], 1u);
    value = rx[0];
    if (one_byte == 0u) {
        tx[0] = (uint8_t)(reg + 1u);
        (void)hal_i2c_transfer_full(BQ27427_I2C_BUS, BQ27427_I2C_ADDR, tx, 1u, &rx[1], 1u);
        value = (int32_t)(rx[0] | ((uint32_t)rx[1] << 8));
    }
    return value;
}

uint32_t bq27427_i2c_write_reg(uint8_t reg, uint16_t value, uint8_t one_byte) {
    uint8_t buf[3];

    buf[0] = reg;
    buf[1] = (uint8_t)value;
    if (one_byte != 0u)
        return hal_i2c_transfer_joined(BQ27427_I2C_BUS, BQ27427_I2C_ADDR, &buf[0], 1u, &buf[1], 1u);
    buf[2] = (uint8_t)(value >> 8);
    return hal_i2c_transfer_joined(BQ27427_I2C_BUS, BQ27427_I2C_ADDR, &buf[0], 1u, &buf[1], 2u);
}

uint32_t bq27427_i2c_read_block(uint8_t reg, void *buf, uint32_t len) {
    uint8_t cmd = reg;
    return hal_i2c_transfer_full(BQ27427_I2C_BUS, BQ27427_I2C_ADDR, &cmd, 1u, buf, len);
}

/* Copies into a 35-byte staging area and logs a bus failure; always returns 0. */
uint32_t bq27427_i2c_write_block(uint8_t reg, const void *data, uint32_t len) {
    uint8_t cmd = reg;
    uint8_t staging[35];
    uint32_t ret;

    (void)audio_queue_copy_bytes(staging, data, len);
    ret = hal_i2c_transfer_joined(BQ27427_I2C_BUS, BQ27427_I2C_ADDR, &cmd, 1u, staging, len);
    if (ret != 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, fn_write_block, 0xb5u, msg_bulk_write, ret);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(FG_LOG_CODE(1, 1), msg_bulk_write_short, msg_bulk_write_short, ret);
    }
    return 0u;
}

int32_t bq27427_read_flags(void) {
    int32_t flags = bq27427_i2c_read_reg(BQ27427_CMD_FLAGS, 0u);
    if (flags < 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, fn_read_flags, 0xc2u, msg_flags);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(FG_LOG_CODE(1, 0), msg_flags_short, msg_flags_short);
    }
    return flags;
}

int32_t bq27427_read_soc(void) {
    int32_t soc = bq27427_i2c_read_reg(BQ27427_CMD_SOC, 0u);
    if (soc < 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, fn_read_soc, 0xd1u, msg_soc);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(FG_LOG_CODE(1, 0), msg_soc_short, msg_soc_short);
    }
    return soc;
}

/* Temperature() is in 0.1 K; returns 0.1 degC. */
int32_t bq27427_read_temperature(void) {
    int32_t temp = bq27427_i2c_read_reg(BQ27427_CMD_TEMP, 0u);
    if (temp < 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module_tag, source_file, fn_read_temperature, 0xdeu, msg_temp);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(FG_LOG_CODE(4, 0), msg_temp_short, msg_temp_short);
    }
    return temp - BQ27427_KELVIN_OFFSET_DK;
}

int32_t bq27427_read_battery_voltage(void) {
    int32_t mv = bq27427_i2c_read_reg(BQ27427_CMD_VOLTAGE, 0u);
    if (mv < 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module_tag, source_file, fn_read_battery_voltage, 0xecu, msg_voltage);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(FG_LOG_CODE(4, 0), msg_voltage_short, msg_voltage_short);
    }
    return mv;
}

/* Generic unsigned two-byte standard-command read. */
int32_t bq27427_read_charge(uint8_t reg) {
    int32_t value = bq27427_i2c_read_reg(reg, 0u);
    if (value < 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module_tag, source_file, fn_read_charge, 0xf9u, msg_register, reg, value);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(FG_LOG_CODE(4, 2), msg_register_short, msg_register_short, reg, value);
    }
    return value;
}

int32_t bq27427_read_nom_capacity(void) { return bq27427_read_charge(BQ27427_CMD_NOM_CAPACITY); }
int32_t bq27427_read_avail_capacity(void) { return bq27427_read_charge(BQ27427_CMD_AVAIL_CAPACITY); }
int32_t bq27427_read_rem_capacity(void) { return bq27427_read_charge(BQ27427_CMD_REM_CAPACITY); }
int32_t bq27427_read_full_capacity(void) { return bq27427_read_charge(BQ27427_CMD_FULL_CAPACITY); }

/* AverageCurrent(), signed mA. The stock error text is the voltage one. */
int32_t bq27427_read_ai(void) {
    int32_t ai = bq27427_i2c_read_reg(BQ27427_CMD_AVG_CURRENT, 0u);
    if (ai < 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module_tag, source_file, fn_read_ai, 0x11fu, msg_voltage);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(FG_LOG_CODE(4, 0), msg_voltage_short, msg_voltage_short);
    }
    return (int16_t)ai;
}

/* AveragePower(), signed mW. Same copied error text as read_ai. */
int32_t bq27427_read_ap(void) {
    int32_t ap = bq27427_i2c_read_reg(BQ27427_CMD_AVG_POWER, 0u);
    if (ap < 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module_tag, source_file, fn_read_ap, 0x12bu, msg_voltage);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(FG_LOG_CODE(4, 0), msg_voltage_short, msg_voltage_short);
    }
    return (int16_t)ap;
}

int32_t bq27427_read_int_temp(void) { return bq27427_read_charge(BQ27427_CMD_INT_TEMP); }
int32_t bq27427_read_rem_cap_unfl(void) { return bq27427_read_charge(BQ27427_CMD_REM_CAP_UNFL); }
int32_t bq27427_read_rem_cap_fil(void) { return bq27427_read_charge(BQ27427_CMD_REM_CAP_FIL); }
int32_t bq27427_read_full_cap_unfl(void) { return bq27427_read_charge(BQ27427_CMD_FULL_CAP_UNFL); }
int32_t bq27427_read_full_cap_fil(void) { return bq27427_read_charge(BQ27427_CMD_FULL_CAP_FIL); }
int32_t bq27427_read_soc_unfl(void) { return bq27427_read_charge(BQ27427_CMD_SOC_UNFL); }

int32_t bq27427_seal(void) {
    int32_t ret = (int32_t)bq27427_i2c_write_reg(BQ27427_CMD_CONTROL, BQ27427_CTRL_SEALED, 0u);
    if (ret == 0)
        return 0;
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, fn_seal, 0x15cu, msg_seal, ret);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(FG_LOG_CODE(4, 1), msg_seal_short, msg_seal_short, ret);
    return ret;
}

/* Writes the high then the low half of the 32-bit key to Control(). */
int32_t bq27427_unseal(void) {
    int32_t ret;

    if (g2_bq27427_unseal_key == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module_tag, source_file, fn_unseal, 0x168u, msg_unseal_key);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(FG_LOG_CODE(4, 0), msg_unseal_key_short, msg_unseal_key_short);
        return -1;
    }
    ret = (int32_t)bq27427_i2c_write_reg(BQ27427_CMD_CONTROL, (uint16_t)(g2_bq27427_unseal_key >> 16), 0u);
    if (ret == 0) {
        ret = (int32_t)bq27427_i2c_write_reg(BQ27427_CMD_CONTROL, (uint16_t)g2_bq27427_unseal_key, 0u);
        if (ret == 0)
            return 0;
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, fn_unseal, 0x177u, msg_unseal, ret);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(FG_LOG_CODE(4, 1), msg_unseal_short, msg_unseal_short, ret);
    return ret;
}

/* BlockDataCheckSum = 0xff - (sum of the 32 data bytes mod 256). */
uint8_t bq27427_checksum_dm_block(const g2_bq27427_dm_block_t *blk) {
    uint16_t sum = 0;

    for (int i = 0; i < (int)BQ27427_DM_BLOCK_SIZE; i++)
        sum = (uint16_t)(sum + blk->data[i]);
    sum &= 0xffu;
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, fn_checksum_dm_block, 0x185u, msg_checksum, 0xff - sum);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(FG_LOG_CODE(4, 1), msg_checksum_short, msg_checksum_short, 0xff - sum);
    return (uint8_t)(0xffu - sum);
}

/* Selects blk->subclass/blk->block, reads the 32 bytes and accepts them only
 * if the gauge checksum matches. BlockDataControl() is not written here. */
int32_t bq27427_read_dm_block(g2_bq27427_dm_block_t *blk) {
    int32_t ret;

    blk->valid = 0u;
    ret = (int32_t)bq27427_i2c_write_reg(BQ27427_EXT_DATA_CLASS, blk->subclass, 1u);
    if (ret == 0)
        ret = (int32_t)bq27427_i2c_write_reg(BQ27427_EXT_DATA_BLOCK, blk->block, 1u);
    if (ret == 0) {
        g2_delay_ms_4910f4(1u);
        ret = (int32_t)bq27427_i2c_read_block(BQ27427_EXT_BLOCK_DATA, blk->data, BQ27427_DM_BLOCK_SIZE);
    }
    if (ret == 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module_tag, source_file, fn_read_dm_block, 0x19cu, msg_dm_param, blk->subclass);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(FG_LOG_CODE(4, 1), msg_dm_param_short, msg_dm_param_short, blk->subclass);
        ret = bq27427_i2c_read_reg(BQ27427_EXT_CHECKSUM, 1u);
        if (ret >= 0) {
            if (audio_log_flags() & 2u)
                audio_log_extended(4u, module_tag, source_file, fn_read_dm_block, 0x1a5u, msg_read_checksum, ret);
            if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
                (void)compress_log_output(FG_LOG_CODE(4, 1), msg_read_checksum_short, msg_read_checksum_short, ret);
            if ((uint8_t)ret == bq27427_checksum_dm_block(blk)) {
                blk->valid = 1u;
                blk->dirty = 0u;
                return 0;
            }
            ret = -1;
        }
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, fn_read_dm_block, 0x1b2u, msg_read_mem, ret);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(FG_LOG_CODE(4, 1), msg_read_mem_short, msg_read_mem_short, ret);
    return ret;
}

/* Patches the cached block from descriptor `index`; the whole byte (or the
 * big-endian word) is overwritten and the block marked dirty. A block that
 * was never read successfully is left untouched. */
void bq27427_update_dm_block(g2_bq27427_dm_block_t *blk, uint8_t index, int32_t value) {
    const g2_bq27427_dm_desc_t *desc = &g2_bq27427_dm_desc_table[index];
    int32_t offset = (int32_t)desc->offset % (int32_t)BQ27427_DM_BLOCK_SIZE;

    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, fn_update_dm_block, 0x1beu, msg_update,
                           index, desc->subclass, offset, value, value);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(FG_LOG_CODE(4, 5), msg_update_short, msg_update_short,
                                  index, desc->subclass, offset, value, value);
    if (blk->valid == 0u)
        return;
    if (desc->size == 1u) {
        blk->data[offset] = (uint8_t)value;
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module_tag, source_file, fn_update_dm_block, 0x1c5u, msg_update_1,
                               offset, blk->data[offset]);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(FG_LOG_CODE(4, 2), msg_update_1_short, msg_update_1_short,
                                      offset, blk->data[offset]);
    } else if (desc->size == 2u) {
        blk->data[offset] = (uint8_t)((uint32_t)value >> 8);
        blk->data[offset + 1] = (uint8_t)value;
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module_tag, source_file, fn_update_dm_block, 0x1c9u, msg_update_2,
                               offset, blk->data[offset], blk->data[offset + 1]);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(FG_LOG_CODE(4, 3), msg_update_2_short, msg_update_2_short,
                                      offset, blk->data[offset], blk->data[offset + 1]);
    } else {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module_tag, source_file, fn_update_dm_block, 0x1cbu, msg_update_size);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(FG_LOG_CODE(4, 0), msg_update_size_short, msg_update_size_short);
        return;
    }
    blk->dirty = 1u;
}

/* enter != 0: SET_CFGUPDATE and wait for Flags.CFGUPMODE = 1; enter == 0:
 * SOFT_RESET and wait for it to clear. Polls every 25 ms, at most 100 times;
 * running out of tries is not an error. */
int32_t bq27427_cfgupdate_priv(uint8_t enter) {
    int32_t tries = BQ27427_CFGUPDATE_TRIES;
    int32_t ret;
    int32_t flags;

    ret = (int32_t)bq27427_i2c_write_reg(BQ27427_CMD_CONTROL,
                                         enter != 0u ? BQ27427_CTRL_SET_CFGUPDATE : BQ27427_CTRL_SOFT_RESET, 0u);
    if (ret != 0)
        return ret;
    do {
        g2_delay_ms_4910f4(BQ27427_CFGUPDATE_POLL_MS);
        flags = bq27427_i2c_read_reg(BQ27427_CMD_FLAGS, 0u);
        if (flags < 0)
            return flags;
    } while ((((uint32_t)(uint8_t)flags >> BQ27427_FLAGS_CFGUPMODE_SHIFT) & 1u) != enter && --tries != 0);
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, fn_cfgupdate_priv, 0x1e3u, msg_cfgupdate,
                           enter, BQ27427_CFGUPDATE_TRIES - tries);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(FG_LOG_CODE(4, 2), msg_cfgupdate_short, msg_cfgupdate_short,
                                  enter, BQ27427_CFGUPDATE_TRIES - tries);
    return 0;
}

int32_t bq27427_set_cfgupdate(void) {
    int32_t ret = bq27427_cfgupdate_priv(1u);
    if (ret != 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module_tag, source_file, fn_set_cfgupdate, 0x1ecu, msg_set_cfgupdate, ret);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(FG_LOG_CODE(4, 1), msg_set_cfgupdate_short, msg_set_cfgupdate_short, ret);
    }
    return ret;
}

/* SOFT_RESET leaves CONFIG UPDATE mode (and re-simulates). */
int32_t bq27427_soft_reset(void) {
    int32_t ret = bq27427_cfgupdate_priv(0u);
    if (ret != 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module_tag, source_file, fn_soft_reset, 0x1f5u, msg_soft_reset, ret);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(FG_LOG_CODE(4, 1), msg_soft_reset_short, msg_soft_reset_short, ret);
    }
    return ret;
}

int32_t bq27427_execute_control_word(uint8_t subcommand) {
    int32_t ret = (int32_t)bq27427_i2c_write_reg(BQ27427_CMD_CONTROL, subcommand, 0u);
    if (ret == 0) {
        g2_delay_ms_4910f4(100u);
        ret = 0;
    }
    return ret;
}

/* Commits a dirty block inside CONFIG UPDATE mode: BlockDataControl = 0,
 * class, block, 32 data bytes, then the recomputed checksum, then SOFT_RESET.
 * A failed step still issues SOFT_RESET before reporting the error. */
int32_t bq27427_write_dm_block(g2_bq27427_dm_block_t *blk) {
    int32_t ret;

    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, fn_write_dm_block, 0x20bu, msg_write_dm,
                           blk->dirty, blk->subclass, blk->block);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(FG_LOG_CODE(4, 3), msg_write_dm_short, msg_write_dm_short,
                                  blk->dirty, blk->subclass, blk->block);
    if (blk->dirty == 0u)
        return 0;
    ret = bq27427_set_cfgupdate();
    if (ret != 0)
        return ret;
    ret = (int32_t)bq27427_i2c_write_reg(BQ27427_EXT_DATA_CONTROL, 0u, 1u);
    if (ret == 0)
        ret = (int32_t)bq27427_i2c_write_reg(BQ27427_EXT_DATA_CLASS, blk->subclass, 1u);
    if (ret == 0)
        ret = (int32_t)bq27427_i2c_write_reg(BQ27427_EXT_DATA_BLOCK, blk->block, 1u);
    if (ret == 0) {
        g2_delay_ms_4910f4(1u);
        ret = (int32_t)bq27427_i2c_write_block(BQ27427_EXT_BLOCK_DATA, blk->data, BQ27427_DM_BLOCK_SIZE);
    }
    if (ret == 0)
        ret = (int32_t)bq27427_i2c_write_reg(BQ27427_EXT_CHECKSUM, bq27427_checksum_dm_block(blk), 1u);
    if (ret == 0) {
        g2_delay_ms_4910f4(1u);
        ret = bq27427_soft_reset();
        if (ret != 0)
            return ret;
        blk->dirty = 0u;
        return 0;
    }
    (void)bq27427_soft_reset();
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, fn_write_dm_block, 0x236u, msg_write_mem, ret);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(FG_LOG_CODE(4, 1), msg_write_mem_short, msg_write_mem_short, ret);
    return ret;
}

/* Applies design capacity/energy, terminate voltage and the fixed vendor
 * values (Update Status 3, Registers byte 4 = 0x2b, subclass 105 byte 5 =
 * 0x28) and seals again. Results of the individual reads/commits are
 * ignored. Terminate voltage shares the State block with design capacity, so
 * when cfd/efd are not positive that block is never read and the voltage
 * update is silently dropped. The Current Thresholds block is read only. */
void bq27427_configure_from_params(const g2_bq27427_params_t *params) {
    g2_bq27427_dm_block_t state;
    g2_bq27427_dm_block_t voltage;
    g2_bq27427_dm_block_t registers;
    g2_bq27427_dm_block_t thresholds;
    g2_bq27427_dm_block_t calibration;
    bool shared;

    audio_uart_lv_memzero_48949c(&state, sizeof(state));
    state.subclass = g2_bq27427_dm_desc_table[DM_DESIGN_CAPACITY].subclass;
    state.block = (uint8_t)(g2_bq27427_dm_desc_table[DM_DESIGN_CAPACITY].offset >> 5);
    audio_uart_lv_memzero_48949c(&voltage, sizeof(voltage));
    voltage.subclass = g2_bq27427_dm_desc_table[DM_TERMINATE_VOLTAGE].subclass;
    voltage.block = (uint8_t)(g2_bq27427_dm_desc_table[DM_TERMINATE_VOLTAGE].offset >> 5);
    audio_uart_lv_memzero_48949c(&registers, sizeof(registers));
    registers.subclass = g2_bq27427_dm_desc_table[DM_REGISTERS_BYTE4].subclass;
    registers.block = (uint8_t)(g2_bq27427_dm_desc_table[DM_REGISTERS_BYTE4].offset >> 5);
    audio_uart_lv_memzero_48949c(&thresholds, sizeof(thresholds));
    thresholds.subclass = g2_bq27427_dm_desc_table[DM_CURRENT_THRESH].subclass;
    thresholds.block = (uint8_t)(g2_bq27427_dm_desc_table[DM_CURRENT_THRESH].offset >> 5);
    audio_uart_lv_memzero_48949c(&calibration, sizeof(calibration));
    calibration.subclass = g2_bq27427_dm_desc_table[DM_CC_GAIN_BYTE5].subclass;
    calibration.block = (uint8_t)(g2_bq27427_dm_desc_table[DM_CC_GAIN_BYTE5].offset >> 5);
    if (bq27427_unseal() < 0)
        return;
    if (params->cfd > 0 && params->efd > 0) {
        (void)bq27427_read_dm_block(&state);
        bq27427_update_dm_block(&state, DM_DESIGN_CAPACITY, params->cfd);
        bq27427_update_dm_block(&state, DM_DESIGN_ENERGY, params->efd);
        bq27427_update_dm_block(&state, DM_UPDATE_STATUS, 3);
    }
    if (params->vmd > 0) {
        shared = state.subclass == voltage.subclass && state.block == voltage.block;
        if (!shared)
            (void)bq27427_read_dm_block(&voltage);
        bq27427_update_dm_block(shared ? &state : &voltage, DM_TERMINATE_VOLTAGE, params->vmd);
    }
    (void)bq27427_read_dm_block(&registers);
    bq27427_update_dm_block(&registers, DM_REGISTERS_BYTE4, 0x2b);
    (void)bq27427_read_dm_block(&thresholds);
    (void)bq27427_read_dm_block(&calibration);
    bq27427_update_dm_block(&calibration, DM_CC_GAIN_BYTE5, 0x28);
    (void)bq27427_write_dm_block(&state);
    (void)bq27427_write_dm_block(&voltage);
    (void)bq27427_write_dm_block(&registers);
    (void)bq27427_write_dm_block(&calibration);
    (void)bq27427_seal();
}

/* Unconditionally switches to the CHEM_B profile (no compare with the current
 * Chem ID), logging CHEM_ID before and after. */
int32_t bq27427_change_chemistry_profile(void) {
    int32_t chem_id;
    int32_t ret;

    if (bq27427_unseal() < 0)
        return -1;
    (void)bq27427_i2c_write_reg(BQ27427_CMD_CONTROL, BQ27427_CTRL_CHEM_ID, 0u);
    chem_id = bq27427_i2c_read_reg(BQ27427_CMD_CONTROL, 0u);
    if (chem_id < 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module_tag, source_file, fn_change_chemistry_profile, 0x271u, msg_chem_id);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(FG_LOG_CODE(4, 0), msg_chem_id_short, msg_chem_id_short);
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, fn_change_chemistry_profile, 0x272u, msg_chem_before, chem_id);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(FG_LOG_CODE(4, 1), msg_chem_before_short, msg_chem_before_short, chem_id);
    ret = bq27427_set_cfgupdate();
    if (ret != 0)
        return ret;
    (void)bq27427_execute_control_word((uint8_t)BQ27427_CTRL_CHEM_B);
    g2_delay_ms_4910f4(1u);
    ret = bq27427_soft_reset();
    if (ret != 0)
        return ret;
    (void)bq27427_i2c_write_reg(BQ27427_CMD_CONTROL, BQ27427_CTRL_CHEM_ID, 0u);
    chem_id = bq27427_i2c_read_reg(BQ27427_CMD_CONTROL, 0u);
    if (chem_id < 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module_tag, source_file, fn_change_chemistry_profile, 0x281u, msg_chem_id);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(FG_LOG_CODE(4, 0), msg_chem_id_short, msg_chem_id_short);
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, fn_change_chemistry_profile, 0x282u, msg_chem_after, chem_id);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(FG_LOG_CODE(4, 1), msg_chem_after_short, msg_chem_after_short, chem_id);
    (void)bq27427_seal();
    return 0;
}

/* Battery parameters are a local initialiser (stock copies them from ROM
 * 0x78a8bc): design energy 240, design capacity 80, terminate voltage 3100. */
void bq27427_settings(void) {
    g2_bq27427_params_t params = { 240, 80, 3100 };

    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, fn_settings, 0x28du, msg_settings,
                           params.efd, params.cfd, params.vmd);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(FG_LOG_CODE(4, 3), msg_settings_short, msg_settings_short,
                                  params.efd, params.cfd, params.vmd);
    if (params.efd >= 37628) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module_tag, source_file, fn_settings, 0x28fu, msg_bad_efd, params.efd);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(FG_LOG_CODE(4, 1), msg_bad_efd_short, msg_bad_efd_short, params.efd);
    } else if (params.cfd >= 8001) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module_tag, source_file, fn_settings, 0x294u, msg_bad_cfd, params.cfd);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(FG_LOG_CODE(4, 1), msg_bad_cfd_short, msg_bad_cfd_short, params.cfd);
    } else if ((uint32_t)(params.vmd - 2500) >= 1201u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module_tag, source_file, fn_settings, 0x299u, msg_bad_vmd, params.vmd);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(FG_LOG_CODE(4, 1), msg_bad_vmd_short, msg_bad_vmd_short, params.vmd);
    } else {
        bq27427_configure_from_params(&params);
        (void)bq27427_change_chemistry_profile();
    }
}

/* Flags() of 0 or with low byte 0xff is treated as an absent gauge. All 15
 * standard reads run, but only SOC, voltage, average current and the
 * temperature are published. */
int32_t bq27427_status_update(void) {
    int32_t flags = bq27427_read_flags();
    int32_t soc;
    int32_t temp;
    int32_t mv;
    int32_t ai;

    if (flags == 0 || (flags & 0xff) == 0xff) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module_tag, source_file, fn_status_update, 0x2a9u, msg_flag_error);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(FG_LOG_CODE(4, 0), msg_flag_error_short, msg_flag_error_short);
        return -1;
    }
    if (flags >= 0) {
        soc = bq27427_read_soc();
        temp = bq27427_read_temperature();
        mv = bq27427_read_battery_voltage();
        (void)bq27427_read_nom_capacity();
        (void)bq27427_read_avail_capacity();
        (void)bq27427_read_rem_capacity();
        (void)bq27427_read_full_capacity();
        ai = bq27427_read_ai();
        (void)bq27427_read_ap();
        (void)bq27427_read_int_temp();
        (void)bq27427_read_rem_cap_unfl();
        (void)bq27427_read_rem_cap_fil();
        (void)bq27427_read_full_cap_unfl();
        (void)bq27427_read_full_cap_fil();
        (void)bq27427_read_soc_unfl();
        g2_charger_telemetry.soc = soc;
        g2_charger_telemetry.voltage_mv = mv;
        g2_charger_telemetry.avg_current_ma = ai;
        g2_charger_telemetry.temperature = temp * 10;
    }
    return 0;
}

int32_t bq27427_init_wrapper(void) {
    (void)bq27427_status_update();
    return 0;
}

int32_t DRV_Bq27427HwInit(void) {
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, fn_hw_init, 0x2f0u, msg_init_start);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(FG_LOG_CODE(4, 0), msg_init_start_short, msg_init_start_short);
    bq27427_settings();
    if (bq27427_status_update() != 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module_tag, source_file, fn_hw_init, 0x2f3u, msg_init_failure);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(FG_LOG_CODE(4, 0), msg_init_failure_short, msg_init_failure_short);
        return -1;
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, fn_hw_init, 0x2f7u, msg_init_done);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(FG_LOG_CODE(4, 0), msg_init_done_short, msg_init_done_short);
    return 0;
}
