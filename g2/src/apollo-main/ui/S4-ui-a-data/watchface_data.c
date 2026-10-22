/* Dashboard watchface manager tables (S4-ui-a storage-definition pass, G2 2.2.6.10).
 *
 * Stock owner app\gui\dashboard\dashboard_watchface_manager.c: per-kind ops tables pointing at the layout1..4 handlers.
 * .data values come from the decoded scatter init streams (records 0x75d3f4
 * for 0x20000000.. and 0x75d404 for 0x20080000..); every other RAM cell is
 * zero-initialised (.bss 0x20004558.. / 0x2013be70..). ROM bytes are copied
 * from ota_s200_firmware_ota.bin (VA = file offset + 0x437fe0). Absolute
 * placement is a linker obligation; compiling this file does not establish
 * byte identity. */
#include <stdint.h>

#define VFP __attribute__((pcs("aapcs-vfp")))
/* Slot layout of the stock watchface ops table (0x3c bytes, 15 slots); the
 * arguments of slot 3 differ per layout (layout4 passes (unused, minute, hour)). */
typedef struct {
    int32_t (*create)(void *parent, int32_t x, const void *cfg);
    void (*deinit)(void);
    void (*set_x)(int32_t x);
    void (*set_time)(int32_t a, int32_t b, uint32_t c);
    void (*set_date)(uint32_t weekday, uint32_t month, uint32_t day, uint32_t date_format);
    VFP void (*set_weather)(uint16_t icon, uint32_t valid, uint32_t unit, float temperature);
    void (*set_battery)(uint8_t level);
    void (*set_value)(uint32_t value);
    void (*set_ble_connected)(uint32_t connected);
    void (*set_ring)(uint32_t paired, uint8_t battery);
    void (*set_ring_connected)(uint32_t connected);
    void (*set_ring_battery)(uint8_t level);
    void (*refresh_health)(void);
    void (*refresh_kind2)(void);
    void (*refresh_kind3)(void);
} g2_watchface_ops_t;
_Static_assert(sizeof(g2_watchface_ops_t) == 0x3cu, "watchface ops table");
extern int32_t layout1_create_5b7b60(void *parent, int32_t x, const void *cfg);
extern void layout1_deinit_5b824c(void);
extern void layout1_set_x_5b82cc(int32_t x);
extern void layout1_update_time_5b82e4(int32_t a, int32_t b, uint32_t c);
extern void layout1_update_date_5b8402(uint32_t weekday, uint32_t month, uint32_t day, uint32_t date_format);
extern VFP void layout1_update_weather_5b856c(uint16_t icon, uint32_t valid, uint32_t unit, float temperature);
extern void layout1_set_glasses_battery_5b8594(uint8_t level);
extern void layout1_update_value_5b871c(uint32_t value);
extern void layout1_set_ble_connected_5b8880(uint32_t connected);
extern void layout1_ring_presence_5b85d4(uint32_t paired, uint8_t battery);
extern void layout1_ring_connection_5b8666(uint32_t connected);
extern void layout1_ring_battery_5b86a0(uint8_t level);
extern void layout1_refresh_health_5b87bc(void);
extern void layout1_refresh_kind2_slots_5b8844(void);
extern void layout1_refresh_kind3_slots_5b8852(void);
const g2_watchface_ops_t g2_watchface_ops_kind1 = { /* ROM 0x713f54 */
    layout1_create_5b7b60,
    layout1_deinit_5b824c,
    layout1_set_x_5b82cc,
    layout1_update_time_5b82e4,
    layout1_update_date_5b8402,
    layout1_update_weather_5b856c,
    layout1_set_glasses_battery_5b8594,
    layout1_update_value_5b871c,
    layout1_set_ble_connected_5b8880,
    layout1_ring_presence_5b85d4,
    layout1_ring_connection_5b8666,
    layout1_ring_battery_5b86a0,
    layout1_refresh_health_5b87bc,
    layout1_refresh_kind2_slots_5b8844,
    layout1_refresh_kind3_slots_5b8852,
};
extern int32_t layout2_create_5b90e8(void *parent, int32_t x, const void *cfg);
extern void layout2_deinit_5b96b4(void);
extern void layout2_set_x_5b9748(int32_t x);
extern void layout2_set_time_5b9760(int32_t a, int32_t b, uint32_t c);
extern void layout2_set_date_5b97a0(uint32_t weekday, uint32_t month, uint32_t day, uint32_t date_format);
extern VFP void layout2_set_weather_5b9860(uint16_t icon, uint32_t valid, uint32_t unit, float temperature);
extern void layout2_set_battery_5b987e(uint8_t level);
extern void layout2_set_unread_count_5b9a38(uint32_t value);
extern void layout2_set_ble_connected_5b9a68(uint32_t connected);
extern void layout2_set_ring_paired_5b98aa(uint32_t paired, uint8_t battery);
extern void layout2_set_ring_connected_5b9954(uint32_t connected);
extern void layout2_set_ring_battery_5b9990(uint8_t level);
extern void layout2_refresh_health_5b9ba0(void);
extern void layout2_refresh_kind2_5b9c32(void);
extern void layout2_refresh_kind3_5b9c4c(void);
const g2_watchface_ops_t g2_watchface_ops_kind2 = { /* ROM 0x713fcc */
    layout2_create_5b90e8,
    layout2_deinit_5b96b4,
    layout2_set_x_5b9748,
    layout2_set_time_5b9760,
    layout2_set_date_5b97a0,
    layout2_set_weather_5b9860,
    layout2_set_battery_5b987e,
    layout2_set_unread_count_5b9a38,
    layout2_set_ble_connected_5b9a68,
    layout2_set_ring_paired_5b98aa,
    layout2_set_ring_connected_5b9954,
    layout2_set_ring_battery_5b9990,
    layout2_refresh_health_5b9ba0,
    layout2_refresh_kind2_5b9c32,
    layout2_refresh_kind3_5b9c4c,
};
extern int32_t layout3_create_5ba07c(void *parent, int32_t x, const void *cfg);
extern void layout3_deinit_5ba728(void);
extern void layout3_set_x_5ba792(int32_t x);
extern void layout3_set_time_5ba7ac(int32_t a, int32_t b, uint32_t c);
extern void layout3_set_date_5ba83c(uint32_t weekday, uint32_t month, uint32_t day, uint32_t date_format);
extern VFP void layout3_set_weather_5ba8a0(uint16_t icon, uint32_t valid, uint32_t unit, float temperature);
extern void layout3_set_battery_5ba8d8(uint8_t level);
extern void layout3_set_ble_connected_5bab24(uint32_t connected);
extern void layout3_set_ring_paired_5ba930(uint32_t paired, uint8_t battery);
extern void layout3_set_ring_connected_5ba9e4(uint32_t connected);
extern void layout3_set_ring_battery_5baa44(uint8_t level);
const g2_watchface_ops_t g2_watchface_ops_kind3 = { /* ROM 0x714008 */
    layout3_create_5ba07c,
    layout3_deinit_5ba728,
    layout3_set_x_5ba792,
    layout3_set_time_5ba7ac,
    layout3_set_date_5ba83c,
    layout3_set_weather_5ba8a0,
    layout3_set_battery_5ba8d8,
    0,
    layout3_set_ble_connected_5bab24,
    layout3_set_ring_paired_5ba930,
    layout3_set_ring_connected_5ba9e4,
    layout3_set_ring_battery_5baa44,
    0,
    0,
    0,
};
extern int32_t layout4_create_5bb36c(void *parent, int32_t x, const void *cfg);
extern void layout4_deinit_5bbaa8(void);
extern void layout4_set_x_5bbb00(int32_t x);
extern void layout4_update_time_5bbb1c(int32_t a, int32_t b, uint32_t c);
extern void layout4_set_battery_5bbb40(uint8_t level);
extern void layout4_set_ble_5bbb84(uint32_t connected);
extern void layout4_set_ring_5bbb8c(uint32_t paired, uint8_t battery);
extern void layout4_set_ring_connected_5bbc3c(uint32_t connected);
extern void layout4_set_ring_battery_5bbc80(uint8_t level);
const g2_watchface_ops_t g2_watchface_ops_kind4 = { /* ROM 0x7140bc */
    layout4_create_5bb36c,
    layout4_deinit_5bbaa8,
    layout4_set_x_5bbb00,
    layout4_update_time_5bbb1c,
    0,
    0,
    layout4_set_battery_5bbb40,
    0,
    layout4_set_ble_5bbb84,
    layout4_set_ring_5bbb8c,
    layout4_set_ring_connected_5bbc3c,
    layout4_set_ring_battery_5bbc80,
    0,
    0,
    0,
};
const g2_watchface_ops_t *g2_watchface_active_ops; /* RAM 0x200744bc */
