/* System KVDB service, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\flashDB\kv\service_kvdb.c.
 * Native 0x4d9530..0x4d9a97 (SVC_KvdbBlobWrite 0x4d957e is
 * audio_settings_kvdb_blob_write elsewhere); literal pool 0x4d9a98..0x4d9b33.
 *
 * Database 0 is FlashDB "sysenv" on partition "kvdb". Its default table has
 * twelve explicit-length nodes (RAM 0x2000372c, initialised data):
 *
 *   key                 value RAM    len  stock default
 *   kvString            0x2000371c     9  "kvString"
 *   kvMagic             0x20003728     4  0x5a000020
 *   kvbooCount          0x20074988     4  0 (bss; incremented every boot)
 *   kvTime              0x2000380c    12  01 00 00 00 2b2d3768 20 00 0000
 *   kvTimeFormat        0x20003818    12  01 000000 00000000 0000 0000
 *   kvTemperatureUnit   0x200037fc    12  01 000000 00000000 0000 0000
 *   kvUniversalSetting  0x20003824    20  03 000000 01000000 00000000 ffffffff ffff 0000
 *   kvSetting           0x200037e0    28  01 64 01 00 00 00 00 00 06 01 01 00 1e 00 ... 0000
 *   kvOnboardingConfig  0x20000040     1  00
 *   kvRing              0x200037c8    24  01 ffffffffffff "EVEN R1_FFFFFF" 00 0000
 *   kvTerminalMode      0x20003808     4  01 00 0000
 *   kvAlsScale          0x200037bc    12  01 000000 00040000 0000 0000
 *
 * CRC fields start at zero and are filled by the per-record
 * DefaultInitialize functions (stock init table, level 75) before init. */
#include "kvdb_private.h"

#define KVDB_DEFAULT_NODES 12u
#define KVDB_MIGRATION_MAX 100u
#define FDB_KVDB_CTRL_SET_LOCK 2
#define FDB_KVDB_CTRL_SET_UNLOCK 3
#define FDB_INIT_FAILED 8u

/* FlashDB 2.1.1 (upstream, report only). */
extern void fdb_kvdb_control(void *db, int cmd, void *arg);                      /* 0x545320 */
extern uint8_t fdb_kvdb_init(void *db, const char *name, const char *path,
                             g2_kvdb_default_t *default_kv, void *user_data);    /* 0x5453fe */
extern uint8_t fdb_kv_set_default(void *db);                                     /* 0x5450a4 */
extern void *audio_queue_copy_bytes(void *, const void *, uint32_t);             /* 0x439be4 */

/* Record owners (other units of this segment and of g2/src). */
extern g2_kvdb_time_t g2_kvdb_time_record;                            /* RAM 0x2000380c */
extern g2_kvdb_word_record_t g2_kvdb_time_format_record;              /* RAM 0x20003818 */
extern g2_kvdb_word_record_t g2_kvdb_temperature_unit_record;         /* RAM 0x200037fc */
extern g2_kvdb_universal_setting_t g2_kvdb_universal_setting_record;  /* RAM 0x20003824 */
extern g2_kvdb_setting_t g2_kvdb_setting_record;                      /* RAM 0x200037e0 */
extern volatile uint8_t g2_onboarding_flag;                           /* RAM 0x20000040 */
extern g2_kvdb_ring_t g2_kvdb_ring_record;                            /* RAM 0x200037c8 */
extern uint8_t audio_settings_terminal_record[4];                     /* RAM 0x20003808 */
extern g2_kvdb_word_record_t g2_kvdb_als_scale_record;                /* RAM 0x200037bc */

/* Section bounds of the eleven registered migration callbacks. */
extern const g2_kvdb_migration_fn __start_kvdb_migration[];           /* ROM 0x746d20 */
extern const g2_kvdb_migration_fn __stop_kvdb_migration[];            /* ROM 0x746d4c */

uint32_t g2_kvdb_boot_count;                                          /* RAM 0x20074988 */
g2_kvdb_default_node_t *g2_kvdb_default_nodes;                        /* RAM 0x2007498c */
g2_kvdb_migration_fn g2_kvdb_migration_list[KVDB_MIGRATION_MAX];      /* RAM 0x2006fabc */

