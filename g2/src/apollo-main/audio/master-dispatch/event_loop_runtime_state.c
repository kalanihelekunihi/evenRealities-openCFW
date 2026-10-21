/* Source-owned event loop objects and CMSIS control-block storage. */
#include <stdint.h>

uint32_t audio_event_loop_delayed_slots[192u]
    __attribute__((section(".g2_ram_2006dad4")));
uint32_t audio_event_loop_elapsed
    __attribute__((section(".g2_ram_20074600")));
void *audio_event_loop_mutex
    __attribute__((section(".g2_ram_200745f4")));
uint8_t audio_event_loop_mutex_cb[80u]
    __attribute__((section(".g2_ram_20072b78")));
void *audio_event_loop_queue
    __attribute__((section(".g2_ram_200745ec")));
uint8_t audio_event_loop_queue_cb[80u]
    __attribute__((section(".g2_ram_20072b28")));
uint8_t audio_event_loop_queue_storage[120u]
    __attribute__((section(".g2_ram_20071d40")));
uint8_t audio_event_loop_thread_cb[112u]
    __attribute__((section(".g2_ram_20071f80")));
void *audio_event_loop_thread_handle
    __attribute__((section(".g2_ram_200745f0")));
uint8_t audio_event_loop_thread_stack[3072u]
    __attribute__((section(".g2_ram_20372bc0")));
void *audio_event_loop_timer
    __attribute__((section(".g2_ram_200745f8")));
uint8_t audio_event_loop_timer_cb[44u]
    __attribute__((section(".g2_ram_20073624")));
