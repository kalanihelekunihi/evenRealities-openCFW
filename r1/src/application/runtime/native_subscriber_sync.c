/* Local event mutex wrappers; CMSIS and FreeRTOS providers remain upstream-owned. */
__attribute__((naked,section(".text.r1_subscriber_lock"))) void r1_subscriber_lock(void) { __asm__ volatile("NCF_5dcb0:\npush\t{r4, lr}\nNCF_5dcb2:\nldr r4, NCF_5dccc\nNCF_5dcb4:\nldr\tr0, [r4, #0]\nNCF_5dcb6:\ncbnz r0, NCF_5dcc0\nNCF_5dcb8:\nldr r0, NCF_5dcd0\nNCF_5dcba:\nbl osMutexNew\nNCF_5dcbe:\nstr\tr0, [r4, #0]\nNCF_5dcc0:\nldmia.w\tsp!, {r4, lr}\nNCF_5dcc4:\nmov.w\tr1, #4294967295\nNCF_5dcc8:\nb.w osMutexAcquire\nNCF_5dccc:\n.word r1_subscriber_mutex\nNCF_5dcd0:\n.word r1_subscriber_mutex_attr\n"); }
__attribute__((naked,section(".text.r1_subscriber_unlock"))) void r1_subscriber_unlock(void) { __asm__ volatile("NCF_5dcd4:\nldr r0, NCF_5dce4\nNCF_5dcd6:\nldr\tr0, [r0, #0]\nNCF_5dcd8:\ncmp\tr0, #0\nNCF_5dcda:\nbeq.n NCF_5dce0\nNCF_5dcdc:\nb.w osMutexRelease\nNCF_5dce0:\nbx\tlr\n.space 2,0\nNCF_5dce4:\n.word r1_subscriber_mutex\n"); }
__attribute__((naked,section(".text.r1_subscriber_current_thread"))) void r1_subscriber_current_thread(void) { __asm__ volatile("NCF_7d814:\nb.w xTaskGetCurrentTaskHandle\n"); }
#include <stdint.h>
uint32_t r1_subscriber_mutex __attribute__((section(".r1.subscriber.mutex"),aligned(4)))=0;
uint32_t r1_subscriber_mutex_control[20] __attribute__((section(".r1.subscriber.control"),aligned(4)))={0};
const char r1_subscriber_mutex_name[12] __attribute__((section(".r1.subscriber.name")))="event_mutex";
struct r1_mutex_attr { const char *name; uint32_t bits; void *memory; uint32_t size; };
const struct r1_mutex_attr r1_subscriber_mutex_attr __attribute__((section(".r1.subscriber.attr"),aligned(4)))={r1_subscriber_mutex_name,0,r1_subscriber_mutex_control,80};
