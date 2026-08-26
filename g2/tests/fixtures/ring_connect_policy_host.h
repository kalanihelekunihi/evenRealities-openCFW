#ifndef OPEN_CFW_RING_CONNECT_POLICY_HOST_H
#define OPEN_CFW_RING_CONNECT_POLICY_HOST_H

#include <stdint.h>

struct open_cfw_ring_policy_state;
extern struct open_cfw_ring_policy_state host_ring_policy_state;
extern uint32_t host_ring_policy_tick;
extern uint32_t host_ring_policy_throttle_tick;
extern uint8_t host_ring_policy_pending;

uint8_t host_ring_policy_remove(void (*callback)(uint32_t));
void host_ring_policy_push(
    void (*callback)(uint32_t), uint32_t argument, uint32_t delay);
void host_ring_policy_notify(uint32_t value);
uint32_t host_ring_policy_is_owner(void);

#define OPEN_CFW_RING_POLICY_STATE host_ring_policy_state
#define OPEN_CFW_RING_POLICY_THROTTLE_TICK host_ring_policy_throttle_tick
#define OPEN_CFW_RING_POLICY_RECONNECT_PENDING host_ring_policy_pending
#define OPEN_CFW_RING_POLICY_TICK() (host_ring_policy_tick)
#define OPEN_CFW_RING_POLICY_REMOVE(callback) \
    host_ring_policy_remove((callback))
#define OPEN_CFW_RING_POLICY_PUSH(callback, argument, delay) \
    host_ring_policy_push((callback), (argument), (delay))
#define OPEN_CFW_RING_POLICY_NOTIFY(value) host_ring_policy_notify((value))
#define OPEN_CFW_RING_POLICY_IS_OWNER() host_ring_policy_is_owner()

#endif
