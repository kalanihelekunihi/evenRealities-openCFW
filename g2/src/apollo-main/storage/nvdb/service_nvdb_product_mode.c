/* NVDB product-mode record, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\flashDB\NV\service_nvdb_product_mode.c.
 * Native 0x4abd90..0x4abe9d; literal pool 0x4abea0..0x4abec7.
 * productModeGet (0x4abe60) is anchored in system/glue/simple_ram_getters.c.
 *
 * Record "nvProdMode" (4 bytes): version 1, mode byte, CRC16 over 2 bytes.
 * The live copy is RAM 0x200038f0 (g2_uart_product_mode_state, whose current
 * definition only reserves the first 2 bytes). */
#include <stdint.h>
#include "nvdb_internal.h"

extern volatile uint8_t g2_uart_product_mode_state[]; /* RAM 0x200038f0 */
#define PROD_MODE ((g2_nvdb_product_mode_t *)(uintptr_t)g2_uart_product_mode_state)

static const char module_tag[] = "nv.productMode"; /* ROM 0x788c10 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\flashDB\\NV\\service_nvdb_product_mode.c"; /* ROM 0x6e18dc */
static const char key_prod_mode[] = "nvProdMode"; /* ROM 0x78c008 */
static const char update_fn[] = "_nvdbUpdataProdMd"; /* ROM 0x783460 */
static const char set_fn[] = "set_product_mode"; /* ROM 0x783474 */
static const char debug_only[] = "!!This is only for program debugging"; /* ROM 0x74e09c */
static const char debug_only_short[] = "[nv.productMode]!!This is only for program debugging"; /* ROM 0x722dd0 */
static const char set_mode_fmt[] = "set product mode is %d\n"; /* ROM 0x77bb0c */
static const char set_mode_short[] = "[nv.productMode]set product mode is %d\n"; /* ROM 0x74e0c4 */

#define LOG(...) NVDB_LOG(module_tag, source_file, __VA_ARGS__)

int32_t productModeDefaultCrcInitialize(void)
{
    g2_nvdb_product_mode_t *rec = PROD_MODE;
    rec->crc = audio_uart_hand_checksum_49acd4(rec, 2u, NULL);
    return 0;
}

/* Rewrites the default when the key is missing, or when a version-0 blob
 * carries a CRC different from the RAM default's. */
int32_t _nvdbUpdataProdMd(void)
{
    g2_nvdb_product_mode_t stored;
    LOG(2u, update_fn, 0x2eu, 0x08000000u, debug_only, debug_only_short);
    if (SVC_NvdbRead(key_prod_mode, &stored, 4u) < 1)
        productModeUpdate(PROD_MODE->mode);
    else if (stored.crc != PROD_MODE->crc && stored.version == 0u)
        productModeUpdate(PROD_MODE->mode);
    return 0;
}

void set_product_mode(uint8_t mode)
{
    LOG(2u, set_fn, 0x40u, 0x08400000u, set_mode_fmt, set_mode_short, (uint32_t)mode);
    PROD_MODE->mode = mode;
}

void productModeUpdate(uint8_t mode)
{
    g2_nvdb_product_mode_t *rec = PROD_MODE;
    set_product_mode(mode);
    rec->version = 1u;
    rec->crc = audio_uart_hand_checksum_49acd4(rec, 2u, NULL);
    (void)SVC_NvdbWrite(key_prod_mode, rec, 4u);
}

uint8_t productModeRead(void)
{
    g2_nvdb_product_mode_t *rec = PROD_MODE;
    (void)SVC_NvdbRead(key_prod_mode, rec, 4u);
    return rec->mode;
}
