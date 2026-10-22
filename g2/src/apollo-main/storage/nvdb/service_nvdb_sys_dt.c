/* NVDB system-data record and OTP serial number, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\flashDB\NV\service_nvdb_sys_dt.c.
 * Native 0x4aee28..0x4b0309 (SVC_NvdbGetSysData 0x4af73a is anchored in
 * drivers/display/display-driver/display_driver_ratio_cell.c); literal pools
 * 0x4af880..0x4af8cf, 0x4afbb8, 0x4afc0c, 0x4afc64, 0x4afca4..0x4afcdb,
 * 0x4aff54..0x4affbf, 0x4b030c..0x4b03df.
 *
 * Record "nvSysDt" (172 bytes, version 2) lives at RAM 0x20003994; see
 * g2_nvdb_sys_dt_t. PSN layout (14 chars): [0..3] project code, [4]
 * manufacturer ('L' = LianHeGuangDian), [5] colour, [6] year letter
 * ('A' = 2024), [7] month letter ('A' = 1), [8..9] day, [10..13] serial.
 *
 * OTP keeps up to eight PSN slots of 16 bytes at OTP offset 0x340..0x3bf.
 * A slot is valid when it starts with "S2" and bytes 8..13 are digits; the
 * last valid slot wins and a new PSN goes to the slot after it. */
#include <stdint.h>
#include "nvdb_internal.h"

extern uint8_t display_driver_ratio_cells_20003994[0xac]; /* RAM 0x20003994 nvSysDt */
#define SYS_DT ((g2_nvdb_sys_dt_t *)(void *)display_driver_ratio_cells_20003994)

extern char g2_otp_psn[15];            /* RAM 0x20073ee4 g_OTP_PSN */
extern char g2_nvdb_month_text[];      /* RAM 0x200740b0 */
extern volatile uint8_t g2_nvdb_legacy_psn_flag; /* RAM 0x2007501a */

extern uint8_t *display_driver_brightness_ratio_cell_4af73a(uint32_t index); /* SVC_NvdbGetSysData */
extern uint32_t g2_log_module_length(const char *);                           /* strlen 0x44a43c */
extern int32_t audio_l2c_strncmp(const char *, const char *, uint32_t);        /* 0x44b610 */
extern void *audio_settings_copy_text(void *, const void *, uint32_t);         /* strncpy 0x44b5a0 */
extern int32_t audio_ble_format_to_buffer(char *, const char *, ...);          /* sprintf 0x4b4728 */
extern void *audio_uart_display_area_copy_439c04(void *, const void *, uint32_t); /* memcpy */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill);    /* memclr 0x48949c */
extern void aeabi_memset_43c0e4(void *dst, uint32_t len, uint32_t value);
extern uint32_t audio_power_peripheral_on(uint32_t peripheral);  /* 0x47f5b8 */
extern uint32_t audio_power_peripheral_off(uint32_t peripheral); /* 0x47f7ae */
extern int32_t osDelay(uint32_t ticks);                           /* 0x449376 */
extern uint32_t am_hal_otp_read_word_51381a(uint32_t offset, uint32_t *value);
extern uint32_t am_hal_otp_write_word_513850(uint32_t offset, uint32_t value);
extern int32_t isdigit_5137b8(int32_t c);

#define OTP_PSN_BASE 0x340u
#define OTP_PSN_SLOTS 8
#define PERIPH_OTP_A 0x1du
#define PERIPH_OTP_B 0x17u

static const char module_tag[] = "nv.sysDt"; /* ROM 0x78c02c */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\flashDB\\NV\\service_nvdb_sys_dt.c"; /* ROM 0x6e4fe0 */
static const char key_sys_dt[] = "nvSysDt"; /* ROM 0x78e63c */
static const char update_fn[] = "_nvdbUpdataSysDt"; /* ROM 0x783488 */
static const char write_fn[] = "SVC_NvdbWriteSysData"; /* ROM 0x77bb6c */
static const char read_fn[] = "SVC_NvdbReadSysData"; /* ROM 0x783500 */
static const char parse_fn[] = "SVC_NvdbparsePsn"; /* ROM 0x783514 */
static const char otp_read_fn[] = "SVC_ReadPSNFromOTP"; /* ROM 0x78358c */
static const char otp_write_fn[] = "SVC_WritePSNToOTP"; /* ROM 0x7835a0 */
static const char sn_prefix[] = "S2"; /* ROM 0x4aff54 and 0x4b030c */
static const char month_fmt[] = "%d"; /* ROM 0x4afcb4 */
static const char manufacturer_lhgd[] = "LianHeGuangDian"; /* ROM 0x788c60 */
static const char unknown_text[] = "unknow"; /* ROM 0x78e64c */

