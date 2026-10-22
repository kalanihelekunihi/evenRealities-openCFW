/* Product-test command 0x20 get_lux_info (TSV label pt_cmd_1B_handler), stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\product_test\pt_protocol_procsr.c.
 * Native 0x57200c..0x572210 (literal pool to 0x57222b; 1e6 divisor at ROM 0x57238c).
 *
 * Reply 0x20 with 32 data bytes: the rounded raw OPT3007 lux (uint32 LE), 24
 * zero bytes, and the lux scaled by the factory calibration word
 * nvSysDt.lux_base (RAM 0x20003994 + 0x28): round(raw * lux_base / 1e6).
 * The handler uses double-precision VFP (IAR hard-float convention), so the
 * unit needs profile g2-apollo-main-20. */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include "g2_nvdb.h"

#define IAR_VFP __attribute__((pcs("aapcs-vfp")))
#define PT_LUX_CALIBRATION_SCALE 1000000.0 /* ROM 0x57238c */

extern uint8_t display_driver_ratio_cells_20003994[0xac]; /* RAM 0x20003994 nvSysDt */
#define SYS_DT ((const g2_nvdb_sys_dt_t *)(const void *)display_driver_ratio_cells_20003994)

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern IAR_VFP double pt_als_raw_lux_get_58f8e4(void);
extern IAR_VFP double iar_round_58f970(double x);

static const char module_tag[] = "pt_protocol_procsr"; /* ROM 0x7829fc */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\product_test\\pt_protocol_procsr.c"; /* ROM 0x6ef458 */
static const char para_null[] = "%s para is NULL\n"; /* ROM 0x782a74 */
static const char para_null_c[] = "[pt_protocol_procsr]%s para is NULL\n"; /* ROM 0x74d304 */

static int log_extended_on(void) { return (audio_log_flags() & 2u) != 0u; }
static int log_compressed_on(void) { return (audio_log_flags() & 1u) || (audio_log_flags() & 4u); }

uint32_t pt_cmd_1B_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "get_lux_info"; /* ROM 0x788480 */
    static const char join[] = "join in get_lux_info"; /* ROM 0x77ad74 */
    static const char join_c[] = "[pt_protocol_procsr]join in get_lux_info"; /* ROM 0x742154 */
    static const char raw_msg[] = "lux val is:%f"; /* ROM 0x788490 */
    static const char raw_msg_c[] = "[pt_protocol_procsr]lux val is:%f"; /* ROM 0x758b5c */
    static const char adj_msg[] = "after adjust lux val is:%f"; /* ROM 0x770580 */
    static const char adj_msg_c[] = "[pt_protocol_procsr]after adjust lux val is:%f"; /* ROM 0x7373c4 */
    uint32_t value;

    if (log_extended_on())
        audio_log_extended(3u, module_tag, source_file, fn, 0x712u, join);
    if (log_compressed_on())
        (void)compress_log_output(0x0c000000u, join_c, join_c);
    if (rsp == NULL || rsp_len == NULL || payload == NULL || length < 4u) {
        if (log_extended_on())
            audio_log_extended(1u, module_tag, source_file, fn, 0x715u, para_null, fn);
        if (log_compressed_on())
            (void)compress_log_output(0x04400000u, para_null_c, para_null_c, fn);
        return 0xffffffffu; /* -1 */
    }
    uint8_t idx = 0;
    rsp[idx++] = 0x20u;
    rsp[idx++] = 1u;
    rsp[idx++] = 3u;
    rsp[idx++] = 0x20u;

    double lux = pt_als_raw_lux_get_58f8e4();
    value = (uint32_t)iar_round_58f970(lux); /* VCVT.U32: negative (-1.0 = sensor off) saturates to 0 */
    if (log_extended_on())
        audio_log_extended(3u, module_tag, source_file, fn, 0x723u, raw_msg, lux);
    if (log_compressed_on())
        (void)compress_log_output(0x0c400000u, raw_msg_c, raw_msg_c, lux);
    for (uint32_t i = 0; i < 4u; i++)
        rsp[idx++] = ((const uint8_t *)&value)[i];
    for (int i = 0; i < 0x18; i++)
        rsp[idx++] = 0u;

    double adjusted = (double)(int32_t)SYS_DT->lux_base * lux / PT_LUX_CALIBRATION_SCALE;
    value = (uint32_t)iar_round_58f970(adjusted);
    if (log_extended_on())
        audio_log_extended(3u, module_tag, source_file, fn, 0x732u, adj_msg, adjusted);
    if (log_compressed_on())
        (void)compress_log_output(0x0c400000u, adj_msg_c, adj_msg_c, adjusted);
    for (uint32_t i = 0; i < 4u; i++)
        rsp[idx++] = ((const uint8_t *)&value)[i];
    *rsp_len = idx;
    return 0;
}
