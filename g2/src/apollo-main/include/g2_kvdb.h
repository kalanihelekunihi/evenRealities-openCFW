/* G2 system key-value settings store (stock platform\service\flashDB\kv\*.c and
 * platform\service\flashDB\db_api\service_db_api.c).
 *
 * Database index 0 is FlashDB 2.1.1 KVDB "sysenv" on FAL partition "kvdb"
 * (NOR 0x01FC0000, 0x38000 bytes); index 1 is "factory" on "NVdb". Both
 * fdb_kvdb objects live at RAM 0x2005dffc with stride 0x8ac.
 *
 * Every versioned record ends with a CRC-16/CCITT-FALSE (poly 0x1021, init
 * 0xffff; stock 0x49acd4) over the bytes before the CRC field. A record's
 * migration callback rewrites the RAM default when the stored record is
 * missing, or when its CRC differs and its version is older than current. */
#ifndef G2_KVDB_H
#define G2_KVDB_H

#include <stdint.h>

/* struct fdb_default_kv_node / struct fdb_default_kv (FlashDB 2.1.1). */
typedef struct {
    const char *key;    /* +0x0 */
    void *value;        /* +0x4 */
    uint32_t value_len; /* +0x8 */
} g2_kvdb_default_node_t;

typedef struct {
    g2_kvdb_default_node_t *kvs; /* +0x0 */
    uint32_t num;                /* +0x4 */
} g2_kvdb_default_t;

typedef void (*g2_flashdb_lock_fn)(void *db);
typedef int32_t (*g2_kvdb_migration_fn)(void);

#define G2_KVDB_MAGIC 0x5a000020u      /* "kvMagic" value */
#define G2_KVDB_MENU_MAGIC 0x5555aaaau /* kvMenuConfigureValue header */
#define G2_KVDB_MENU_ITEM_MAX 20u

/* Generic 12-byte record: kvTimeFormat, kvTemperatureUnit, kvAlsScale.
 * Payload field names are not recoverable from the store code. */
typedef struct {
    uint8_t version;      /* +0x0 */
    uint8_t field_01[3];  /* +0x1 */
    uint32_t field_04;    /* +0x4 kvAlsScale default 0x400 */
    uint16_t crc;         /* +0x8 over +0x0..+0x7 */
    uint16_t reserved;    /* +0xa */
} g2_kvdb_word_record_t;
_Static_assert(sizeof(g2_kvdb_word_record_t) == 12, "12-byte KV record");

typedef struct {
    uint8_t version;      /* +0x00 current 3 */
    uint8_t field_01[3];  /* +0x01 */
    uint32_t field_04;    /* +0x04 default 1 */
    uint32_t field_08;    /* +0x08 default 0 */
    uint32_t field_0c;    /* +0x0c default 0xffffffff */
    uint16_t field_10;    /* +0x10 default 0xffff */
    uint16_t crc;         /* +0x12 over +0x00..+0x11 */
} g2_kvdb_universal_setting_t;
_Static_assert(sizeof(g2_kvdb_universal_setting_t) == 20, "kvUniversalSetting");

typedef struct {
    uint8_t version;      /* +0x00 current 4 */
    uint8_t field_01[23]; /* +0x01 */
    uint16_t crc;         /* +0x18 over +0x00..+0x17 */
    uint8_t reserved[2];  /* +0x1a */
} g2_kvdb_setting_t;
_Static_assert(sizeof(g2_kvdb_setting_t) == 28, "kvSetting");

typedef struct {
    uint8_t version;      /* +0x0 current 1 */
    uint8_t mode;         /* +0x1 */
    uint16_t crc;         /* +0x2 over +0x0..+0x1 */
} g2_kvdb_terminal_mode_t;
_Static_assert(sizeof(g2_kvdb_terminal_mode_t) == 4, "kvTerminalMode");

typedef struct {
    uint8_t version;      /* +0x0 current 3 */
    uint8_t reserved_01[3];
    uint32_t timestamp;   /* +0x4 Unix seconds */
    int8_t timezone;      /* +0x8 */
    uint8_t reserved_09;
    uint16_t crc;         /* +0xa over +0x0..+0x9 */
} g2_kvdb_time_t;
_Static_assert(sizeof(g2_kvdb_time_t) == 12, "kvTime");