static const char debug_only[] = "!!This is only for program debugging"; /* ROM 0x74e114 */
static const char debug_only_short[] = "[nv.sysDt]!!This is only for program debugging"; /* ROM 0x738624 */
static const char otp_ok[] = "read SN from OTP success, g_OTP_PSN: %s, g_NVSysDt.record_PSN: %s"; /* ROM 0x705af0 */
static const char otp_ok_short[] =
    "[nv.sysDt]read SN from OTP success, g_OTP_PSN: %s, g_NVSysDt.record_PSN: %s"; /* ROM 0x6f5ef4 */
static const char otp_fail[] = "read SN from OTP failed"; /* ROM 0x77bb3c */
static const char otp_fail_short[] = "[nv.sysDt]read SN from OTP failed"; /* ROM 0x759c84 */
static const char version_fmt[] = "version %d(%d)"; /* ROM 0x788c40 */
static const char version_short[] = "[nv.sysDt]version %d(%d)"; /* ROM 0x771460 */
static const char crc_fmt[] = "crc 0x%x(0x%x)"; /* ROM 0x788c50 */
static const char crc_short[] = "[nv.sysDt]crc 0x%x(0x%x)"; /* ROM 0x77147c */
static const char lux_base_fmt[] = "lux_base %d"; /* ROM 0x78c038 */
static const char lux_base_short[] = "[nv.sysDt]lux_base %d"; /* ROM 0x77bb54 */
static const char canvas_fmt[] = "canvas_x %d, canvas_y %d"; /* ROM 0x771498 */
static const char canvas_short[] = "[nv.sysDt]canvas_x %d, canvas_y %d"; /* ROM 0x759ca8 */
static const char panel_fmt[] = "panel_current %d"; /* ROM 0x78349c */
static const char panel_short[] = "[nv.sysDt]panel_current %d"; /* ROM 0x7714b4 */
static const char sn_fmt[] = "SN: %s\n"; /* ROM 0x78e644 */
static const char sn_short[] = "[nv.sysDt]SN: %s\n"; /* ROM 0x7834b0 */
static const char bsn_fmt[] = "BSN: %s\n"; /* ROM 0x78c044 */
static const char bsn_short[] = "[nv.sysDt]BSN: %s\n"; /* ROM 0x7834c4 */
static const char lux_fmt[] = "LUX: %d\n"; /* ROM 0x78c050 */
static const char lux_short[] = "[nv.sysDt]LUX: %d\n"; /* ROM 0x7834d8 */
static const char canvas_x_fmt[] = "canvas_x %d"; /* ROM 0x78c05c */
static const char canvas_x_short[] = "[nv.sysDt]canvas_x %d"; /* ROM 0x77bb84 */
static const char canvas_y_fmt[] = "canvas_y %d"; /* ROM 0x78c068 */
static const char canvas_y_short[] = "[nv.sysDt]canvas_y %d"; /* ROM 0x77bb9c */
static const char aging_start_fmt[] = "aging_start_time %d-%d-%d %d:%d:%d"; /* ROM 0x759ccc */
static const char aging_start_short[] = "[nv.sysDt]aging_start_time %d-%d-%d %d:%d:%d"; /* ROM 0x738654 */
static const char aging_end_fmt[] = "aging_end_time %d-%d-%d %d:%d:%d"; /* ROM 0x759cf0 */
static const char aging_end_short[] = "[nv.sysDt]aging_end_time %d-%d-%d %d:%d:%d"; /* ROM 0x743468 */
static const char aging_soc_fmt[] = "aging_soc_to_10_time %d-%d-%d %d:%d:%d"; /* ROM 0x74e13c */
static const char aging_soc_short[] = "[nv.sysDt]aging_soc_to_10_time %d-%d-%d %d:%d:%d"; /* ROM 0x72d6f4 */
static const char wrong_touch_fmt[] = "aging_wrong_touch_times %d"; /* ROM 0x7714d0 */
static const char wrong_touch_short[] = "[nv.sysDt]aging_wrong_touch_times %d"; /* ROM 0x74e164 */
static const char begin_soc_fmt[] = "aging_begin_charge_soc %d"; /* ROM 0x7714ec */
static const char begin_soc_short[] = "[nv.sysDt]aging_begin_charge_soc %d"; /* ROM 0x759d14 */
static const char total_fmt[] = "aging_total_times %d"; /* ROM 0x77bbb4 */
static const char total_short[] = "[nv.sysDt]aging_total_times %d"; /* ROM 0x7650d0 */
static const char finish_fmt[] = "aging_finish_flag %d"; /* ROM 0x77bbcc */
static const char finish_short[] = "[nv.sysDt]aging_finish_flag %d"; /* ROM 0x7650f0 */
static const char unknown_idx[] = "Unknown nv dataIdx\n"; /* ROM 0x7834ec */
static const char unknown_idx_short[] = "[nv.sysDt]Unknown nv dataIdx\n"; /* ROM 0x765110 */
static const char too_short[] = "length too short\n"; /* ROM 0x783528 */
static const char too_short_short[] = "[nv.sysDt]length too short\n"; /* ROM 0x771508 */
static const char project_fmt[] = " projectCode: %s"; /* ROM 0x78353c */
static const char project_short[] = "[nv.sysDt] projectCode: %s"; /* ROM 0x771524 */
static const char manufacturer_fmt[] = "manufacturer: %c (%s)"; /* ROM 0x77bbe4 */
static const char manufacturer_short[] = "[nv.sysDt]manufacturer: %c (%s)"; /* ROM 0x765130 */
static const char color_fmt[] = "       color: %c"; /* ROM 0x783550 */
static const char color_short[] = "[nv.sysDt]       color: %c"; /* ROM 0x771540 */
static const char year_fmt[] = "        year: %c (%d)"; /* ROM 0x77bbfc */
static const char year_short[] = "[nv.sysDt]        year: %c (%d)"; /* ROM 0x765150 */
static const char month_fmt_log[] = "       month: %c (%s)"; /* ROM 0x77bc14 */
static const char month_short[] = "[nv.sysDt]       month: %c (%s)"; /* ROM 0x765170 */
static const char day_fmt[] = "         day: %s"; /* ROM 0x783564 */
static const char day_short[] = "[nv.sysDt]         day: %s"; /* ROM 0x77155c */
static const char serial_fmt[] = "serialNumber: %s"; /* ROM 0x783578 */
static const char serial_short[] = "[nv.sysDt]serialNumber: %s"; /* ROM 0x771578 */
static const char found_fmt[] = "Found valid SN[%d] at offset 0x%X: %s"; /* ROM 0x74e18c */
static const char found_short[] = "[nv.sysDt]Found valid SN[%d] at offset 0x%X: %s"; /* ROM 0x738684 */
static const char read_fail_fmt[] = "Failed to read SN[%d] from OTP at offset 0x%X, status: 0x%X\n"; /* ROM 0x70eee4 */
static const char read_fail_short[] =
    "[nv.sysDt]Failed to read SN[%d] from OTP at offset 0x%X, status: 0x%X\n"; /* ROM 0x6fd07c */
