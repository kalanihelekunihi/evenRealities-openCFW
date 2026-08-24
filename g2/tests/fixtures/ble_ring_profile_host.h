#ifndef OPEN_CFW_BLE_RING_PROFILE_HOST_H
#define OPEN_CFW_BLE_RING_PROFILE_HOST_H
#include <stdint.h>
struct open_cfw_ring_control;
extern struct open_cfw_ring_control open_cfw_test_ring_control;
extern const uint8_t open_cfw_test_ring_uuid[16];
extern const uint32_t open_cfw_test_ring_characteristics;
#define OPEN_CFW_RING_CONTROL (&open_cfw_test_ring_control)
#define OPEN_CFW_RING_SERVICE_UUID open_cfw_test_ring_uuid
#define OPEN_CFW_RING_DISCOVERY_CHARACTERISTICS \
    ((const void *)&open_cfw_test_ring_characteristics)
#define OPEN_CFW_RING_CONNECTION_IN_USE(i) open_cfw_test_ring_in_use(i)
#define OPEN_CFW_RING_WRITE_REQUEST(...) open_cfw_test_ring_write_request(__VA_ARGS__)
#define OPEN_CFW_RING_DISCOVER_SERVICE(...) open_cfw_test_ring_discover(__VA_ARGS__)
#define OPEN_CFW_RING_CONNECTION_ROLE(i) open_cfw_test_ring_role(i)
#define OPEN_CFW_RING_WRITE_COMMAND(...) open_cfw_test_ring_write_command(__VA_ARGS__)
#define OPEN_CFW_RING_REMOVE_DELAYED(c) open_cfw_test_ring_remove(c)
#define OPEN_CFW_RING_PUSH_DELAYED(...) open_cfw_test_ring_push(__VA_ARGS__)
#define OPEN_CFW_RING_THREAD_EVENT(e) open_cfw_test_ring_thread_event(e)
#define OPEN_CFW_RING_THREAD_MESSAGE(d,n) open_cfw_test_ring_thread_message((d),(n))
#define OPEN_CFW_RING_WAIT_TX_READY() open_cfw_test_ring_wait()
#define OPEN_CFW_RING_TX_COMPLETE_NOTIFY() open_cfw_test_ring_complete()
#define OPEN_CFW_RING_MESSAGE_ALLOC(n) open_cfw_test_ring_alloc(n)
#define OPEN_CFW_RING_MESSAGE_SEND(h,m) open_cfw_test_ring_send((h),(m))
#define OPEN_CFW_RING_DELAY_CALLBACK open_cfw_ring_enable_ccc
uint8_t open_cfw_test_ring_in_use(uint8_t);
void open_cfw_test_ring_write_request(uint8_t,uint16_t,uint16_t,const uint8_t*);
void open_cfw_test_ring_discover(uint8_t,uint8_t,const uint8_t*,uint8_t,const void*,uint16_t*);
uint8_t open_cfw_test_ring_role(uint8_t);
void open_cfw_test_ring_write_command(uint8_t,uint16_t,uint16_t,const uint8_t*);
uint8_t open_cfw_test_ring_remove(void(*)(void*));
void open_cfw_test_ring_push(void(*)(void*),void*,uint32_t);
void open_cfw_test_ring_thread_event(uint32_t);
void open_cfw_test_ring_thread_message(const uint8_t*,uint16_t);
void open_cfw_test_ring_wait(void);
void open_cfw_test_ring_complete(void);
void *open_cfw_test_ring_alloc(uint16_t);
void open_cfw_test_ring_send(uint8_t,void*);
void open_cfw_test_ring_reset(void);
uint16_t *open_cfw_test_ring_handles(void);
void open_cfw_test_ring_set(uint32_t,uint32_t);
uint32_t open_cfw_test_ring_word(uint32_t);
#endif
