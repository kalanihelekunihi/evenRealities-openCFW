#include <stdint.h>

extern uint32_t open_cfw_test_ring_battery_list;
extern const char open_cfw_test_ring_battery_type[];

#define OPEN_CFW_CB_RING_BAT_LIST ((void *)&open_cfw_test_ring_battery_list)
#define OPEN_CFW_CB_RING_BAT_TYPE open_cfw_test_ring_battery_type
#define OPEN_CFW_CB_RING_BAT_CONSUMER(event, value) \
    open_cfw_test_ring_battery_consumer((event), (value))
#define OPEN_CFW_CALLBACK_LIST_INIT(list, type) \
    open_cfw_test_ring_battery_init((list), (type))
#define OPEN_CFW_CALLBACK_LIST_DEINIT(list) \
    open_cfw_test_ring_battery_deinit((list))
#define OPEN_CFW_CALLBACK_REGISTER(list, callback) \
    open_cfw_test_ring_battery_register((list), (callback))
#define OPEN_CFW_CALLBACK_NOTIFY(list, event, value) \
    open_cfw_test_ring_battery_notify((list), (event), (uintptr_t)(value))

void open_cfw_test_ring_battery_consumer(uint32_t event, uint32_t *value);
uint32_t open_cfw_test_ring_battery_init(void *list, const char *type);
void open_cfw_test_ring_battery_deinit(void *list);
uint32_t open_cfw_test_ring_battery_register(void *list, uintptr_t callback);
void open_cfw_test_ring_battery_notify(void *list, uint32_t event,
    uintptr_t value);