typedef struct {
    uint8_t version;      /* +0x00 current 1 */
    uint8_t mac[6];       /* +0x01 */
    char name[14];        /* +0x07, byte 13 forced to NUL on write */
    uint8_t reserved;     /* +0x15 */
    uint16_t crc;         /* +0x16 over +0x00..+0x15 */
} g2_kvdb_ring_t;
_Static_assert(sizeof(g2_kvdb_ring_t) == 24, "kvRing");

typedef struct {
    uint8_t app_type;     /* +0x00 0 = built-in app */
    uint8_t reserved[3];
    int32_t icon_num;     /* +0x04 */
    char text_name[32];   /* +0x08 */
    int32_t app_id;       /* +0x28 */
} g2_kvdb_menu_item_t;
_Static_assert(sizeof(g2_kvdb_menu_item_t) == 44, "menu item record");

typedef struct {
    uint32_t magic;       /* +0x000 G2_KVDB_MENU_MAGIC */
    uint8_t total_count;  /* +0x004 */
    uint8_t reserved[3];
    g2_kvdb_menu_item_t items[G2_KVDB_MENU_ITEM_MAX]; /* +0x008 */
} g2_kvdb_menu_configure_t;
_Static_assert(sizeof(g2_kvdb_menu_configure_t) == 0x378, "kvMenuConfigureValue");

/* db_api */
void _flashDBMutexInit(void);
void _flashDBMutexLock(void *db);
void _flashDBMutexUnlock(void *db);
void *SVC_FlashDBGetObject(uint8_t index);
void SVC_FlashDBInit(void);

/* service_kvdb */
void SVC_KvdbRunMigrations(void);
int32_t SVC_KvdbBlobRead(const char *key, void *buf, uint16_t length);
void SVC_KvdbDefaultDescriptor(g2_kvdb_default_t *defaults);
void SVC_KvdbReadAll(void);
uint8_t SVC_KvdbInit(g2_flashdb_lock_fn lock, g2_flashdb_lock_fn unlock);
int32_t SVC_KvdbInvalidateMagic(void);

/* per-record objects */
int32_t kvdbUniversalSettingDefaultInitialize(void);
int32_t _kvdbUpdataUniversalSetting(void);
int32_t SVC_KvdbWriteUniversalSetting(const g2_kvdb_universal_setting_t *setting);
int32_t kvdbTimeFormatDefaultInitialize(void);
int32_t _kvdbUpdataTimeFormat(void);
int32_t SVC_KvdbWriteTimeFormat(const g2_kvdb_word_record_t *record);
int32_t kvdbTemperatureUnitDefaultInitialize(void);
int32_t _kvdbUpdataTemperatureUnit(void);
int32_t SVC_KvdbWriteTemperatureUnit(const g2_kvdb_word_record_t *record);
int32_t kvdbSettingDefaultInitialize(void);
int32_t _kvdbUpdataSetting(void);
int32_t SVC_KvdbWriteSetting(const g2_kvdb_setting_t *setting);
int32_t kvdbAlsScaleDefaultInitialize(void);
int32_t _kvdbUpdataAlsScale(void);
int32_t SVC_KvdbWriteAlsScale(const g2_kvdb_word_record_t *record);
int32_t kvdbTerminalModeDefaultInitialize(void);
int32_t _kvdbUpdataTerminalMode(void);
int32_t kvdbTimeDefaultInitialize(void);
int32_t _kvdbUpdataTime(void);
int32_t SVC_KvdbWriteTime(uint32_t timestamp, int8_t timezone);
int32_t kvdbRingDefaultInitialize(void);
int32_t _kvdbUpdataRing(void);
int32_t SVC_KvdbWriteRing(const uint8_t *mac, const char *name);
int32_t SVC_SetKvdbOnboardingConfig(uint8_t index, const uint8_t *value);
int32_t SVC_KvdbBlobWriteOnboardingConfig(void);
void kvdbOnboardingConfigUpdateAndPersist(uint8_t index, const uint8_t *value);
volatile uint8_t *kvdbOnboardingConfigPointer(uint8_t index);
volatile uint8_t *SVC_KvdbReadOnboardingConfig(uint8_t index);
int32_t SVC_KvdbReadLanguage(void);
int32_t SVC_KvdbWriteLanguage(uint8_t language);
int32_t SVC_KvdbReadDashboardAutoCloseValue(void);
int32_t SVC_KvdbWriteDashboardAutoCloseValue(uint32_t value);
int32_t SVC_KvdbReadMenuConfigureValue(void);
int32_t SVC_KvdbWriteMenuConfigureValue(void);

#endif
