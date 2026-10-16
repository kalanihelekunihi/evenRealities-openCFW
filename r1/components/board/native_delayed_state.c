#include "native_delayed_state.h"
/* Source-owned zero-initialized storage and authenticated product attributes.
 * Runtime creation remains the initializer/provider contract, not static handles. */
#define RAM(name,size,section_name) uint8_t name[size] __attribute__((section(section_name),aligned(4)))
volatile uint32_t r1_delayed_context[6] __attribute__((section(".r1.delayed.context"),aligned(4)));
uint32_t r1_delayed_callbacks[64] __attribute__((section(".r1.delayed.callbacks"),aligned(4)));
uint32_t r1_delayed_arguments[64] __attribute__((section(".r1.delayed.arguments"),aligned(4)));
uint32_t r1_delayed_deadlines[64] __attribute__((section(".r1.delayed.deadlines"),aligned(4)));
RAM(r1_delayed_queue_cb,80,".r1.delayed.queue_cb");
RAM(r1_delayed_queue_storage,120,".r1.delayed.queue_storage");
RAM(r1_delayed_thread_cb,112,".r1.delayed.thread_cb");
RAM(r1_delayed_thread_stack,3072,".r1.delayed.thread_stack");
RAM(r1_delayed_mutex_cb,80,".r1.delayed.mutex_cb");
RAM(r1_delayed_timer_cb,44,".r1.delayed.timer_cb");
const struct r1_delayed_queue_attr r1_delayed_queue_attributes={"fw_evt_loop_mesq",0,r1_delayed_queue_cb,80,r1_delayed_queue_storage,120};
const struct r1_delayed_thread_attr r1_delayed_thread_attributes={"evt_loop",0,r1_delayed_thread_cb,112,r1_delayed_thread_stack,3072,32,0,0};
const struct r1_delayed_object_attr r1_delayed_mutex_attributes={"fw_evt_loop_mutex",0,r1_delayed_mutex_cb,80};
/* Stock timer uses the same name string as its mutex. */
const struct r1_delayed_object_attr r1_delayed_timer_attributes={"fw_evt_loop_mutex",0,r1_delayed_timer_cb,44};
_Static_assert(sizeof(struct r1_delayed_queue_attr)==24 && sizeof(struct r1_delayed_thread_attr)==36 && sizeof(struct r1_delayed_object_attr)==16,"native product attributes");
