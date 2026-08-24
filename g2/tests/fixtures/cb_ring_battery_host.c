#include <stdint.h>
#include <string.h>

uint32_t open_cfw_test_ring_battery_list;
const char open_cfw_test_ring_battery_type[] = "RING_BAT_INFO";
static uint32_t words[16];

void open_cfw_test_ring_battery_reset(void)
{
    uint32_t index;
    for (index = 0u; index < 16u; index++) {
        words[index] = 0u;
    }
}

uint32_t open_cfw_test_ring_battery_word(uint32_t index)
{
    return index < 16u ? words[index] : 0u;
}

void open_cfw_test_ring_battery_set(uint32_t index, uint32_t value)
{
    if (index < 16u) {
        words[index] = value;
    }
}

void open_cfw_test_ring_battery_consumer(uint32_t event, uint32_t *value)
{
    words[0]++;
    words[1] = event;
    words[2] = *value;
    *value += words[3];
}

uint32_t open_cfw_test_ring_battery_init(void *list, const char *type)
{
    words[4]++;
    words[5] = list == &open_cfw_test_ring_battery_list;
    words[6] = type != 0 && strcmp(type, "RING_BAT_INFO") == 0;
    return 1u;
}

void open_cfw_test_ring_battery_deinit(void *list)
{
    words[7]++;
    words[8] = list == &open_cfw_test_ring_battery_list;
}

uint32_t open_cfw_test_ring_battery_register(void *list, uintptr_t callback)
{
    words[9]++;
    words[10] = list == &open_cfw_test_ring_battery_list;
    words[11] = (uint32_t)callback;
    return words[12];
}

void open_cfw_test_ring_battery_notify(void *list, uint32_t event,
    uintptr_t value)
{
    uint32_t *word = (uint32_t *)value;
    words[13]++;
    words[14] = (list == &open_cfw_test_ring_battery_list) ? event : 0u;
    words[15] = *word;
    *word += words[3];
}