static const char module_tag[] = "kvdb"; /* ROM 0x78e58c; also the partition name */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\flashDB\\kv\\service_kvdb.c"; /* ROM 0x6ef9f8 */
static const char db_name[] = "sysenv";             /* ROM 0x78e594 */
static const char key_string[] = "kvString";        /* ROM 0x78bf60 */
static const char key_magic[] = "kvMagic";          /* ROM 0x78e574 */
static const char key_boot_count[] = "kvbooCount";  /* ROM 0x78bf6c */
static const char key_time[] = "kvTime";            /* ROM 0x78e57c */
static const char key_time_format[] = "kvTimeFormat";             /* ROM 0x788a10 */
static const char key_temperature_unit[] = "kvTemperatureUnit";   /* ROM 0x7832bc */
static const char key_universal_setting[] = "kvUniversalSetting"; /* ROM 0x7832d0 */
static const char key_setting[] = "kvSetting";                    /* ROM 0x78bf78 */
static const char key_onboarding[] = "kvOnboardingConfig";        /* ROM 0x7832e4 */
static const char key_ring[] = "kvRing";                          /* ROM 0x78e584 */
static const char key_terminal_mode[] = "kvTerminalMode";         /* ROM 0x788a20 */
static const char key_als_scale[] = "kvAlsScale";                 /* ROM 0x78bf84 */

static const char read_all_fn[] = "SVC_KvdbReadAll"; /* ROM 0x788a30 */
static const char read_all_msg[] = "[%d]name:%s,len:%d"; /* ROM 0x7832f8 */
static const char read_all_msg_short[] = "[kvdb][%d]name:%s,len:%d"; /* ROM 0x771284 */
static const char read_fail_msg[] = "[%d]name:%s, KV read fail"; /* ROM 0x7712a0 */
static const char read_fail_msg_short[] = "[kvdb][%d]name:%s, KV read fail"; /* ROM 0x764f50 */
static const char init_fn[] = "SVC_KvdbInit"; /* ROM 0x788a40 */
static const char init_msg[] = "SVC_KvdbInit SVC_KVDB"; /* ROM 0x77b8b4 */
static const char init_msg_short[] = "[kvdb]SVC_KvdbInit SVC_KVDB"; /* ROM 0x7712bc */
static const char init_fail_msg[] = "%s init fail %d"; /* ROM 0x788a50 */
static const char init_fail_msg_short[] = "[kvdb]%s init fail %d"; /* ROM 0x77b8cc */
static const char pmagic_msg[] = "read the pfdbMagic:%s"; /* ROM 0x77b8e4 */
static const char pmagic_msg_short[] = "[kvdb]read the pfdbMagic:%s"; /* ROM 0x7712d8 */
static const char magic_len_msg[] = "read the fdbMagic:0x%x,length:%d"; /* ROM 0x759ad4 */
static const char magic_len_msg_short[] = "[kvdb]read the fdbMagic:0x%x,length:%d"; /* ROM 0x74df0c */
static const char no_magic_msg[] = "length:%d,not exist fdbMagic, need format flashdb"; /* ROM 0x72d588 */
static const char no_magic_msg_short[] = "[kvdb]length:%d,not exist fdbMagic, need format flashdb"; /* ROM 0x722c80 */
static const char bad_magic_msg[] = "fdbMagic:0x%x,not equal:0x%x, need reset flashdb"; /* ROM 0x72d5bc */
static const char bad_magic_msg_short[] = "[kvdb]fdbMagic:0x%x,not equal:0x%x, need reset flashdb"; /* ROM 0x722cb8 */
static const char set_default_msg[] = "SVC_FdbKvSetDefault"; /* ROM 0x78330c */
static const char set_default_msg_short[] = "[kvdb]SVC_FdbKvSetDefault"; /* ROM 0x7712f4 */
static const char reread_msg[] = "read the SVC_KVDB fdbMagic:0x%x,length:%d"; /* ROM 0x7432b0 */
static const char reread_msg_short[] = "[kvdb]read the SVC_KVDB fdbMagic:0x%x,length:%d"; /* ROM 0x7384a4 */
static const char magic_msg[] = "read the fdbMagic:0x%x"; /* ROM 0x77b8fc */
static const char magic_msg_short[] = "[kvdb]read the fdbMagic:0x%x"; /* ROM 0x764f70 */
static const char boot_msg[] = "read the bootCount:%d"; /* ROM 0x77b914 */
static const char boot_msg_short[] = "[kvdb]read the bootCount:%d"; /* ROM 0x771310 */
static const char success_msg[] = "success"; /* ROM 0x78e59c */
static const char success_msg_short[] = "[kvdb]success"; /* ROM 0x788a60 */

