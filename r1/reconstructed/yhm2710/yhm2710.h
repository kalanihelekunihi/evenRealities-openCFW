#ifndef OPENR1_RECONSTRUCTED_YHM2710_H
#define OPENR1_RECONSTRUCTED_YHM2710_H

/*
 * Owner-authorized clean-room reconstruction of the R1 YHM2710 closure.
 * This is not YHMICROS or Even Realities source.  The implementation is
 * derived from the byte-exact R1 application image (SHA-256
 * 0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a)
 * and the Ghidra/disassembly evidence named in the correlation document.
 */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define YHM2710_STACMD_GPIO (32u + 1u) /* recovered P1.01 */
#define YHM2710_STACMD_RETRY_ATTEMPTS 9u
#define YHM2710_STACMD_EDGE_POLLS 1000u
#define YHM2710_DEVICE_ID UINT8_C(0xA0)

enum {
    YHM2710_STATUS_OK = 0,
    YHM2710_STATUS_NULL_REQUEST = 11,
    YHM2710_STATUS_WRITE_NOT_OPEN = 27,
    YHM2710_STATUS_READ_NOT_OPEN = 29,
    YHM2710_STATUS_WRITE_FAILED = 30,
    YHM2710_STATUS_READ_FAILED = 31
};

typedef void (*yhm2710_pin_op_fn)(uint32_t pin);
typedef void (*yhm2710_set_input_fn)(uint32_t pin, uint32_t pull);
typedef uint32_t (*yhm2710_read_pin_fn)(uint32_t pin);
typedef void (*yhm2710_delay_cycles_fn)(uint32_t cycles);

/* Runtime-installed stock record fields at +0x0c..+0x28. */
typedef struct {
    uint32_t pin;
    yhm2710_pin_op_fn drive_low;
    yhm2710_pin_op_fn release_high;
    yhm2710_pin_op_fn set_output;
    yhm2710_set_input_fn set_input;
    uint8_t input_pull;
    yhm2710_read_pin_fn read_pin;
    yhm2710_delay_cycles_fn delay_cycles;
} yhm2710_stacmd_line;

typedef struct {
    bool opened;
    yhm2710_stacmd_line line;
    uint32_t failed_transactions;
} yhm2710_stacmd_device;

/* Stock generic-device request layouts used by the operation table. */
typedef struct {
    uint8_t command;
    uint8_t reserved_01[11];
    uint8_t *buffer;
    uint8_t length;
    uint8_t reserved_11[3];
} yhm2710_stacmd_read_request;

typedef struct {
    uint8_t command;
    uint8_t reserved_01[3];
    const uint8_t *buffer;
    uint8_t length;
    uint8_t reserved_09[3];
} yhm2710_stacmd_write_request;

void yhm2710_stacmd_initialize(yhm2710_stacmd_device *device,
                               const yhm2710_stacmd_line *line);
bool yhm2710_stacmd_operational(const yhm2710_stacmd_device *device);

/* Exact transport primitives. */
uint8_t yhm2710_stacmd_parity(uint8_t value);                 /* 0x968A8 */
void yhm2710_stacmd_drive_bit(yhm2710_stacmd_device *device,
                              uint8_t bit);                   /* 0x5CBE4 */
void yhm2710_stacmd_write_bits(yhm2710_stacmd_device *device,
                               uint8_t value, bool seven_bits); /* 0x5CC68 */
void yhm2710_stacmd_bus_recovery(yhm2710_stacmd_device *device); /* 0x5CC8C */
void yhm2710_stacmd_idle(yhm2710_stacmd_device *device);        /* 0x5CCCC */
bool yhm2710_stacmd_read_bit(yhm2710_stacmd_device *device,
                             uint8_t *bit);                    /* 0x87B30 */
bool yhm2710_stacmd_read_bit_adapter(yhm2710_stacmd_device *device,
                                     uint8_t *bit);            /* 0x969EC */