static const char read_last_fmt[] = "Successfully read last valid SN[%d] from OTP: %s"; /* ROM 0x72d728 */
static const char read_last_short[] = "[nv.sysDt]Successfully read last valid SN[%d] from OTP: %s"; /* ROM 0x718694 */
static const char none_fmt[] = "No valid SN found in OTP"; /* ROM 0x771594 */
static const char none_short[] = "[nv.sysDt]No valid SN found in OTP"; /* ROM 0x759d38 */
static const char null_fmt[] = "Invalid parameter: pSN is NULL"; /* ROM 0x765190 */
static const char null_short[] = "[nv.sysDt]Invalid parameter: pSN is NULL"; /* ROM 0x743494 */
static const char format_fmt[] = "Invalid SN format: %s"; /* ROM 0x77bc2c */
static const char format_short[] = "[nv.sysDt]Invalid SN format: %s"; /* ROM 0x7651b0 */
static const char exists_fmt[] = "SN already exists in OTP[%d], no need to write: %s"; /* ROM 0x72d75c */
static const char exists_short[] = "[nv.sysDt]SN already exists in OTP[%d], no need to write: %s"; /* ROM 0x70ef24 */
static const char differ_fmt[] =
    "Current SN[%d]: %s, different from new SN: %s, will write to position[%d]"; /* ROM 0x6f5f40 */