static char kv_string_value[9] = "kvString";  /* RAM 0x2000371c */
static uint32_t kv_magic_value = G2_KVDB_MAGIC; /* RAM 0x20003728 */

static g2_kvdb_default_node_t default_kv_table[KVDB_DEFAULT_NODES] = { /* RAM 0x2000372c */
    { key_string, kv_string_value, 9u },
    { key_magic, &kv_magic_value, 4u },
    { key_boot_count, &g2_kvdb_boot_count, 4u },
    { key_time, &g2_kvdb_time_record, 12u },
    { key_time_format, &g2_kvdb_time_format_record, 12u },
    { key_temperature_unit, &g2_kvdb_temperature_unit_record, 12u },
    { key_universal_setting, &g2_kvdb_universal_setting_record, 20u },
    { key_setting, &g2_kvdb_setting_record, 28u },
    { key_onboarding, (void *)(uintptr_t)&g2_onboarding_flag, 1u },
    { key_ring, &g2_kvdb_ring_record, 24u },
    { key_terminal_mode, audio_settings_terminal_record, 4u },
    { key_als_scale, &g2_kvdb_als_scale_record, 12u },
};

void SVC_KvdbRunMigrations(void) {
    uint32_t count = (uint32_t)(__stop_kvdb_migration - __start_kvdb_migration);
    if (count > KVDB_MIGRATION_MAX)
        count = KVDB_MIGRATION_MAX;
    audio_queue_copy_bytes(g2_kvdb_migration_list, __start_kvdb_migration,
                           count * sizeof(g2_kvdb_migration_fn));
    for (uint32_t i = 0; i < count; i++) {
        if (g2_kvdb_migration_list[i] != NULL)
            (void)g2_kvdb_migration_list[i]();
    }
}

int32_t SVC_KvdbBlobRead(const char *key, void *buf, uint16_t length) {
    return (int32_t)g2_flashdb_candidate_blob_read(0u, (uint32_t)(uintptr_t)key,
                                                   (uint32_t)(uintptr_t)buf, length);
}

void SVC_KvdbDefaultDescriptor(g2_kvdb_default_t *defaults) {
    defaults->kvs = default_kv_table;
    defaults->num = KVDB_DEFAULT_NODES;
}

/* Reload every non-empty default node from flash into its RAM value. */
void SVC_KvdbReadAll(void) {
    g2_kvdb_default_t defaults;
    SVC_KvdbDefaultDescriptor(&defaults);
    g2_kvdb_default_nodes = defaults.kvs;
    for (int16_t i = 0; (uint32_t)(int32_t)i < defaults.num; i++) {
        g2_kvdb_default_node_t *node = &g2_kvdb_default_nodes[i];
        if (node->value_len == 0u)
            continue;
        G2_KV_LOG(4u, module_tag, source_file, read_all_fn, 141u, read_all_msg, read_all_msg_short,
                  0x10c00000u, (int32_t)i, node->key, node->value_len);
        if (g2_flashdb_candidate_blob_read(0u, (uint32_t)(uintptr_t)node->key,
                                           (uint32_t)(uintptr_t)node->value,
                                           node->value_len & 0xffffu) == 0u)
            G2_KV_LOG(1u, module_tag, source_file, read_all_fn, 144u, read_fail_msg,
                      read_fail_msg_short, 0x04800000u, (int32_t)i, node->key);
    }
}

/* Mount "sysenv"; a missing or foreign kvMagic resets the whole database to
 * defaults while carrying the onboarding byte across the reset. Then count the
 * boot, run the record migrations and reload all records. */
