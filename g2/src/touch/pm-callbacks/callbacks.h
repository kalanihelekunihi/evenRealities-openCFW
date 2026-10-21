#ifndef TOUCH_PM_CALLBACKS_OFFLINE_H
#define TOUCH_PM_CALLBACKS_OFFLINE_H
#include <stdint.h>
#include <stdbool.h>
typedef struct {void *base,*context;} touch_pm_params;
typedef struct touch_pm_callback touch_pm_callback;
struct touch_pm_callback {
 uint32_t (*callback)(touch_pm_params *,uint32_t);
 uint8_t type;
 uint32_t skip;
 touch_pm_params *params;
 touch_pm_callback *prev,*next;
 uint8_t order;
};
bool touch_pm_register(touch_pm_callback *handler);
/* type0/1, mode1/2/4/8; mode8 requires a nonempty coherent list. */
uint32_t touch_pm_execute(uint32_t type,uint32_t mode);
uint32_t touch_pm_deep_sleep(void);
#endif
