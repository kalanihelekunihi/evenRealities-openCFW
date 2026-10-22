/* Power-path storage (S1 storage-definition pass, 2.2.6.10).
 *
 * Stock owners: driver\bq27427 (fuel-gauge DM descriptors and unseal key),
 * driver\bq25180 (charger runtime pointer), the nPM1300 glue
 * (npmx_main_driver.c: backend record, fuel-gauge poll timing), the box UART
 * manager and service_ring_battery.c. .data values are from the decoded
 * 0x20000000 init stream (scatter record 0x75d3f4); all other cells are in
 * the zero-init range 0x20004558..0x20075048 or SSRAM zero-init. */
#include <stddef.h>
#include <stdint.h>

/* ---- drv_bq27427.c ------------------------------------------------------ */

/* RAM 0x200006e8 (.data): CONTROL unseal key words, 00 80 00 80. */
uint32_t g2_bq27427_unseal_key = 0x80008000u;

typedef struct {
    uint8_t subclass; /* +0 */
    uint8_t offset;   /* +1 */
    uint8_t size;     /* +2 */
    uint8_t pad;      /* +3 */
    uint16_t min;     /* +4 */
    uint16_t max;     /* +6 */
} g2_bq27427_dm_desc_t;
_Static_assert(sizeof(g2_bq27427_dm_desc_t) == 8u, "DM descriptor stride");

/* RAM 0x200006ec..0x20000723 (.data), seven descriptors. */
g2_bq27427_dm_desc_t g2_bq27427_dm_desc_table[7] = {
    {0x52u, 0x06u, 2u, 0u, 0x0000u, 0x1f40u}, /* design capacity */
    {0x52u, 0x08u, 2u, 0u, 0x0000u, 0x7fffu}, /* design energy */
    {0x52u, 0x0au, 2u, 0u, 0x0bb8u, 0x1130u}, /* terminate voltage */
    {0x40u, 0x04u, 1u, 0u, 0x0000u, 0x00ffu}, /* registers byte 4 */
    {0x52u, 0x02u, 1u, 0u, 0x0000u, 0x00ffu}, /* update status */
    {0x51u, 0x00u, 2u, 0u, 0x0000u, 0x07d0u}, /* current thresholds */
    {0x69u, 0x05u, 1u, 0u, 0x0000u, 0x7fffu}, /* subclass 105 byte 5 */
};

/* ---- drv_bq25180.c ------------------------------------------------------ */

void *g2_charger_runtime; /* RAM 0x200744fc, g2_charger_runtime_t * */

/* ---- npmx_main_driver.c (product glue) ---------------------------------- */

typedef uint32_t (*g2_npmx_backend_fn_t)(void *p_context, uint32_t register_address,
                                         uint8_t *p_data, size_t num_of_bytes);
typedef struct {
    g2_npmx_backend_fn_t write; /* +0x0 */
    g2_npmx_backend_fn_t read;  /* +0x4 */
    void *p_context;            /* +0x8 */
} g2_npmx_backend_t;
_Static_assert(sizeof(g2_npmx_backend_t) == 12u, "npmx_backend_t");

g2_npmx_backend_t g2_npmx_backend;   /* RAM 0x20074068 */
void *g2_npmx_backend_context;       /* RAM 0x2007482c */
uint8_t g2_npmx_last_charger_status; /* RAM 0x20074ff0 */
uint8_t g2_fuel_gauge_initialized;   /* RAM 0x20074fef */
uint32_t g2_fuel_gauge_ref_time;     /* RAM 0x2007481c, tick of the previous poll */
uint32_t g2_fuel_gauge_now_tick;     /* RAM 0x20074820 */
uint32_t g2_fuel_gauge_delta_ms;     /* RAM 0x20074824 */
float g2_fuel_gauge_t_delta;         /* RAM 0x20074828, seconds (zero-init) */

/* ---- box_uart_mgr.c ----------------------------------------------------- */

uint8_t g2_box_uart_rx_slot; /* RAM 0x20074f96 */
/* RAM 0x2005ba68..0x2005ce67: five 1 KiB receive slots. */
__attribute__((aligned(4))) uint8_t g2_box_uart_rx_buffers[5][0x400];

/* ---- service_ring_battery.c --------------------------------------------- */

/* RAM 0x20074f3a: {level, is_charging}. */
__attribute__((aligned(2))) uint8_t g2_ring_battery_state[2];