uint8_t SVC_KvdbInit(g2_flashdb_lock_fn lock, g2_flashdb_lock_fn unlock) {
    uint32_t boot_count = 0u;
    uint32_t magic = 0u;
    g2_kvdb_default_t defaults;
    uint32_t length;

    G2_KV_LOG(4u, module_tag, source_file, init_fn, 162u, init_msg, init_msg_short, 0x10000000u);
    if (lock != NULL && unlock != NULL) {
        fdb_kvdb_control(SVC_FlashDBGetObject(0u), FDB_KVDB_CTRL_SET_LOCK, (void *)lock);
        fdb_kvdb_control(SVC_FlashDBGetObject(0u), FDB_KVDB_CTRL_SET_UNLOCK, (void *)unlock);
    }
    SVC_KvdbDefaultDescriptor(&defaults);
    uint8_t result = fdb_kvdb_init(SVC_FlashDBGetObject(0u), db_name, module_tag, &defaults, NULL);
    if (result != 0u) {
        G2_KV_LOG(1u, module_tag, source_file, init_fn, 174u, init_fail_msg, init_fail_msg_short,
                  0x04800000u, module_tag, (uint32_t)result);
        return FDB_INIT_FAILED;
    }

    G2_KV_LOG(4u, module_tag, source_file, init_fn, 180u, pmagic_msg, pmagic_msg_short, 0x10400000u,
              key_magic);
    length = g2_flashdb_candidate_blob_read(0u, (uint32_t)(uintptr_t)key_magic,
                                            (uint32_t)(uintptr_t)&magic, 4u);
    G2_KV_LOG(4u, module_tag, source_file, init_fn, 183u, magic_len_msg, magic_len_msg_short,
              0x10800000u, magic, length);
    if (length != 0u && magic == G2_KVDB_MAGIC) {
        G2_KV_LOG(4u, module_tag, source_file, init_fn, 199u, magic_msg, magic_msg_short,
                  0x10400000u, magic);
    } else {
        if (length == 0u) {
            G2_KV_LOG(2u, module_tag, source_file, init_fn, 186u, no_magic_msg, no_magic_msg_short,
                      0x08400000u, length);
        } else if (magic != G2_KVDB_MAGIC) {
            G2_KV_LOG(2u, module_tag, source_file, init_fn, 188u, bad_magic_msg,
                      bad_magic_msg_short, 0x08800000u, magic, G2_KVDB_MAGIC);
            (void)SVC_KvdbReadOnboardingConfig(1u);
        }
        magic = G2_KVDB_MAGIC;
        (void)fdb_kv_set_default(SVC_FlashDBGetObject(0u));
        G2_KV_LOG(4u, module_tag, source_file, init_fn, 194u, set_default_msg,
                  set_default_msg_short, 0x10000000u);
        (void)SVC_KvdbBlobWriteOnboardingConfig();
        length = g2_flashdb_candidate_blob_read(0u, (uint32_t)(uintptr_t)key_magic,
                                                (uint32_t)(uintptr_t)&magic, 4u);
        G2_KV_LOG(4u, module_tag, source_file, init_fn, 197u, reread_msg, reread_msg_short,
                  0x10800000u, magic, length);
    }

    (void)g2_flashdb_candidate_blob_read(0u, (uint32_t)(uintptr_t)key_boot_count,
                                         (uint32_t)(uintptr_t)&boot_count, 4u);
    G2_KV_LOG(3u, module_tag, source_file, init_fn, 204u, boot_msg, boot_msg_short, 0x0c400000u,
              boot_count);
    boot_count++;
    (void)audio_flashdb_blob_write(0u, key_boot_count, &boot_count, 4u);
    SVC_KvdbRunMigrations();
    SVC_KvdbReadAll();
    G2_KV_LOG(3u, module_tag, source_file, init_fn, 212u, success_msg, success_msg_short, 0x0c000000u);
    return result;
}

/* Zero kvMagic so the next SVC_KvdbInit resets the database to defaults. */
int32_t SVC_KvdbInvalidateMagic(void) {
    uint32_t magic = 0u;
    (void)audio_flashdb_blob_write(0u, key_magic, &magic, 4u);
    return 0;
}