static const char differ_short[] =
    "[nv.sysDt]Current SN[%d]: %s, different from new SN: %s, will write to position[%d]"; /* ROM 0x6e9e8c */
static const char first_fmt[] = "No valid SN found in OTP, will write to position[0]"; /* ROM 0x72d790 */
static const char first_short[] = "[nv.sysDt]No valid SN found in OTP, will write to position[0]"; /* ROM 0x70ef64 */
static const char full_fmt[] = "OTP SN storage is full (max 8 positions), cannot write new SN"; /* ROM 0x70efa4 */
static const char full_short[] =
    "[nv.sysDt]OTP SN storage is full (max 8 positions), cannot write new SN"; /* ROM 0x6fd0c4 */
static const char write_fail_fmt[] = "Failed to write SN to OTP at offset 0x%X, status: 0x%X"; /* ROM 0x722e40 */
static const char write_fail_short[] =
    "[nv.sysDt]Failed to write SN to OTP at offset 0x%X, status: 0x%X"; /* ROM 0x705b34 */
static const char wrote_fmt[] = "Successfully wrote SN to OTP[%d] at offset 0x%X: %s"; /* ROM 0x72d7c4 */
static const char wrote_short[] = "[nv.sysDt]Successfully wrote SN to OTP[%d] at offset 0x%X: %s"; /* ROM 0x70efe4 */

/* ROM 0x6d3358: pointer table of 40 early-production PSNs (strings 0x788c70..0x788ee0). */
static const char *const legacy_psn[40] = {
    "S200LABI270028", "S200LABI270036", "S200LABI270050", "S200LDBE210004",
    "S200LABI260010", "S200LABI270068", "S200LABI270066", "S200LABI270004",
    "S200LABI270072", "S200LABI260003", "S200LABI250030", "S200LABI260024",
    "S200LABI260026", "S200LABI260021", "S200LABI270029", "S200LABI270058",
    "S200LABI270022", "S200LABI270073", "S200LABI250002", "S200LABI270071",
    "S200LABI270001", "S200LABI270012", "S200LABI260014", "S200LABI270027",
    "S200LABI270069", "S200LABI260009", "S200LABI270008", "S200LABI270060",
    "S200LABI270053", "S200LABI250023", "S200LABI270043", "S200LABG190017",
    "S200LCBI190019", "S200LCBI200013", "S200LABI270031", "S200LCBI200010",
    "S200LCBI200008", "S200LCBI190022", "S200LCBI200001", "S200LCBI190025",
};

#define LOG(...) NVDB_LOG(module_tag, source_file, __VA_ARGS__)

int32_t nvdbSysDtDefaultInitialize(void)
{
    SYS_DT->crc = audio_uart_hand_checksum_49acd4(SYS_DT, 0x26u, NULL);
    return 0;
}

/* Logs the stored record, reconciles the RAM PSN with OTP, and writes the
 * RAM record back when the key is missing or an older blob's CRC differs. */
int32_t _nvdbUpdataSysDt(void)
{
    g2_nvdb_sys_dt_t stored;
    g2_nvdb_sys_dt_t *rec = SYS_DT;
    LOG(2u, update_fn, 0x42u, 0x08000000u, debug_only, debug_only_short);
    rec->psn[14] = '\0';
    SVC_NvdbparsePsn(rec->psn);
    int32_t length = SVC_NvdbRead(key_sys_dt, &stored, 0xacu);
    nvdbSysDtMarkLegacyPsn();
    if (SVC_ReadPSNFromOTP(g2_otp_psn, NULL) == 0) {
        LOG(3u, update_fn, 0x49u, 0x0c800000u, otp_ok, otp_ok_short, g2_otp_psn, rec->psn);
        audio_uart_checksum_copy(rec->psn, g2_otp_psn, 14u);
        rec->psn[14] = '\0';
    } else {
        LOG(1u, update_fn, 0x4fu, 0x04000000u, otp_fail, otp_fail_short);
    }
    if (length > 0) {
        LOG(3u, update_fn, 0x52u, 0x0c800000u, version_fmt, version_short,
            (uint32_t)stored.version, 2u);
        LOG(3u, update_fn, 0x53u, 0x0c800000u, crc_fmt, crc_short,
            (uint32_t)stored.crc, (uint32_t)rec->crc);
        LOG(3u, update_fn, 0x54u, 0x0c400000u, lux_base_fmt, lux_base_short, stored.lux_base);
        LOG(3u, update_fn, 0x55u, 0x0c800000u, canvas_fmt, canvas_short,
            (uint32_t)stored.canvas_x, (uint32_t)stored.canvas_y);
        LOG(3u, update_fn, 0x56u, 0x0c400000u, panel_fmt, panel_short, (uint32_t)stored.panel_current);
        if (stored.crc != rec->crc && stored.version < 2u)
            (void)SVC_NvdbWriteSysData(G2_NVDB_SYSDT_PSN, rec->psn);
        return 0;
    }
    (void)SVC_NvdbWriteSysData(G2_NVDB_SYSDT_PSN, rec->psn);
    return 0;
}

