/* Factory NV database service, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\flashDB\NV\service_nvdb.c.
 * Native 0x5105f0..0x510991; literal pool 0x510994..0x510a0b.
 *
 * Database object 1 (SVC_FlashDBGetObject) is the FlashDB 2.x KVDB "factory"
 * on FAL partition "NVdb". The nine-node default table at RAM 0x20003868 is
 * {key, RAM record, length}: nvString 9, nvMagic 4, nvProdMode 4, nvSysDt 172,
 * nvAdvMagic 4, nvMAC 10, nvSCald 92, nvSCaldAG 68, nvBuzzer 12. A missing or
 * wrong nvMagic (expected 0x55550022) resets the whole database to defaults.
 * The FlashDB calls are pinned upstream functions (fdb_kvdb_control,
 * fdb_kvdb_init, fdb_kv_set_default); only their stock addresses appear here. */
#include <stdint.h>
#include <stddef.h>
#include "nvdb_internal.h"

/* FlashDB struct fdb_default_kv_node / struct fdb_default_kv (32-bit ABI). */
typedef struct {
    const char *key;
    void *value;
    uint32_t value_len;
} g2_fdb_default_kv_node_t;
_Static_assert(sizeof(g2_fdb_default_kv_node_t) == 12, "FlashDB default node is 12 bytes");

typedef struct {
    g2_fdb_default_kv_node_t *kvs;
    uint32_t num;
} g2_fdb_default_kv_t;

#define NVDB_DB_INDEX 1u
#define NVDB_DEFAULT_COUNT 9u
#define NVDB_MAGIC 0x55550022u
#define FDB_KVDB_CTRL_SET_LOCK 2
#define FDB_KVDB_CTRL_SET_UNLOCK 3

extern g2_fdb_default_kv_node_t g2_nvdb_default_kv_nodes[NVDB_DEFAULT_COUNT]; /* RAM 0x20003868 */
extern g2_fdb_default_kv_node_t *g2_nvdb_default_kvs;                         /* RAM 0x20074990 */
extern uint8_t display_driver_ratio_cells_20003994[0xac]; /* RAM 0x20003994 nvSysDt */
#define SYS_DT ((g2_nvdb_sys_dt_t *)(void *)display_driver_ratio_cells_20003994)
extern char g2_otp_psn[15];                      /* RAM 0x20073ee4 g_OTP_PSN */

extern uint32_t SVC_FlashDBBlobRead(uint8_t db, const char *key, void *buffer, uint16_t length);
extern int32_t SVC_FlashDBBlobWrite(uint8_t db, const char *key, const void *buffer, uint16_t length);
extern void *SVC_FlashDBGetObject(uint8_t db);
extern uint8_t fdb_kvdb_control_545320(void *db, int32_t cmd, void *arg);
extern uint8_t fdb_kvdb_init_5453fe(void *db, const char *name, const char *path,
                                    g2_fdb_default_kv_t *default_kv, void *user_data);
extern uint8_t fdb_kv_set_default_5450a4(void *db);
extern int32_t audio_uart_font_path_compare(const char *, const char *); /* strcmp 0x46cacc */

void service_nvdb_defaults_get(g2_fdb_default_kv_t *defaults);
void service_nvdb_defaults_validate(void);

static const char module_tag[] = "nvdb"; /* ROM 0x78e604 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\flashDB\\NV\\service_nvdb.c"; /* ROM 0x6efa98 */
static const char validate_fn[] = "SVC_NvdbUpdataAll"; /* ROM 0x783438 */
static const char init_fn[] = "SVC_NvdbInit"; /* ROM 0x788bd0 */
static const char db_name[] = "factory"; /* ROM 0x78e60c */
static const char db_partition[] = "NVdb"; /* ROM 0x78e614 */
static const char key_magic[] = "nvMagic"; /* ROM 0x78e5e4 */
static const char key_sys_dt[] = "nvSysDt"; /* ROM 0x78e5ec */
static const char read_fail[] = "[%d]name:%s, NV read fail"; /* ROM 0x7713f0 */
static const char read_fail_short[] = "[nvdb][%d]name:%s, NV read fail"; /* ROM 0x765090 */
static const char otp_ok[] = "read SN from OTP success, g_OTP_PSN: %s, g_NVSysDt.record_PSN: %s"; /* ROM 0x705aac */
static const char otp_ok_short[] =
    "[nvdb]read SN from OTP success, g_OTP_PSN: %s, g_NVSysDt.record_PSN: %s"; /* ROM 0x6fd034 */
static const char otp_fail[] = "read SN from OTP failed"; /* ROM 0x77badc */
static const char otp_fail_short[] = "[nvdb]read SN from OTP failed"; /* ROM 0x7650b0 */
static const char init_fail[] = "%s init fail %d"; /* ROM 0x788be0 */
static const char init_fail_short[] = "[nvdb]%s init fail %d"; /* ROM 0x77baf4 */
static const char magic_fmt[] = "read the fdbMagic:0x%x,length:%d"; /* ROM 0x759c3c */
static const char magic_short[] = "[nvdb]read the fdbMagic:0x%x,length:%d"; /* ROM 0x74e024 */
static const char magic_missing[] = "length:%d,not exist fdbMagic, need format flashdb"; /* ROM 0x72d68c */
static const char magic_missing_short[] =
    "[nvdb]length:%d,not exist fdbMagic, need format flashdb"; /* ROM 0x722d60 */
