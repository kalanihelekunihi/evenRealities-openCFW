/* Native CMSIS semaphore attribute and static control-block contract. */
#include "FreeRTOS.h"
#include "semphr.h"
#include "cmsis_os2.h"
#include <stddef.h>
/* Native wrapper ignores attr->name; leave baseline kernel config unchanged. */
#undef configQUEUE_REGISTRY_SIZE
#define configQUEUE_REGISTRY_SIZE 0
_Static_assert(sizeof(StaticSemaphore_t)==80,"native static semaphore extent");
_Static_assert(offsetof(osSemaphoreAttr_t,cb_mem)==8 && offsetof(osSemaphoreAttr_t,cb_size)==12,"native attributes");
_Static_assert(configSUPPORT_STATIC_ALLOCATION==1 && configSUPPORT_DYNAMIC_ALLOCATION==1,"native both allocation paths");
_Static_assert(configQUEUE_REGISTRY_SIZE==0,"native no semaphore registry/name call");
