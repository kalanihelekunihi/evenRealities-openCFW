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
/* Reset-copy descriptors use the upstream PDL callback ABI. */
#endif