/* Updates one field (or the whole record for index 13) and rewrites the blob.
 * Returns the blob-write status, or 0 when nothing was written. */
int32_t SVC_NvdbWriteSysData(uint8_t data_index, const void *value)
{
    g2_nvdb_sys_dt_t *rec = SYS_DT;
    const uint8_t *byte = (const uint8_t *)value;
    const uint32_t *word = (const uint32_t *)value;
    bool changed = false;
    int32_t result = 0;
    uint8_t length;

    switch (data_index) {
    case G2_NVDB_SYSDT_PSN:
        if (value != NULL) {
            LOG(4u, write_fn, 0x6cu, 0x10400000u, sn_fmt, sn_short, (const char *)value);
            if (g2_log_module_length((const char *)value) < 15u)
                length = (uint8_t)g2_log_module_length((const char *)value);
            else
                length = 14u;
            audio_uart_checksum_copy(rec->psn, value, length);
            rec->psn[length] = '\0';
            changed = true;
        }
        break;
    case G2_NVDB_SYSDT_BSN:
        if (value != NULL) {
            LOG(4u, write_fn, 0x79u, 0x10400000u, bsn_fmt, bsn_short, (const char *)value);
            if (g2_log_module_length((const char *)value) < 22u)
                length = (uint8_t)g2_log_module_length((const char *)value);
            else
                length = 21u;
            audio_uart_checksum_copy(rec->bsn, value, length);
            rec->bsn[length] = '\0';
            changed = true;
        }
        break;
    case G2_NVDB_SYSDT_LUX:
        if (value != NULL) {
            LOG(4u, write_fn, 0x85u, 0x10400000u, lux_fmt, lux_short, word[0]);
            rec->lux_base = word[0];
            changed = true;
        }
        break;
    case G2_NVDB_SYSDT_CANVAS_X:
        if (value != NULL) {
            LOG(4u, write_fn, 0x8fu, 0x10400000u, canvas_x_fmt, canvas_x_short, (uint32_t)byte[0]);
            rec->canvas_x = byte[0];
            changed = true;
        }
        break;
    case G2_NVDB_SYSDT_CANVAS_Y:
        if (value != NULL) {
            LOG(4u, write_fn, 0x99u, 0x10400000u, canvas_y_fmt, canvas_y_short, (uint32_t)byte[0]);
            rec->canvas_y = byte[0];
            changed = true;
        }
        break;
    case G2_NVDB_SYSDT_PANEL_CURRENT:
        if (value != NULL) {
            LOG(4u, write_fn, 0xa3u, 0x10400000u, panel_fmt, panel_short, (uint32_t)byte[0]);
            rec->panel_current = byte[0];
            changed = true;
        }
        break;
    case G2_NVDB_SYSDT_AGING_START:
        if (value != NULL) {
            LOG(4u, write_fn, 0xadu, 0x11800000u, aging_start_fmt, aging_start_short,
                word[3], word[4], word[5], word[6], word[7], word[8]);
            (void)audio_uart_display_area_copy_439c04(&rec->aging_start, value, 0x28u);
            changed = true;
        }
        break;
    case G2_NVDB_SYSDT_AGING_END:
        if (value != NULL) {
            LOG(4u, write_fn, 0xb7u, 0x11800000u, aging_end_fmt, aging_end_short,
                word[3], word[4], word[5], word[6], word[7], word[8]);
            (void)audio_uart_display_area_copy_439c04(&rec->aging_end, value, 0x28u);
            changed = true;
        }
        break;
    case G2_NVDB_SYSDT_AGING_SOC_TO_10:
        if (value != NULL) {
            LOG(4u, write_fn, 0xc0u, 0x11800000u, aging_soc_fmt, aging_soc_short,
                word[3], word[4], word[5], word[6], word[7], word[8]);
            (void)audio_uart_display_area_copy_439c04(&rec->aging_soc_to_10, value, 0x28u);
            changed = true;
        }
        break;
    case G2_NVDB_SYSDT_AGING_WRONG_TOUCH:
        if (value != NULL) {
            LOG(4u, write_fn, 0xc9u, 0x10400000u, wrong_touch_fmt, wrong_touch_short, (uint32_t)byte[0]);
            rec->aging_wrong_touch_times = byte[0];
            changed = true;
        }
        break;
    case G2_NVDB_SYSDT_AGING_BEGIN_SOC:
        if (value != NULL) {
            LOG(4u, write_fn, 0xd2u, 0x10400000u, begin_soc_fmt, begin_soc_short, (uint32_t)byte[0]);
            rec->aging_begin_charge_soc = byte[0];
            changed = true;
        }
        break;
    case G2_NVDB_SYSDT_AGING_TOTAL:
        if (value != NULL) {
            LOG(4u, write_fn, 0xe3u, 0x10400000u, total_fmt, total_short, (uint32_t)byte[0]);
            rec->aging_total_times = byte[0];
            changed = true;
        }
        break;
    case G2_NVDB_SYSDT_AGING_FINISH:
        if (value != NULL) {
            LOG(4u, write_fn, 0xecu, 0x10400000u, finish_fmt, finish_short, (uint32_t)byte[0]);
            rec->aging_finish_flag = byte[0];
            changed = true;
        }
        break;
    case G2_NVDB_SYSDT_RECORD:
        changed = value != NULL;
        if (changed)
            audio_uart_checksum_copy(rec, value, 0xacu);
        break;
    default:
        LOG(2u, write_fn, 0xf2u, 0x08000000u, unknown_idx, unknown_idx_short);
        changed = false;
        break;
    }
    if (changed) {
        rec->version = 2u;
        rec->crc = audio_uart_hand_checksum_49acd4(rec, 0x26u, NULL);
        result = SVC_NvdbWrite(key_sys_dt, rec, 0xacu);
    }
    return result;
}

