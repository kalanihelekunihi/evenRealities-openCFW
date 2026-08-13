/* Clean-room reconstruction of driver/chg/drv_bq25180.c. */

#include <stddef.h>
#include <stdint.h>

void *memset(void *destination, int value, size_t length);

enum {
    OPEN_CFW_BQ25180_ADDRESS = 0x6a,
    OPEN_CFW_BQ25180_REG_STAT0 = 0x00,
    OPEN_CFW_BQ25180_REG_STAT1 = 0x01,
    OPEN_CFW_BQ25180_REG_FLAG0 = 0x02,
    OPEN_CFW_BQ25180_REG_VBAT_CTRL = 0x03,
    OPEN_CFW_BQ25180_REG_ICHG_CTRL = 0x04,
    OPEN_CFW_BQ25180_REG_CHARGECTRL0 = 0x05,
    OPEN_CFW_BQ25180_REG_CHARGECTRL1 = 0x06,
    OPEN_CFW_BQ25180_REG_IC_CTRL = 0x07,
    OPEN_CFW_BQ25180_REG_TMR_ILIM = 0x08,
    OPEN_CFW_BQ25180_REG_SYS_REG = 0x0a,
    OPEN_CFW_BQ25180_REG_MASK_ID = 0x0c,
};

typedef struct {
    uint8_t reserved[0x14];
    uint8_t event;
    uint8_t alignment;
    uint16_t state;
} open_cfw_bq25180_runtime;

_Static_assert(offsetof(open_cfw_bq25180_runtime, event) == 0x14,
    "stock charger event byte must remain at offset 0x14");
_Static_assert(offsetof(open_cfw_bq25180_runtime, state) == 0x16,
    "stock charger state word must remain at offset 0x16");

#ifndef OPEN_CFW_BQ25180_RUNTIME_POINTER_ADDRESS
#define OPEN_CFW_BQ25180_RUNTIME_POINTER_ADDRESS 0x200744fcu
#endif
#ifndef OPEN_CFW_BQ25180_CHARGE_STATE_ADDRESS
#define OPEN_CFW_BQ25180_CHARGE_STATE_ADDRESS 0x20073b18u
#endif

#ifndef OPEN_CFW_BQ25180_BUS_READ
void open_cfw_bq25180_bus_read(
    uint8_t bus, uint8_t address, uint8_t reg, uint8_t *value
);
#define OPEN_CFW_BQ25180_BUS_READ(bus, address, reg, value) \
    open_cfw_bq25180_bus_read((bus), (address), (reg), (value))
#endif
#ifndef OPEN_CFW_BQ25180_BUS_WRITE
void open_cfw_bq25180_bus_write(
    uint8_t bus, uint8_t address, uint8_t reg, uint8_t value
);
#define OPEN_CFW_BQ25180_BUS_WRITE(bus, address, reg, value) \
    open_cfw_bq25180_bus_write((bus), (address), (reg), (value))
#endif
#ifndef OPEN_CFW_BQ25180_ASSERT
void open_cfw_bq25180_assert_failure(const char *expression);
#define OPEN_CFW_BQ25180_ASSERT(condition, expression) \
    do { \
        if (!(condition)) { \
            open_cfw_bq25180_assert_failure(expression); \
            for (;;) { \
            } \
        } \
    } while (0)
#endif
#ifndef OPEN_CFW_BQ25180_DIAGNOSTIC
#define OPEN_CFW_BQ25180_DIAGNOSTIC(code) ((void)(code))
#endif

#define OPEN_CFW_BQ25180_RUNTIME \
    (*(open_cfw_bq25180_runtime **)(uintptr_t) \
        OPEN_CFW_BQ25180_RUNTIME_POINTER_ADDRESS)
#define OPEN_CFW_BQ25180_CHARGE_STATE \
    (*(volatile uint32_t *)(uintptr_t)OPEN_CFW_BQ25180_CHARGE_STATE_ADDRESS)

static int open_cfw_bq25180_write_register(uint8_t reg, uint8_t value)
{
    OPEN_CFW_BQ25180_BUS_WRITE(
        7u, OPEN_CFW_BQ25180_ADDRESS, reg, value
    );
    return 0;
}

static int open_cfw_bq25180_read_register(uint8_t reg)
{
    uint8_t value = 0u;
    OPEN_CFW_BQ25180_BUS_READ(
        7u, OPEN_CFW_BQ25180_ADDRESS, reg, &value
    );
    return value;
}

static uint8_t open_cfw_bq25180_update_field(
    uint8_t reg, uint8_t shift, uint8_t mask, uint8_t value
)
{
    uint8_t current = (uint8_t)open_cfw_bq25180_read_register(reg);
    current = (uint8_t)(
        (current & (uint8_t)~(uint8_t)(mask << shift)) |
        (uint8_t)(value << shift)
    );
    (void)open_cfw_bq25180_write_register(reg, current);
    return value;
}

