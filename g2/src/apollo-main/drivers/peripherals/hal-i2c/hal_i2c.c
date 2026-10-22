/* Product I2C HAL, stock D:\01_workspace\s200_ap510b_iar_git\driver\hal\src\hal_i2c.c.
 * Native 0x50412c..0x50475b; literal pool 0x50475c..0x504783.
 *
 * The bus table at RAM 0x20000c4c (initialised data) holds one 16-byte row per
 * IOM module. The stock names hal_i2c_power_down/power_up are kept as anchors,
 * but power_down wakes the IOM and restores the bus pins before a transfer and
 * power_up returns it to deep sleep afterwards. */
#include <stdint.h>
#include <stddef.h>
#include "g2_hal_i2c.h"

typedef struct {
    uint32_t scl;     /* +0x0 */
    uint32_t sda;     /* +0x4 */
    uint32_t scl_cfg; /* +0x8 am_hal_gpio_pincfg_t */
    uint32_t sda_cfg; /* +0xc */
} g2_i2c_pins_t;

typedef struct {
    uint32_t module;             /* +0x0 IOM module number */
    void *handle;                /* +0x4 filled by am_hal_iom_initialize */
    const g2_i2c_pins_t *pins;   /* +0x8 */
    const void *config;          /* +0xc am_hal_iom_config_t */
} g2_i2c_bus_t;

/* am_hal_iom_transfer_t in the stock (pre-SDK-5.2, IAR one-byte enum) layout. */
typedef struct {
    uint32_t dev_addr;      /* +0x00 uPeerInfo.ui32I2CDevAddr */
    uint32_t instr_len;     /* +0x04 */
    uint64_t instr;         /* +0x08 */
    uint32_t num_bytes;     /* +0x10 */
    uint8_t direction;      /* +0x14 0 = TX, 1 = RX */
    const void *tx;         /* +0x18 */
    void *rx;               /* +0x1c */
    uint8_t do_continue;    /* +0x20 */
    uint8_t repeat_count;   /* +0x21 */
    uint8_t priority;       /* +0x22 */
    uint32_t pause;         /* +0x24 */
    uint32_t status_setclr; /* +0x28 */
} g2_iom_transfer_t;
_Static_assert(sizeof(g2_iom_transfer_t) == 0x30, "stock IOM transaction is 48 bytes");

enum { IOM_TX = 0u, IOM_RX = 1u };
enum { POWER_WAKE = 0u, POWER_DEEPSLEEP = 2u };
#define IOM4_IRQ 10
#define POWER_RETRIES 1000

extern g2_i2c_bus_t g2_i2c_bus_table[G2_HAL_I2C_BUS_COUNT]; /* RAM 0x20000c4c */
extern void *g2_i2c_bus_mutex[G2_HAL_I2C_BUS_COUNT];       /* RAM 0x200738fc */
extern void *g2_i2c4_semaphore;                            /* RAM 0x2007460c */
extern const uint32_t g2_audio_clock_pin_config;           /* ROM 0x78ee48, disabled pad */

extern uint32_t am_hal_iom_initialize_55c2bc(uint32_t module, void **handle);
extern uint32_t am_hal_iom_enable_55c32e(void *handle);
extern uint32_t am_hal_iom_interrupt_enable_55c498(void *handle, uint32_t mask);
extern uint32_t am_hal_iom_interrupt_status_get_55c4d0(void *handle, uint8_t enabled_only, uint32_t *status);
extern uint32_t am_hal_iom_interrupt_clear_55c518(void *handle, uint32_t status);
extern uint32_t am_hal_iom_interrupt_service_55c558(void *handle, uint32_t status);
extern uint32_t am_hal_iom_power_ctrl_55c7e8(void *handle, uint32_t state, uint8_t retain);
extern uint32_t am_hal_iom_configure_55ca94(void *handle, const void *config);
extern uint32_t am_hal_iom_blocking_transfer_55cc1c(void *handle, g2_iom_transfer_t *txn);
extern uint32_t am_hal_gpio_pinconfig_480f0c(uint32_t pin, uint32_t config);
extern void g2_delay_ms_4910f4(uint32_t ms);
extern void *osMutexNew(const void *attr);
extern int32_t osMutexAcquire(void *mutex, uint32_t timeout);
extern int32_t osMutexRelease(void *mutex);
extern void *osSemaphoreNew(uint32_t max, uint32_t initial, const void *attr);
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...);