/* Reloads the RAM record from flash, overrides the PSN from OTP, then returns
 * the SVC_NvdbGetSysData field pointer. */
uint8_t *SVC_NvdbReadSysData(uint8_t data_index)
{
    g2_nvdb_sys_dt_t *rec = SYS_DT;
    (void)SVC_NvdbRead(key_sys_dt, rec, 0xacu);
    nvdbSysDtMarkLegacyPsn();
    if (SVC_ReadPSNFromOTP(g2_otp_psn, NULL) == 0) {
        LOG(3u, read_fn, 0x137u, 0x0c800000u, otp_ok, otp_ok_short, g2_otp_psn, rec->psn);
        audio_uart_checksum_copy(rec->psn, g2_otp_psn, 14u);
        rec->psn[14] = '\0';
    } else {
        LOG(1u, read_fn, 0x13du, 0x04000000u, otp_fail, otp_fail_short);
    }
    return display_driver_brightness_ratio_cell_4af73a(data_index);
}

void SVC_NvdbparsePsn(const char *psn)
{
    char day[3];
    char serial[5];
    char project[5];

    if (g2_log_module_length(psn) < 14u) {
        LOG(4u, parse_fn, 0x151u, 0x10000000u, too_short, too_short_short);
        return;
    }
    (void)audio_settings_copy_text(project, psn, 4u);
    project[4] = '\0';
    char manufacturer = psn[4];
    char color = psn[5];
    char year = psn[6];
    char month = psn[7];
    (void)audio_settings_copy_text(day, psn + 8, 2u);
    day[2] = '\0';
    (void)audio_settings_copy_text(serial, psn + 10, 4u);
    serial[4] = '\0';
    const char *manufacturer_name = nvdbSysDtManufacturerName(manufacturer);
    int32_t year_value = nvdbSysDtYear((uint8_t)year);
    const char *month_text = nvdbSysDtMonth((uint8_t)month);
    LOG(4u, parse_fn, 0x16bu, 0x10400000u, project_fmt, project_short, project);
    LOG(4u, parse_fn, 0x16cu, 0x10800000u, manufacturer_fmt, manufacturer_short,
        (uint32_t)(uint8_t)manufacturer, manufacturer_name);
    LOG(4u, parse_fn, 0x16du, 0x10400000u, color_fmt, color_short, (uint32_t)(uint8_t)color);
    LOG(4u, parse_fn, 0x16eu, 0x10800000u, year_fmt, year_short, (uint32_t)(uint8_t)year, year_value);
    LOG(4u, parse_fn, 0x16fu, 0x10800000u, month_fmt_log, month_short,
        (uint32_t)(uint8_t)month, month_text);
    LOG(4u, parse_fn, 0x170u, 0x10400000u, day_fmt, day_short, day);
    LOG(4u, parse_fn, 0x171u, 0x10400000u, serial_fmt, serial_short, serial);
}