static void open_cfw_bq25180_configure_event_mask(
    uint8_t events, uint8_t enabled
)
{
    uint8_t masked = enabled == 0u;
    if ((events & 0x01u) != 0u) {
        open_cfw_bq25180_update_field(0x06u, 2u, 1u, masked);
    }
    if ((events & 0x02u) != 0u) {
        open_cfw_bq25180_update_field(0x06u, 1u, 1u, masked);
    }
    if ((events & 0x04u) != 0u) {
        open_cfw_bq25180_update_field(0x06u, 0u, 1u, masked);
    }
    if ((events & 0x08u) != 0u) {
        open_cfw_bq25180_update_field(0x0cu, 7u, 1u, masked);
    }
    if ((events & 0x10u) != 0u) {
        open_cfw_bq25180_update_field(0x0cu, 6u, 1u, masked);
    }
    if ((events & 0x20u) != 0u) {
        open_cfw_bq25180_update_field(0x0cu, 5u, 1u, masked);
    }
    if ((events & 0x40u) != 0u) {
        open_cfw_bq25180_update_field(0x0cu, 4u, 1u, masked);
    }
}

static void open_cfw_bq25180_mask_events(uint8_t events)
{
    open_cfw_bq25180_configure_event_mask(events, 0u);
}

int open_cfw_bq25180_read_event(uint8_t *event)
{
    int value;
    OPEN_CFW_BQ25180_ASSERT(event != NULL, "p != NULL");
    value = open_cfw_bq25180_read_register(OPEN_CFW_BQ25180_REG_FLAG0);
    if (value < 0) {
        return 0;
    }
    memset(event, 0, 1u);
    *event = (uint8_t)value;
    return 1;
}

int open_cfw_bq25180_read_state(uint16_t *state)
{
    int stat0;
    int stat1;
    OPEN_CFW_BQ25180_ASSERT(state != NULL, "p != NULL");
    stat0 = open_cfw_bq25180_read_register(OPEN_CFW_BQ25180_REG_STAT0);
    stat1 = open_cfw_bq25180_read_register(OPEN_CFW_BQ25180_REG_STAT1);
    if (stat0 < 0 || stat1 < 0) {
        return 0;
    }
    memset(state, 0, 2u);
    *state = (uint16_t)((uint8_t)stat0 | ((uint16_t)(uint8_t)stat1 << 8));
    OPEN_CFW_BQ25180_CHARGE_STATE = (*state & 0x7fu) >> 5;
    return 1;
}

int open_cfw_bq25180_read_device_id(void)
{
    int value = open_cfw_bq25180_read_register(OPEN_CFW_BQ25180_REG_MASK_ID);
    if (value < 1) {
        OPEN_CFW_BQ25180_DIAGNOSTIC(1u);
        return -1;
    }
    OPEN_CFW_BQ25180_DIAGNOSTIC(2u);
    return value & 0x0f;
}

void open_cfw_bq25180_set_charge_enabled(uint8_t enabled)
{
    open_cfw_bq25180_update_field(0x04u, 7u, 1u, enabled == 0u);
}

void open_cfw_bq25180_set_ts_enabled(uint8_t enabled)
{
    open_cfw_bq25180_update_field(0x07u, 7u, 1u, enabled);
}

void open_cfw_bq25180_set_safety_timer(uint8_t setting)
{
    open_cfw_bq25180_update_field(0x07u, 2u, 3u, setting);
}

void open_cfw_bq25180_set_watchdog(uint8_t setting)
{
    open_cfw_bq25180_update_field(0x07u, 0u, 3u, setting);
}

void open_cfw_bq25180_set_battery_regulation_voltage(uint16_t millivolts)
{
    OPEN_CFW_BQ25180_ASSERT(
        millivolts >= 3500u && millivolts <= 4650u,
        "millivoltage >= MIN_BAT_REG_mV && millivoltage <= MAX_BAT_REG_mV"
    );
    (void)open_cfw_bq25180_write_register(
        OPEN_CFW_BQ25180_REG_VBAT_CTRL,
        (uint8_t)((millivolts - 3500u) / 10u)
    );
}

void open_cfw_bq25180_set_battery_overcurrent(uint8_t setting)
{
    open_cfw_bq25180_update_field(0x06u, 6u, 3u, setting);
}

void open_cfw_bq25180_set_battery_undervoltage_lockout(uint16_t millivolts)
{
    uint8_t setting;
    OPEN_CFW_BQ25180_ASSERT(
        millivolts >= 2000u && millivolts <= 3000u,
        "millivoltage >= MIN_BAT_UNDERVOLTAGE_mV && millivoltage <= MAX_BAT_UNDERVOLTAGE_mV"
    );
    if (millivolts >= 2801u) {
        setting = 2u;
    } else if (millivolts >= 2601u) {
        setting = 3u;
    } else if (millivolts >= 2401u) {
        setting = 4u;
    } else if (millivolts >= 2201u) {
        setting = 5u;
    } else if (millivolts >= 2001u) {
        setting = 6u;
    } else {
        setting = 7u;
    }
    open_cfw_bq25180_update_field(0x06u, 3u, 7u, setting);
}