bool yhm2710_stacmd_read_frame(yhm2710_stacmd_device *device,
                               uint8_t command, uint8_t reg,
                               uint8_t *bytes, size_t length); /* 0x28BB0 */
bool yhm2710_stacmd_write_frame(yhm2710_stacmd_device *device,
                                uint8_t command, uint8_t reg,
                                const uint8_t *bytes,
                                size_t length);                /* 0x28C6C */
bool yhm2710_stacmd_write_retry(yhm2710_stacmd_device *device,
                                uint8_t reg, const uint8_t *bytes,
                                size_t length);                /* 0x35698 */

/* Exact operation-table lifecycle/adapters. */
uint32_t yhm2710_stacmd_open(yhm2710_stacmd_device *device);   /* 0x5657C */
uint32_t yhm2710_stacmd_close(yhm2710_stacmd_device *device);  /* 0x56568 */
uint32_t yhm2710_stacmd_read(yhm2710_stacmd_device *device,
                             const yhm2710_stacmd_read_request *request);
uint32_t yhm2710_stacmd_write(yhm2710_stacmd_device *device,
                              const yhm2710_stacmd_write_request *request);

typedef bool (*yhm2710_register_read_fn)(void *context, uint8_t reg,
                                         uint8_t *bytes, size_t length);
typedef bool (*yhm2710_register_write_fn)(void *context, uint8_t reg,
                                          const uint8_t *bytes,
                                          size_t length);
typedef void (*yhm2710_lock_fn)(void *context);
typedef void (*yhm2710_event_fn)(void *context, uint32_t value);

typedef struct {
    yhm2710_register_read_fn read;
    yhm2710_register_write_fn write;
    void *io_context;
    yhm2710_lock_fn acquire;
    yhm2710_lock_fn release;
    void *lock_context;
    yhm2710_delay_cycles_fn delay_cycles;
    yhm2710_event_fn completion;
    void *completion_context;
} yhm2710_bindings;

typedef struct {
    yhm2710_bindings bindings;
    yhm2710_stacmd_device *transport;
} yhm2710_device;

void yhm2710_initialize(yhm2710_device *device,
                        const yhm2710_bindings *bindings);
void yhm2710_initialize_with_stacmd(yhm2710_device *device,
                                    yhm2710_stacmd_device *transport,
                                    const yhm2710_bindings *extra_bindings);
bool yhm2710_register_read(yhm2710_device *device, uint8_t reg,
                           uint8_t *bytes, size_t length);      /* 0x3540C */
bool yhm2710_register_write(yhm2710_device *device, uint8_t reg,
                            const uint8_t *bytes, size_t length); /* 0x35760 */
bool yhm2710_register_read_byte(yhm2710_device *device, uint8_t reg,
                                uint8_t *value);                /* 0x35412 */
bool yhm2710_register_write_byte(yhm2710_device *device, uint8_t reg,
                                 uint8_t value);                /* 0x35766 */
bool yhm2710_ready(yhm2710_device *device);                     /* 0x3541C */
uint8_t yhm2710_chip_id(yhm2710_device *device);                /* 0x3530C */
uint32_t yhm2710_configure(yhm2710_device *device);             /* 0x3510C */
uint8_t yhm2710_status(yhm2710_device *device);                 /* 0x3529A */
uint8_t yhm2710_charge_state(yhm2710_device *device);           /* 0x35272 */
uint8_t yhm2710_set_ladder(yhm2710_device *device, float target); /* 0x35508 */
bool yhm2710_set_shared_power_active(yhm2710_device *device);   /* 0x355A8 */
bool yhm2710_set_high_temperature(yhm2710_device *device);      /* 0x35684 */
bool yhm2710_set_system_track(yhm2710_device *device);          /* 0x355BC */
void yhm2710_delay_209(void);                                  /* 0x5C0FA */
void yhm2710_dispatch_completion(yhm2710_device *device,
                                 uint32_t value);               /* 0x507AC */

#endif
