/* Event-group scheduler ABI adapters to selected Apollo source children.
 * Stock 0x454d7c/0x454dcc match the selected Audio suspend/resume entries. */
#include <stdint.h>
extern void audio_suspend(void);
extern int32_t stock_scheduler_resume(void);
void vTaskSuspendAll(void) { audio_suspend(); }
int32_t xTaskResumeAll(void) { return stock_scheduler_resume(); }
