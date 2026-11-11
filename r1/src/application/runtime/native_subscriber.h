#ifndef R1_NATIVE_SUBSCRIBER_H
#define R1_NATIVE_SUBSCRIBER_H
#include <stdint.h>
#include "cmsis_os2.h"
extern volatile uint32_t r1_subscriber_mutex;
extern uint32_t r1_subscriber_mutex_control[20];
extern const char r1_subscriber_mutex_name[12];
extern const osMutexAttr_t r1_subscriber_mutex_attr;
osStatus_t r1_subscriber_lock(void),r1_subscriber_unlock(void);
osStatus_t r1_event_service_0008b0fc(volatile uint8_t *);
void r1_subscriber_invoke(uint32_t,uint32_t);
extern void *volatile r1_subscriber_roots[5];
uint32_t r1_subscriber_register(uint32_t,uint32_t,uint32_t);
struct r1_subscriber_route {void **thread; uint16_t event_id,reserved;};
extern const struct r1_subscriber_route r1_subscriber_routes[2];
uint32_t r1_event_service_0008b028(uint32_t,const void *,uint32_t);
#endif