static const char magic_wrong[] = "fdbMagic:0x%x,not equal:0x%x, need reset flashdb"; /* ROM 0x72d6c0 */
static const char magic_wrong_short[] =
    "[nvdb]fdbMagic:0x%x,not equal:0x%x, need reset flashdb"; /* ROM 0x722d98 */
static const char success[] = "success"; /* ROM 0x78e61c */
static const char success_short[] = "[nvdb]success"; /* ROM 0x788bf0 */

#define LOG(...) NVDB_LOG(module_tag, source_file, __VA_ARGS__)

int32_t SVC_NvdbRead(const char *key, void *buffer, uint16_t length)
{
    return (int32_t)SVC_FlashDBBlobRead(NVDB_DB_INDEX, key, buffer, length);
}

int32_t SVC_NvdbWrite(const char *key, const void *buffer, uint16_t length)
{
    return SVC_FlashDBBlobWrite(NVDB_DB_INDEX, key, buffer, length);
}

void service_nvdb_defaults_get(g2_fdb_default_kv_t *defaults)
{
    defaults->kvs = g2_nvdb_default_kv_nodes;
    defaults->num = NVDB_DEFAULT_COUNT;
}

/* Loads every default node's RAM record from flash; for nvSysDt the PSN is
 * then reconciled with OTP (stock function name "SVC_NvdbUpdataAll"). */
void service_nvdb_defaults_validate(void)
{
    g2_fdb_default_kv_t defaults;
    service_nvdb_defaults_get(&defaults);
    g2_nvdb_default_kvs = defaults.kvs;
    for (int16_t i = 0; (uint32_t)(int32_t)i < defaults.num; i++) {
        g2_fdb_default_kv_node_t *node = &g2_nvdb_default_kvs[i];
        if (node->value_len == 0u)
            continue;
        if (SVC_FlashDBBlobRead(NVDB_DB_INDEX, node->key, node->value,
                                (uint16_t)node->value_len) == 0u)
            LOG(1u, validate_fn, 0x92u, 0x04800000u, read_fail, read_fail_short,
                (int32_t)i, g2_nvdb_default_kvs[i].key);
        if (audio_uart_font_path_compare(g2_nvdb_default_kvs[i].key, key_sys_dt) != 0)
            continue;
        nvdbSysDtMarkLegacyPsn();
        if (SVC_ReadPSNFromOTP(g2_otp_psn, NULL) == 0) {
            LOG(3u, validate_fn, 0x9au, 0x0c800000u, otp_ok, otp_ok_short,
                g2_otp_psn, SYS_DT->psn);
            audio_uart_checksum_copy(SYS_DT->psn, g2_otp_psn, 14u);
            SYS_DT->psn[14] = '\0';
        } else {
            LOG(1u, validate_fn, 0xa0u, 0x04000000u, otp_fail, otp_fail_short);
        }
    }
}

/* Returns 0 on success, 8 when fdb_kvdb_init fails. After a magic reset the
 * stock code reads nvMagic again (it does not write it); the default node
 * already supplies the expected value. */
uint8_t SVC_NvdbInit(void (*lock)(void *), void (*unlock)(void *))
{
    uint32_t magic = 0u;
    g2_fdb_default_kv_t defaults;

    if (lock != NULL && unlock != NULL) {
        (void)fdb_kvdb_control_545320(SVC_FlashDBGetObject(NVDB_DB_INDEX), FDB_KVDB_CTRL_SET_LOCK,
                                      (void *)(uintptr_t)lock);
        (void)fdb_kvdb_control_545320(SVC_FlashDBGetObject(NVDB_DB_INDEX), FDB_KVDB_CTRL_SET_UNLOCK,
                                      (void *)(uintptr_t)unlock);
    }
    service_nvdb_defaults_get(&defaults);
    uint8_t result = fdb_kvdb_init_5453fe(SVC_FlashDBGetObject(NVDB_DB_INDEX), db_name,
                                          db_partition, &defaults, NULL);
    if (result != 0u) {
        LOG(1u, init_fn, 0xbfu, 0x04800000u, init_fail, init_fail_short, db_partition, (uint32_t)result);
        return 8u;
    }
    uint32_t length = SVC_FlashDBBlobRead(NVDB_DB_INDEX, key_magic, &magic, 4u);
    LOG(3u, init_fn, 0xc8u, 0x0c800000u, magic_fmt, magic_short, magic, length);
    if (length == 0u || magic != NVDB_MAGIC) {
        if (length == 0u)
            LOG(2u, init_fn, 0xcbu, 0x08400000u, magic_missing, magic_missing_short, length);
        else if (magic != NVDB_MAGIC)
            LOG(2u, init_fn, 0xcdu, 0x08800000u, magic_wrong, magic_wrong_short, magic, NVDB_MAGIC);
        magic = NVDB_MAGIC;
        (void)fdb_kv_set_default_5450a4(SVC_FlashDBGetObject(NVDB_DB_INDEX));
        (void)SVC_FlashDBBlobRead(NVDB_DB_INDEX, key_magic, &magic, 4u);
    }
    service_nvdb_defaults_validate();
    LOG(3u, init_fn, 0xdau, 0x0c000000u, success, success_short);
    return result;
}
