#include <stdint.h>
int32_t xTaskPriorityDisinherit(void *holder);
void vTaskPriorityDisinheritAfterTimeout(void *holder,uint32_t highest_waiter);
int32_t xTaskPriorityInherit(void *holder);
