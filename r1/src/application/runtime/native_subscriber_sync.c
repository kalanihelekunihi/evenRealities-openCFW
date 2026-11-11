#include <stddef.h>
#include "native_subscriber.h"
/* Native 0x5dcb0 / 0x5dcd4. The factory acquires even a zero creation
 * result, and its unlock route samples the shared cell again. */
volatile uint32_t r1_subscriber_mutex __attribute__((section(".r1.subscriber.mutex"),aligned(4)))=0;
uint32_t r1_subscriber_mutex_control[20] __attribute__((section(".r1.subscriber.control"),aligned(4)))={0};
const char r1_subscriber_mutex_name[12] __attribute__((section(".r1.subscriber.name")))="event_mutex";
const osMutexAttr_t r1_subscriber_mutex_attr __attribute__((section(".r1.subscriber.attr"),aligned(4)))={
 .name=r1_subscriber_mutex_name,.attr_bits=0,.cb_mem=r1_subscriber_mutex_control,.cb_size=80
};
_Static_assert(sizeof(osStatus_t)==4 && sizeof(osMutexAttr_t)==16 &&
 offsetof(osMutexAttr_t,attr_bits)==4 && offsetof(osMutexAttr_t,cb_mem)==8 &&
 offsetof(osMutexAttr_t,cb_size)==12,"native subscriber CMSIS ABI");
osStatus_t r1_subscriber_lock(void)
{
 uint32_t mutex=r1_subscriber_mutex;
 if(!mutex){
  mutex=(uint32_t)(uintptr_t)osMutexNew(&r1_subscriber_mutex_attr);
  r1_subscriber_mutex=mutex;
 }
 return osMutexAcquire((osMutexId_t)(uintptr_t)mutex,osWaitForever);
}
osStatus_t r1_subscriber_unlock(void)
{
 uint32_t mutex=r1_subscriber_mutex;
 if(mutex)return osMutexRelease((osMutexId_t)(uintptr_t)mutex);
 return osOK;
}