static const char module_tag[] = "hal.i2c"; /* ROM 0x78d6d4 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\hal\\src\\hal_i2c.c"; /* ROM 0x70c124 */
static const char init_fn[] = "HAL_I2CInit"; /* ROM 0x78ab08 */
static const char sem_error[] = "Error - Failed to create semaphore for I2C4."; /* ROM 0x734544 */
static const char sem_error_short[] = "[hal.i2c]Error - Failed to create semaphore for I2C4."; /* ROM 0x71f598 */

void hal_i2c_irq_enable(int16_t irq) {
    if (irq >= 0)
        ((volatile uint32_t *)0xe000e100u)[(uint32_t)irq >> 5] = 1u << ((uint32_t)irq & 31u);
}

uint32_t hal_i2c_power_down(uint8_t bus) {
    uint32_t status = 0;
    for (int i = 0; i < POWER_RETRIES; i++) {
        status = am_hal_iom_power_ctrl_55c7e8(g2_i2c_bus_table[bus].handle, POWER_WAKE, 1u);
        if (status == 0u)
            break;
        g2_delay_ms_4910f4(10u);
    }
    const g2_i2c_pins_t *pins = g2_i2c_bus_table[bus].pins;
    (void)am_hal_gpio_pinconfig_480f0c(pins->scl, pins->scl_cfg);
    (void)am_hal_gpio_pinconfig_480f0c(pins->sda, pins->sda_cfg);
    return status != 0u ? 4u : 0u;
}

uint32_t hal_i2c_power_up(uint8_t bus) {
    uint32_t status = 0;
    if (bus == 4u) {
        (void)am_hal_gpio_pinconfig_480f0c(g2_i2c_bus_table[bus].pins->scl, g2_audio_clock_pin_config);
        (void)am_hal_gpio_pinconfig_480f0c(g2_i2c_bus_table[bus].pins->sda, g2_audio_clock_pin_config);
    }
    for (int i = 0; i < POWER_RETRIES; i++) {
        status = am_hal_iom_power_ctrl_55c7e8(g2_i2c_bus_table[bus].handle, POWER_DEEPSLEEP, 1u);
        if (status == 0u)
            break;
        g2_delay_ms_4910f4(10u);
    }
    return status != 0u ? 4u : 0u;
}

uint32_t HAL_I2CInit(void) {
    uint32_t status = 0;
    for (uint32_t bus = 0; bus < G2_HAL_I2C_BUS_COUNT; bus++) {
        g2_i2c_bus_t *row = &g2_i2c_bus_table[bus];
        if (row->pins == NULL || row->config == NULL)
            continue;
        if (g2_i2c_bus_mutex[bus] == NULL) {
            g2_i2c_bus_mutex[bus] = osMutexNew(NULL);
            if (g2_i2c_bus_mutex[bus] == NULL)
                return 1u;
        }
        (void)am_hal_iom_initialize_55c2bc(row->module, &row->handle);
        if (am_hal_gpio_pinconfig_480f0c(row->pins->scl, row->pins->scl_cfg) != 0u)
            return 1u;
        if (am_hal_gpio_pinconfig_480f0c(row->pins->sda, row->pins->sda_cfg) != 0u)
            return 1u;
        (void)am_hal_iom_power_ctrl_55c7e8(row->handle, POWER_WAKE, 0u);
        (void)am_hal_iom_configure_55ca94(row->handle, row->config);
        status = am_hal_iom_enable_55c32e(row->handle);
        (void)hal_i2c_power_up((uint8_t)bus);
    }
    (void)am_hal_iom_interrupt_enable_55c498(g2_i2c_bus_table[4].handle, 0xffu);
    hal_i2c_irq_enable(IOM4_IRQ);
    g2_i2c4_semaphore = osSemaphoreNew(1u, 0u, NULL);
    if (g2_i2c4_semaphore == NULL) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, init_fn, 0x131u, sem_error);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x04000000u, sem_error_short, sem_error_short);
        status = 1u;
    }
    return status;
}

/* Shared tail of every transfer: sleep the IOM and drop the bus lock. */
static uint32_t finish(uint8_t bus, uint32_t transfer_status) {
    uint32_t sleep_status = hal_i2c_power_up(bus);
    if (g2_i2c_bus_mutex[bus] != NULL)
        (void)osMutexRelease(g2_i2c_bus_mutex[bus]);
    return (transfer_status != 0u || sleep_status != 0u) ? 1u : 0u;
}

