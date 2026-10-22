/* EasyLogger port lock creation, native 0x44aa2c..0x44aa3f (literals 0x44aafc/0x44ab00),
 * called once from the port init at 0x44aa68. The lock/unlock pair 0x44aa40/0x44aa56
 * is g2_log_lock_enter/g2_log_lock_exit in
 * system/log/extended-log/extended-log-runtime/locks.c, which reads the same cell. */
#include <stdint.h>
#include <stddef.h>

typedef struct {
    const char *name; uint32_t attr_bits; void *cb_mem; uint32_t cb_size;
} g2_os_mutex_attr_t;
_Static_assert(sizeof(g2_os_mutex_attr_t) == 16, "osMutexAttr_t");

#define ELOG_MUTEX_CB_SIZE 0x50u /* StaticSemaphore_t */

extern void *g2_elog_mutex; /* RAM 0x20074578 */
extern void *osMutexNew(const void *attr); /* 0x44971c */

static const char elog_mutex_name[] = "elogMutex"; /* ROM 0x78a9a0 */
uint32_t g2_elog_mutex_cb[ELOG_MUTEX_CB_SIZE / 4u]; /* RAM 0x20072ad8 */
static const g2_os_mutex_attr_t elog_mutex_attr = { /* ROM 0x785dd0 */
    elog_mutex_name, 0u, g2_elog_mutex_cb, ELOG_MUTEX_CB_SIZE};

void elog_port_mutex_create_44aa2c(void)
{
    if (g2_elog_mutex == NULL)
        g2_elog_mutex = osMutexNew(&elog_mutex_attr);
}