const char *nvdbSysDtManufacturerName(char code)
{
    const char *name = unknown_text;
    if (code == 'L')
        name = manufacturer_lhgd;
    return name;
}

/* 'A'..'Z' -> 2024..2049. */
int32_t nvdbSysDtYear(uint8_t code)
{
    if ((uint32_t)code - 0x41u < 26u)
        return (int32_t)code + 0x7a7;
    return 0;
}

/* 'A'..'Z' -> "1".."26" formatted into a shared RAM buffer. */
const char *nvdbSysDtMonth(uint8_t code)
{
    const char *text = unknown_text;
    if ((uint32_t)code - 0x41u < 26u) {
        (void)audio_ble_format_to_buffer(g2_nvdb_month_text, month_fmt, (int32_t)code - 0x40);
        text = g2_nvdb_month_text;
    }
    return text;
}

/* Clears the three aging timestamps and two counters (total_times is kept),
 * then persists through dataIdx 10. */
void nvdbSysDtResetAging(void)
{
    uint8_t zero[0x28];
    g2_nvdb_sys_dt_t *rec = SYS_DT;
    audio_uart_buffer_zero(zero, 0x28u, 0u);
    (void)audio_uart_display_area_copy_439c04(&rec->aging_start, zero, 0x28u);
    (void)audio_uart_display_area_copy_439c04(&rec->aging_end, zero, 0x28u);
    (void)audio_uart_display_area_copy_439c04(&rec->aging_soc_to_10, zero, 0x28u);
    rec->aging_wrong_touch_times = 0u;
    rec->aging_begin_charge_soc = 0u;
    rec->aging_finish_flag = 0u;
    (void)SVC_NvdbWriteSysData(G2_NVDB_SYSDT_AGING_BEGIN_SOC, &rec->aging_begin_charge_soc);
}

/* Sets the legacy flag when the RAM PSN is one of the 40 listed units. */
void nvdbSysDtMarkLegacyPsn(void)
{
    const char *table[40];
    (void)audio_uart_display_area_copy_439c04(table, legacy_psn, sizeof table);
    for (uint32_t i = 0; i < 40u; i++) {
        if (audio_l2c_strncmp(SYS_DT->psn, table[i], 15u) == 0) {
            g2_nvdb_legacy_psn_flag = 1u;
            return;
        }
    }
}