static void begin(uint8_t bus) {
    if (g2_i2c_bus_mutex[bus] != NULL)
        (void)osMutexAcquire(g2_i2c_bus_mutex[bus], UINT32_MAX);
    (void)hal_i2c_power_down(bus);
}

/* Write tx then read rx as two separate (non-continued) transactions. */
uint32_t hal_i2c_transfer_full(uint8_t bus, uint8_t addr, const void *tx, uint32_t tx_len,
                               void *rx, uint32_t rx_len) {
    g2_iom_transfer_t txn = {0};
    if (bus >= G2_HAL_I2C_BUS_COUNT)
        return 1u;
    begin(bus);
    txn.priority = 1u;
    txn.direction = IOM_TX;
    txn.do_continue = 0u;
    txn.dev_addr = addr;
    txn.num_bytes = tx_len;
    txn.tx = tx;
    uint32_t status = am_hal_iom_blocking_transfer_55cc1c(g2_i2c_bus_table[bus].handle, &txn);
    if (status == 0u) {
        txn.direction = IOM_RX;
        txn.num_bytes = rx_len;
        txn.rx = rx;
        status = am_hal_iom_blocking_transfer_55cc1c(g2_i2c_bus_table[bus].handle, &txn);
    }
    return finish(bus, status);
}

void hal_i2c_irq_handler(void) {
    uint32_t status;
    void *handle = g2_i2c_bus_table[4].handle;
    if (am_hal_iom_interrupt_status_get_55c4d0(handle, 1u, &status) == 0u && status != 0u) {
        (void)am_hal_iom_interrupt_clear_55c518(handle, status);
        (void)am_hal_iom_interrupt_service_55c558(handle, status);
    }
}

/* Concatenate head and body (at most 32 bytes) into one write transaction. */
uint32_t hal_i2c_transfer_joined(uint8_t bus, uint8_t addr, const void *head, uint32_t head_len,
                                 const void *body, uint32_t body_len) {
    uint8_t joined[G2_HAL_I2C_JOINED_MAX];
    g2_iom_transfer_t txn = {0};
    for (uint32_t i = 0; i < sizeof joined; i++)
        joined[i] = 0u;
    if (bus >= G2_HAL_I2C_BUS_COUNT || head_len + body_len > G2_HAL_I2C_JOINED_MAX)
        return 1u;
    begin(bus);
    for (uint32_t i = 0; i < head_len; i++)
        joined[i] = ((const uint8_t *)head)[i];
    for (uint32_t i = 0; i < body_len; i++)
        joined[head_len + i] = ((const uint8_t *)body)[i];
    txn.priority = 1u;
    txn.direction = IOM_TX;
    txn.num_bytes = head_len + body_len;
    txn.do_continue = 0u;
    txn.dev_addr = addr;
    txn.tx = joined;
    return finish(bus, am_hal_iom_blocking_transfer_55cc1c(g2_i2c_bus_table[bus].handle, &txn));
}

uint32_t hal_i2c_transfer_read(uint8_t bus, uint8_t addr, void *rx, uint32_t len) {
    g2_iom_transfer_t txn = {0};
    if (bus >= G2_HAL_I2C_BUS_COUNT)
        return 1u;
    begin(bus);
    txn.priority = 1u;
    txn.direction = IOM_RX;
    txn.do_continue = 0u;
    txn.dev_addr = addr;
    txn.num_bytes = len;
    txn.rx = rx;
    return finish(bus, am_hal_iom_blocking_transfer_55cc1c(g2_i2c_bus_table[bus].handle, &txn));
}

uint32_t hal_i2c_transfer_write(uint8_t bus, uint8_t addr, const void *tx, uint32_t len) {
    g2_iom_transfer_t txn = {0};
    if (bus >= G2_HAL_I2C_BUS_COUNT)
        return 1u;
    begin(bus);
    txn.priority = 1u;
    txn.direction = IOM_TX;
    txn.do_continue = 0u;
    txn.dev_addr = addr;
    txn.num_bytes = len;
    txn.tx = tx;
    return finish(bus, am_hal_iom_blocking_transfer_55cc1c(g2_i2c_bus_table[bus].handle, &txn));
}
