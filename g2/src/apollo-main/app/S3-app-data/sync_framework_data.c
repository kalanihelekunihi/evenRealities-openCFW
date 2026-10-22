/* Sync framework storage (S3 storage-definition pass, 2.2.6.10).
 *
 * Stock owner: framework\sync\sync_framework.c (module tag
 * "sync.module.framework") and the sync schedule manager / display start
 * blocking helpers in app/a-07-sync-framework. Every log call in the sync
 * listeners (0x45a578 role sampling, 0x45a6d0/0x45a72c user response,
 * 0x45d1ec schedule manager init, timeout listeners 0x45d710..0x45e5a4) loads
 * the same two ROM strings, module tag ROM 0x77c07c and __FILE__ ROM 0x705fb8.
 * Those are already defined as audio_uart_timer_module / audio_uart_timer_source
 * (rtos/S2-system-rtos-runtime-data/rtos_objects_data.c), so every per-caller
 * extern name (audio_uart_{master,role,user,timeout}_{module,source},
 * *_peer, *_display) is a defsym alias of those two (S3 manifest). All RAM
 * cells here are in the zero-init range 0x20004558..0x20075048. */
#include <stdint.h>

/* ---- disp_start_blocking.c / sync_schedule_manager.c -------------------- */

volatile uint16_t g2_disp_start_blocking_flag;       /* RAM 0x20074f48 */
void *g2_disp_start_blocking_timer;                  /* RAM 0x200749dc osTimerId_t */
void *g2_disp_start_blocking_mutex;                  /* RAM 0x200749e0 osMutexId_t */
volatile uint32_t g2_sync_schedule_startup_word;     /* RAM 0x200749e8 */
volatile uint8_t g2_sync_system_disp_status;         /* RAM 0x20075023 */

/* ---- display_slave_send.c ----------------------------------------------- */

void *g2_display_sender_mutex;                       /* RAM 0x200744e8 osMutexId_t */
