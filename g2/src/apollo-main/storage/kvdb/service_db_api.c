/* FlashDB service adapter, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\flashDB\db_api\service_db_api.c.
 * This unit: native 0x541088..0x54125b (mutex, object accessor, init).
 * SVC_FlashDBBlobRead 0x54116e and SVC_FlashDBBlobWrite 0x5411f2 are
 * g2_flashdb_candidate_blob_read / audio_flashdb_blob_write elsewhere in g2/src;
 * the FAL callbacks _flashDBInit/Read/Write/Erase (0x540ed0..0x541087) are not here.
 *
 * Two fdb_kvdb objects (2,220 bytes each) start at RAM 0x2005dffc: index 0 is
 * "sysenv" (SVC_KvdbInit), index 1 is "factory" (SVC_NvdbInit). One CMSIS mutex
 * with a static control block serialises both through FlashDB's lock hooks. */
#include "kvdb_private.h"

typedef struct {
    const char *name;   /* +0x0 */
    uint32_t attr_bits; /* +0x4 */
    void *cb_mem;       /* +0x8 */
    uint32_t cb_size;   /* +0xc */
} g2_os_mutex_attr_t;   /* osMutexAttr_t */

#define FLASHDB_OBJECT_SIZE 0x8acu

extern uint8_t g2_flashdb_db_rows[];       /* RAM 0x2005dffc, 2 x 0x8ac */
void *g2_flashdb_mutex_id;                            /* RAM 0x20074944 */
uint8_t g2_flashdb_mutex_cb[0x50] __attribute__((aligned(8))); /* RAM 0x20072d58 StaticSemaphore_t */

extern void *osMutexNew(const void *attr);
extern int32_t osMutexAcquire(void *mutex, uint32_t timeout);
extern int32_t osMutexRelease(void *mutex);
extern uint8_t SVC_NvdbInit(g2_flashdb_lock_fn lock, g2_flashdb_lock_fn unlock); /* 0x51079c */

static const char mutex_name[] = "flashDBMutex"; /* ROM 0x7888d0 */
static const g2_os_mutex_attr_t flashdb_mutex_attr = { /* ROM 0x788920 */
    mutex_name, 0u, g2_flashdb_mutex_cb, sizeof(g2_flashdb_mutex_cb)
};

static const char module_tag[] = "db.api"; /* ROM 0x78e54c */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\flashDB\\db_api\\service_db_api.c"; /* ROM 0x6e4cc8 */
static const char init_fn[] = "_flashDBMutexInit"; /* ROM 0x783154 */
static const char init_msg[] = "Warning: failed to Create flashDBMutexId"; /* ROM 0x743124 */
static const char init_msg_short[] = "[db.api]Warning: failed to Create flashDBMutexId"; /* ROM 0x72d318 */
static const char lock_fn[] = "_flashDBMutexLock"; /* ROM 0x783168 */
static const char lock_msg[] = "flashDBMutexId lock fail"; /* ROM 0x77116c */
static const char lock_msg_short[] = "[db.api]flashDBMutexId lock fail"; /* ROM 0x759924 */
static const char unlock_fn[] = "_flashDBMutexUnlock"; /* ROM 0x78317c */
static const char unlock_msg[] = "flashDBMutexId unlock fail"; /* ROM 0x771188 */
static const char unlock_msg_short[] = "[db.api]flashDBMutexId unlock fail"; /* ROM 0x759948 */

void _flashDBMutexInit(void) {
    if (g2_flashdb_mutex_id != NULL)
        return;
    g2_flashdb_mutex_id = osMutexNew(&flashdb_mutex_attr);
    if (g2_flashdb_mutex_id == NULL)
        G2_KV_LOG(1u, module_tag, source_file, init_fn, 138u, init_msg, init_msg_short, 0x04000000u);
}

void _flashDBMutexLock(void *db) {
    (void)db;
    if (osMutexAcquire(g2_flashdb_mutex_id, 0xffffffffu) != 0)
        G2_KV_LOG(1u, module_tag, source_file, lock_fn, 148u, lock_msg, lock_msg_short, 0x04000000u);
}

void _flashDBMutexUnlock(void *db) {
    (void)db;
    if (osMutexRelease(g2_flashdb_mutex_id) != 0)
        G2_KV_LOG(1u, module_tag, source_file, unlock_fn, 155u, unlock_msg, unlock_msg_short, 0x04000000u);
}

void *SVC_FlashDBGetObject(uint8_t index) {
    return g2_flashdb_db_rows + (uint32_t)index * FLASHDB_OBJECT_SIZE;
}

void SVC_FlashDBInit(void) {
    _flashDBMutexInit();
    (void)SVC_KvdbInit(_flashDBMutexLock, _flashDBMutexUnlock);
    (void)SVC_NvdbInit(_flashDBMutexLock, _flashDBMutexUnlock);
}
