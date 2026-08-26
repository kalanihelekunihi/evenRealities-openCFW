#include <stdint.h>

struct open_cfw_ring_policy_state {
    uint8_t mode;
    uint8_t reserved[3];
    uint32_t started_at;
    uint8_t connect_info_processed;
};

struct open_cfw_ring_policy_state host_ring_policy_state;
uint32_t host_ring_policy_tick;
uint32_t host_ring_policy_throttle_tick;
uint8_t host_ring_policy_pending;
uint32_t host_ring_policy_owner;
uint32_t host_ring_policy_notify_value;
uint32_t host_ring_policy_notify_count;
uint32_t host_ring_policy_remove_count;
uint32_t host_ring_policy_push_count;
uint32_t host_ring_policy_delay;
uintptr_t host_ring_policy_argument;
uintptr_t host_ring_policy_last_removed;
uintptr_t host_ring_policy_last_pushed;

uint8_t host_ring_policy_remove(void (*callback)(uint32_t))
{
    ++host_ring_policy_remove_count;
    host_ring_policy_last_removed = (uintptr_t)callback;
    return 1u;
}

void host_ring_policy_push(
    void (*callback)(uint32_t), uint32_t argument, uint32_t delay)
{
    ++host_ring_policy_push_count;
    host_ring_policy_last_pushed = (uintptr_t)callback;
    host_ring_policy_argument = argument;
    host_ring_policy_delay = delay;
}

void host_ring_policy_notify(uint32_t value)
{
    ++host_ring_policy_notify_count;
    host_ring_policy_notify_value = value;
}

uint32_t host_ring_policy_is_owner(void)
{
    return host_ring_policy_owner;
}

void PB_TxEncodeNotifyRingConnectInfo(uint32_t value)
{
    host_ring_policy_notify(value);
}