int32_t SVC_ReadPSNFromOTP(char *psn, int32_t *slot)
{
    uint32_t base = OTP_PSN_BASE;
    uint32_t words[4];
    char candidate[15];
    int32_t found = -1;

    aeabi_memset_43c0e4(words, 16u, 0u);
    aeabi_memset_43c0e4(candidate, 15u, 0u);
    (void)audio_power_peripheral_on(PERIPH_OTP_A);
    (void)audio_power_peripheral_on(PERIPH_OTP_B);
    (void)osDelay(1u);
    for (int32_t index = 0; index < OTP_PSN_SLOTS; index++) {
        uint32_t offset = base + (uint32_t)index * 16u;
        bool ok = true;
        aeabi_memset_43c0e4(words, 16u, 0u);
        for (int32_t w = 0; w < 4; w++) {
            uint32_t status = am_hal_otp_read_word_51381a(offset + (uint32_t)w * 4u, &words[w]);
            if (status != 0u) {
                LOG(3u, otp_read_fn, 0x203u, 0x0cc00000u, read_fail_fmt, read_fail_short,
                    index, offset + (uint32_t)w * 4u, status);
                ok = false;
                break;
            }
        }
        if (!ok)
            break;
        audio_uart_checksum_copy(candidate, words, 14u);
        candidate[14] = '\0';
        if (audio_l2c_strncmp(candidate, sn_prefix, 2u) == 0 &&
            isdigit_5137b8(candidate[13]) && isdigit_5137b8(candidate[12]) &&
            isdigit_5137b8(candidate[11]) && isdigit_5137b8(candidate[10]) &&
            isdigit_5137b8(candidate[9]) && isdigit_5137b8(candidate[8])) {
            found = index;
            audio_uart_checksum_copy(psn, candidate, 14u);
            psn[14] = '\0';
            LOG(3u, otp_read_fn, 0x21cu, 0x0cc00000u, found_fmt, found_short, index, offset, psn);
        }
    }
    (void)audio_power_peripheral_off(PERIPH_OTP_B);
    (void)audio_power_peripheral_off(PERIPH_OTP_A);
    if (found < 0) {
        LOG(1u, otp_read_fn, 0x237u, 0x04000000u, none_fmt, none_short);
        return -1;
    }
    if (slot != NULL)
        *slot = found;
    LOG(3u, otp_read_fn, 0x232u, 0x0c800000u, read_last_fmt, read_last_short, found, psn);
    return 0;
}

int32_t SVC_WritePSNToOTP(const char *psn)
{
    uint32_t words[4];
    char current[16];
    int32_t slot = -1;
    int32_t position;

    aeabi_memset_43c0e4(words, 16u, 0u);
    aeabi_memset_43c0e4(current, 15u, 0u);
    if (psn == NULL) {
        LOG(1u, otp_write_fn, 0x24bu, 0x04000000u, null_fmt, null_short);
        return -1;
    }
    if (audio_l2c_strncmp(psn, sn_prefix, 2u) != 0 ||
        !isdigit_5137b8(psn[13]) || !isdigit_5137b8(psn[12]) ||
        !isdigit_5137b8(psn[11]) || !isdigit_5137b8(psn[10]) ||
        !isdigit_5137b8(psn[9]) || !isdigit_5137b8(psn[8])) {
        LOG(1u, otp_write_fn, 600u, 0x04400000u, format_fmt, format_short, psn);
        return -1;
    }
    if (SVC_ReadPSNFromOTP(current, &slot) == 0) {
        if (audio_l2c_strncmp(current, psn, 14u) == 0) {
            LOG(3u, otp_write_fn, 0x266u, 0x0c800000u, exists_fmt, exists_short, slot, psn);
            return 0;
        }
        position = slot + 1;
        LOG(3u, otp_write_fn, 0x26eu, 0x0d000000u, differ_fmt, differ_short,
            slot, current, psn, position);
    } else {
        position = 0;
        LOG(3u, otp_write_fn, 0x275u, 0x0c000000u, first_fmt, first_short);
    }
    if (position >= OTP_PSN_SLOTS) {
        LOG(1u, otp_write_fn, 0x27bu, 0x04000000u, full_fmt, full_short);
        return -1;
    }
    uint32_t offset = (uint32_t)position * 16u + OTP_PSN_BASE;
    (void)audio_power_peripheral_on(PERIPH_OTP_A);
    (void)audio_power_peripheral_on(PERIPH_OTP_B);
    (void)osDelay(1u);
    aeabi_memset_43c0e4(words, 16u, 0u);
    audio_uart_checksum_copy(words, psn, 14u);
    for (int32_t w = 0; w < 4; w++) {
        uint32_t status = am_hal_otp_write_word_513850(offset + (uint32_t)w * 4u, words[w]);
        if (status != 0u) {
            LOG(1u, otp_write_fn, 0x294u, 0x04800000u, write_fail_fmt, write_fail_short,
                offset + (uint32_t)w * 4u, status);
            (void)audio_power_peripheral_off(PERIPH_OTP_B);
            (void)audio_power_peripheral_off(PERIPH_OTP_A);
            return -1;
        }
    }
    LOG(3u, otp_write_fn, 0x2a0u, 0x0cc00000u, wrote_fmt, wrote_short, position, offset, psn);
    (void)audio_power_peripheral_off(PERIPH_OTP_B);
    (void)audio_power_peripheral_off(PERIPH_OTP_A);
    return 0;
}
