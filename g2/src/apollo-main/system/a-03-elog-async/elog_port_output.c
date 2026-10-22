/* EasyLogger port (G2 elog_port.c; no source-path string survives), native
 * 0x44aa2c..0x44ab41. This unit holds the port entry points that the upstream
 * EasyLogger a596b264 elog.c / elog_utils.c units call:
 *   elog_port_init          0x44aa68..0x44aa75  creates the port mutex, returns ELOG_NO_ERR
 *   elog_port_output        0x44aa76..0x44aa7f  queue a line at the default level
 *   elog_port_output_level  0x44aa80..0x44aa97  queue a line with its level and wake the
 *                                               log task (event bit 0 on RAM 0x20074570);
 *                                               the stock elog_output calls this instead of
 *                                               elog_port_output (name invented, no symbol)
 *   elog_port_output_lock   0x44aa98..0x44aa9f
 *   elog_port_output_unlock 0x44aaa0..0x44aaa7
 * The mutex create 0x44aa2c (rtos/rtos-glue-gaps/elog_mutex_init.c), lock helpers
 * 0x44aa40/0x44aa56 (extended-log-runtime/locks.c), get_time 0x44aaa8 (log-time)
 * and get_p_info/get_t_info 0x44ab14/0x44ab1c (log-task) are reconstructed
 * elsewhere; the manifest aliases elog_port_get_time/_p_info/_t_info to them. */
#include <stdint.h>
#include <stddef.h>

extern uint32_t elog_async_enqueue_log_448ccc(const char *text, uint32_t length, uint8_t level);
extern void g2_log_transport_submit(uint32_t source_address, uint32_t length,
                                    uint32_t level, uint32_t mode); /* 0x448d4e */
extern uint32_t osEventFlagsSet(void *ef_id, uint32_t flags);       /* 0x4495e4 */
extern uint32_t g2_audio_log_event_handle;                          /* RAM 0x20074570 */
extern void elog_port_mutex_create_44aa2c(void);
extern void g2_log_lock_enter(void); /* 0x44aa40 */
extern void g2_log_lock_exit(void);  /* 0x44aa56 */

/* ElogErrCode is a one-byte enum in stock (IAR); ELOG_NO_ERR = 0. */
uint8_t elog_port_init(void)
{
    uint8_t result = 0u;
    elog_port_mutex_create_44aa2c();
    return result;
}

/* Queue the formatted line at the default level. */
void elog_port_output(const char *log, size_t size)
{
    (void)elog_async_enqueue_log_448ccc(log, (uint32_t)size, 0u);
}

void elog_port_output_level(const char *log, size_t size, uint8_t level)
{
    g2_log_transport_submit((uint32_t)(uintptr_t)log, (uint32_t)size, 0u, level);
    (void)osEventFlagsSet((void *)(uintptr_t)g2_audio_log_event_handle, 1u);
}

void elog_port_output_lock(void)
{
    g2_log_lock_enter();
}

void elog_port_output_unlock(void)
{
    g2_log_lock_exit();
}