void open_cfw_bq25180_set_precharge_threshold(uint16_t millivolts)
{
    open_cfw_bq25180_update_field(0x07u, 6u, 1u, millivolts < 2801u);
}

void open_cfw_bq25180_set_precharge_ratio(uint8_t ratio)
{
    open_cfw_bq25180_update_field(0x05u, 6u, 1u, ratio < 2u);
}

void open_cfw_bq25180_set_fastcharge_current(uint16_t milliamps)
{
    uint8_t setting;
    OPEN_CFW_BQ25180_ASSERT(
        milliamps >= 5u && milliamps <= 1000u,
        "milliampere >= MIN_IN_CURR_mA && milliampere <= MAX_IN_CURR_mA"
    );
    if (milliamps <= 35u) {
        setting = (uint8_t)(milliamps - 5u);
    } else {
        uint16_t converted = (uint16_t)(milliamps / 10u + 27u);
        setting = converted < 128u ? (uint8_t)converted : 127u;
    }
    open_cfw_bq25180_update_field(0x04u, 0u, 0x7fu, setting);
}

void open_cfw_bq25180_set_termination_percent(uint8_t percent)
{
    uint8_t setting = percent >= 20u ? 3u :
        (percent >= 10u ? 2u : (percent >= 5u ? 1u : 0u));
    open_cfw_bq25180_update_field(0x05u, 4u, 3u, setting);
}

void open_cfw_bq25180_set_vindpm(uint8_t setting)
{
    open_cfw_bq25180_update_field(0x05u, 2u, 3u, setting);
}

void open_cfw_bq25180_set_vdppm_enabled(uint8_t enabled)
{
    open_cfw_bq25180_update_field(0x0au, 0u, 1u, enabled == 0u);
}

void open_cfw_bq25180_set_input_current_limit(uint16_t milliamps)
{
    uint8_t setting;
    if (milliamps >= 1100u) {
        setting = 7u;
    } else if (milliamps >= 700u) {
        setting = 6u;
    } else if (milliamps >= 500u) {
        setting = 5u;
    } else if (milliamps >= 400u) {
        setting = 4u;
    } else if (milliamps >= 300u) {
        setting = 3u;
    } else if (milliamps >= 200u) {
        setting = 2u;
    } else if (milliamps >= 100u) {
        setting = 1u;
    } else {
        setting = 0u;
    }
    open_cfw_bq25180_update_field(0x08u, 0u, 7u, setting);
}

void open_cfw_bq25180_set_system_mode(uint8_t setting)
{
    open_cfw_bq25180_update_field(0x0au, 2u, 3u, setting);
}

void open_cfw_bq25180_set_system_voltage(uint8_t setting)
{
    open_cfw_bq25180_update_field(0x0au, 5u, 7u, setting);
}

void open_cfw_bq25180_set_ts_auto_enabled(uint8_t enabled)
{
    open_cfw_bq25180_update_field(0x07u, 7u, 1u, enabled);
}

static void open_cfw_bq25180_apply_defaults(void)
{
    open_cfw_bq25180_set_charge_enabled(0u);
    open_cfw_bq25180_set_ts_enabled(0u);
    open_cfw_bq25180_set_fastcharge_current(91u);
    open_cfw_bq25180_set_input_current_limit(1000u);
    open_cfw_bq25180_set_precharge_ratio(2u);
    open_cfw_bq25180_set_termination_percent(10u);
    open_cfw_bq25180_set_battery_overcurrent(0u);
    open_cfw_bq25180_set_system_voltage(1u);
    open_cfw_bq25180_set_battery_regulation_voltage(4400u);
    open_cfw_bq25180_set_vindpm(1u);
    open_cfw_bq25180_set_battery_undervoltage_lockout(2800u);
    open_cfw_bq25180_set_precharge_threshold(2800u);
    open_cfw_bq25180_set_system_mode(0u);
    open_cfw_bq25180_set_vdppm_enabled(0u);
    open_cfw_bq25180_set_safety_timer(1u);
    open_cfw_bq25180_set_watchdog(0u);
    open_cfw_bq25180_set_ts_auto_enabled(0u);
    open_cfw_bq25180_mask_events(0x7fu);
    open_cfw_bq25180_set_charge_enabled(1u);
}

int open_cfw_bq25180_refresh_status(void)
{
    open_cfw_bq25180_runtime *runtime = OPEN_CFW_BQ25180_RUNTIME;
    (void)open_cfw_bq25180_read_event(&runtime->event);
    (void)open_cfw_bq25180_read_state(&runtime->state);
    return 0;
}

int open_cfw_bq25180_hardware_init(void)
{
    int device_id;
    OPEN_CFW_BQ25180_DIAGNOSTIC(3u);
    device_id = open_cfw_bq25180_read_device_id();
    if (device_id != 0) {
        OPEN_CFW_BQ25180_DIAGNOSTIC(4u);
        return -1;
    }
    open_cfw_bq25180_apply_defaults();
    OPEN_CFW_BQ25180_DIAGNOSTIC(5u);
    return 0;
}
