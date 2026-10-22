/* Apollo main 0x473c44..0x473e2d, official s200_v2.2.6.10 image.
 * Candidate only: native helper semantics and final linker layout remain gated.
 */
#include <stdint.h>

typedef struct { uint32_t id, arg[8]; } display_driver_message;
_Static_assert(sizeof(display_driver_message) == 0x24, "native message size");

typedef struct {
    void (*thread_init)(void);
    void (*queue_init)(void);
    void *thread;
    void *queue;
} display_driver_manager_prefix;
_Static_assert(sizeof(display_driver_manager_prefix)==16u, "native manager size");
extern display_driver_manager_prefix audio_display_driver_manager; /* SRAM 0x20000658 */
volatile uint32_t display_driver_enabled; /* source-owned BSS cell, SRAM 0x200744ec */

/* Native calls named by their image addresses where semantics remain unknown. */
extern void audio_display_driver_queue_init(void); /* 0x4739fc */
extern void display_driver_init_473abc(void);
extern uint32_t display_driver_init_4c9f32(void);
extern void display_driver_init_473ac6(void);
extern void display_driver_init_473ad0(void);
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t); /* 0x43c0e4 */
extern uint32_t audio_uart_queue_receive(void *, void *, uint32_t, uint32_t); /* 0x449b3c */
extern void task_vote_acquire_current(void); /* 0x46d816 */
extern void task_vote_release_current(void); /* 0x46d826 */
extern void display_driver_case3_prelude(void); /* 0x46ca14 */
extern void display_driver_case3_sync(void); /* 0x47386a */
extern uint32_t display_driver_dispatch_gate(void); /* 0x46b238 */
extern uint32_t display_driver_case0(void); /* 0x4ca18a */
extern uint32_t display_driver_case1_a(void); /* 0x4ca010 */
extern void display_driver_case1_b(void); /* 0x473b34 */
extern uint32_t display_driver_case2(void); /* 0x4c9fb4 */
extern uint32_t display_driver_case3(uint32_t, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t); /* 0x4ca564 */
extern uint32_t display_driver_case4_read(uint32_t, uint32_t *, uint32_t *); /* 0x46c410 */
extern uint32_t display_driver_case4_apply(uint32_t, uint32_t, uint32_t); /* 0x4ca1ee */
extern void display_driver_case5_a(void); /* 0x473b46 */
extern uint32_t display_driver_case5_b(void); /* 0x4ca126 */
extern uint32_t display_driver_case6_guard(uint32_t); /* 0x4ca5be */
extern uint32_t display_driver_case8(uint32_t); /* 0x4ca60e */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint32_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern void compressed_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
static const char display_driver_task[] = "task.displaydrvmgr";
static const char display_driver_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\display_mgr\\displaydrv_manager.c";
static const char display_driver_function[] = "Disp_Mgr_ThreadHandler";
static const char display_driver_recovery[] = "uled recovery and reflash ok\r\n";
static const char display_driver_unknown[] = "unknow async command type = %d\r\n";
static const char display_driver_compact_recovery[] = "[task.displaydrvmgr]uled recovery and reflash ok\r\n";
static const char display_driver_compact_unknown[] = "[task.displaydrvmgr]unknow async command type = %d\r\n";

/* Stock 0x473C44 (Disp_Mgr_ThreadHandler) */
void display_driver_event_loop(void) {
    display_driver_message message;
    audio_display_driver_queue_init();
    display_driver_init_473abc();
    (void)display_driver_init_4c9f32();
    display_driver_init_473ac6();
    display_driver_init_473ad0();
    for (;;) {
        audio_uart_buffer_zero(&message, sizeof message, 0);
        if (audio_uart_queue_receive(audio_display_driver_manager.queue, &message, 0, UINT32_MAX) != 0)
            continue;
        task_vote_acquire_current();
        if (message.id == 3) {
            display_driver_case3_prelude();
            display_driver_case3_sync();
        }
        if (display_driver_dispatch_gate() == 0 && message.arg[8 - 1] == 0) {
            task_vote_release_current();
            continue;
        }
        switch (message.id) {
        case 0: (void)display_driver_case0(); break;
        case 1:
            (void)display_driver_case1_a();
            display_driver_case1_b();
            display_driver_enabled = 1;
            break;
        case 2:
            if (display_driver_enabled == 1) (void)display_driver_case2();
            break;
        case 3:
            if (display_driver_enabled == 1)
                (void)display_driver_case3(message.arg[0], message.arg[1], message.arg[2],
                                     message.arg[3], message.arg[4], message.arg[5]);
            break;
        case 4:
            if (display_driver_enabled == 1) {
                uint32_t first = 0, second = 0;
                (void)display_driver_case4_read(message.arg[6], &first, &second);
                (void)display_driver_case4_apply(message.arg[6], second, first);
            }
            break;
        case 5:
            if (display_driver_enabled == 1) {
                display_driver_case5_a();
                (void)display_driver_case5_b();
                display_driver_enabled = 0;
            }
            break;
        case 6:
            if (display_driver_enabled == 1 && (uint8_t)display_driver_case6_guard(1) == 0) {
                display_driver_case3_prelude();
                display_driver_case3_sync();
                (void)display_driver_case3(message.arg[0], message.arg[1], message.arg[2],
                                     message.arg[3], message.arg[4], message.arg[5]);
                if (audio_log_flags() & 2) audio_log_extended(3, display_driver_task, display_driver_file,
                                                                         display_driver_function, 0x10d, display_driver_recovery);
                if (audio_log_flags() & 1 || audio_log_flags() & 4)
                    compressed_log_output(0x0c000000, display_driver_compact_recovery, display_driver_compact_recovery);
            }
            break;
        case 8:
            if (display_driver_enabled == 1) (void)display_driver_case8((uint8_t)message.arg[6]);
            break;
        default:
            if (audio_log_flags() & 2) audio_log_extended(2, display_driver_task, display_driver_file,
                                                                 display_driver_function, 0x117, display_driver_unknown, message.id);
            if (audio_log_flags() & 1 || audio_log_flags() & 4)
                compressed_log_output(0x08400000, display_driver_compact_unknown,
                                           display_driver_compact_unknown, message.id);
            break;
        }
        task_vote_release_current();
    }
}

void audio_display_driver_thread_entry(void *argument) {
    (void)argument;
    display_driver_event_loop();
}
