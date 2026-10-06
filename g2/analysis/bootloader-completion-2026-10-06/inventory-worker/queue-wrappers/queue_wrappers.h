/* Readable candidate for Apollo bootloader queue wrappers at 0x416816,
 * 0x4168A2 and 0x416920. Kernel entry points are version-agnostic provider
 * boundaries; the evidence file records their linked addresses separately.
 */
#ifndef OPENCFW_BOOT_QUEUE_WRAPPERS_H
#define OPENCFW_BOOT_QUEUE_WRAPPERS_H

#include <stdint.h>

typedef void *opencfw_queue_handle_t;

/* CMSIS-RTOS2 osMessageQueueAttr_t field layout, as consumed by these bytes. */
typedef struct {
    const char *name;       /* +0, ignored */
    uint32_t attr_bits;     /* +4, ignored */
    void *cb_mem;           /* +8 */
    uint32_t cb_size;       /* +12 */
    void *mq_mem;           /* +16 */
    uint32_t mq_size;       /* +20 */
} opencfw_queue_attr_t;

enum {
    OPENCFW_OS_OK = 0,
    OPENCFW_OS_ERROR_TIMEOUT = -2,
    OPENCFW_OS_ERROR_RESOURCE = -3,
    OPENCFW_OS_ERROR_PARAMETER = -4
};

opencfw_queue_handle_t opencfw_bl_queue_create(
    uint32_t msg_count, uint32_t msg_size, const opencfw_queue_attr_t *attr);
int32_t opencfw_bl_queue_put(opencfw_queue_handle_t queue, const void *msg,
                              uint32_t msg_priority, uint32_t timeout);
int32_t opencfw_bl_queue_get(opencfw_queue_handle_t queue, void *msg,
                              uint32_t *msg_priority, uint32_t timeout);
uint32_t opencfw_bl_queue_is_nonblocking_context(void);

#endif
