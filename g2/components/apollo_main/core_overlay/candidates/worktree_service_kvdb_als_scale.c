/*
 * Clean-room reconstruction of the retained first-party G2 object
 * platform/service/flashDB/kv/service_kvdb_als_scale.c, covering the three
 * contiguous functions at [0x004AECA4,0x004AEDF6) plus their shared
 * absolute-address literal pool at [0x004AEDF8,0x004AEE28).
 *
 * Evidence: docs/research/g2-kvdb-als-scale-recovery.md and the recovered
 * in-component EasyLogger literals (file path, tag "kv.als_scale", the
 * "version %d(%d)" / "crc 0x%x(0x%x)" / "write als scale failed, ret = %d"
 * format strings, and the "kvAlsScale" key).
 */

#include <stdint.h>

typedef struct {
    uint8_t  version;
    uint8_t  payload[7];
    uint16_t crc16;
    uint8_t  reserved[2];
} als_scale_record;

#define ALS_SCALE_RECORD ((volatile als_scale_record *)(uintptr_t)0x200037BCu)
#define ALS_SCALE_KEY    "kvAlsScale"
#define ALS_SCALE_TAG    "kv.als_scale"
#define ALS_SCALE_FILE \
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\flashDB\\kv" \
    "\\service_kvdb_als_scale.c"

/* Recovered external ABI (absolute-address callees in the stock component). */
extern uint16_t open_cfw_crc16_ccitt(const void *data, uint32_t length,
                                     const uint16_t *seed);          /* 0x49ACD4 */
extern int  kvdb_get(const char *key, void *value, uint16_t length); /* 0x4D956C */
extern int  kvdb_set(const char *key, const void *value,
                     uint16_t length);                               /* 0x4D957E */
extern uint32_t elog_get_filter(void);                               /* 0x43D0CE */
extern void elog_output(uint32_t level, const char *tag, const char *file,
                        const char *func, long line, const char *format, ...);
                                                                     /* 0x43D574 */
extern void elog_async_output(uint32_t packed, const char *format, ...);
                                                                     /* 0x43CE9E */

enum { ELOG_LVL_ERROR = 1, ELOG_LVL_DEBUG = 4 };

int SVC_KvdbWriteAlsScale(const void *value);

int service_kvdb_als_scale_default_initialize(void)
{
    volatile als_scale_record *record = ALS_SCALE_RECORD;
    record->crc16 = open_cfw_crc16_ccitt((const void *)(uintptr_t)record, 8u, 0);
    return 0;
}

int _kvdbUpdataAlsScale(void)
{
    als_scale_record stored;
    volatile als_scale_record *record = ALS_SCALE_RECORD;
    int ret = kvdb_get(ALS_SCALE_KEY, &stored, (uint16_t)sizeof(stored));

    if (ret >= 1) {
        if (elog_get_filter() & 2u) {
            elog_output(ELOG_LVL_DEBUG, ALS_SCALE_TAG, ALS_SCALE_FILE,
                        "_kvdbUpdataAlsScale", 32, "version %d(%d)",
                        stored.version, 1);
        }
        if ((elog_get_filter() & 1u) || (elog_get_filter() & 4u)) {
            elog_async_output(0x10800000u, "[kv.als_scale]version %d(%d)",
                              stored.version, 1);
        }
        if (elog_get_filter() & 2u) {
            elog_output(ELOG_LVL_DEBUG, ALS_SCALE_TAG, ALS_SCALE_FILE,
                        "_kvdbUpdataAlsScale", 33, "crc 0x%x(0x%x)",
                        record->crc16, stored.crc16);
        }
        if ((elog_get_filter() & 1u) || (elog_get_filter() & 4u)) {
            elog_async_output(0x10800000u, "[kv.als_scale]crc 0x%x(0x%x)",
                              record->crc16, stored.crc16);
        }
        if (stored.crc16 != record->crc16 && stored.version == 0u) {
            (void)SVC_KvdbWriteAlsScale((const void *)(uintptr_t)record);
        }
    } else {
        (void)SVC_KvdbWriteAlsScale((const void *)(uintptr_t)record);
    }
    return 0;
}

int SVC_KvdbWriteAlsScale(const void *value)
{
    const uint8_t *source = (const uint8_t *)value;
    volatile als_scale_record *record = ALS_SCALE_RECORD;
    uint8_t *destination = (uint8_t *)(uintptr_t)record;
    uint32_t index;
    int ret;

    for (index = 0; index < sizeof(*record); ++index) {
        destination[index] = source[index];
    }
    record->version = 1u;
    record->crc16 = open_cfw_crc16_ccitt((const void *)(uintptr_t)record, 8u, 0);
    ret = kvdb_set(ALS_SCALE_KEY, (const void *)(uintptr_t)record,
                   (uint16_t)sizeof(*record));
    if (ret != 0) {
        if (elog_get_filter() & 2u) {
            elog_output(ELOG_LVL_ERROR, ALS_SCALE_TAG, ALS_SCALE_FILE,
                        "SVC_KvdbWriteAlsScale", 50,
                        "write als scale failed, ret = %d", ret);
        }
        if ((elog_get_filter() & 1u) || (elog_get_filter() & 4u)) {
            elog_async_output(0x04400000u,
                              "[kv.als_scale]write als scale failed, ret = %d",
                              ret);
        }
    }
    return 0;
}
