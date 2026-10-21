#ifndef OPENR1_RECONSTRUCTED_SOFTWARE_TWI_H
#define OPENR1_RECONSTRUCTED_SOFTWARE_TWI_H

/*
 * Provenance banner
 * -----------------
 * Family:         unknown_software_twi_provider_candidate (Bravechip B210
 *                 "ChipletRing" platform GPIO-driven two-wire engine,
 *                 compiler-instantiated for buses `i2c_2`..`i2c_5`).
 * Stock image:    application image, load base 0x00027000, sha256
 *                 0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a.
 * Evidence:       the engine region 0x000552DC..0x000562DF is absent from the
 *                 Ghidra corpus; all forty bodies were disassembled from the
 *                 byte-exact rebuilt image
 *                 r1/research/decompilation/rebuild/rebuilt-application.bin
 *                 with arm-none-eabi-objdump (GNU binutils, Thumb-2) during
 *                 this reduction.
 * Status:         RECONSTRUCTED FROM DECOMPILATION EVIDENCE; NOT VENDOR
 *                 SOURCE.  Never present this file as Even Realities or
 *                 Bravechip source.  No upstream source, version, or license
 *                 exists for this family (see the 2026-08 attribution
 *                 re-examination); reduction is owner-authorized per
 *                 docs/SOURCE-ADMISSION.md ("Owner-authorized full reduction
 *                 (2026-08-14)").
 *
 * Reduced stock functions (application image extents, end-exclusive):
 *
 *   0x00055330..<0x0005535C   44  i2c_2 open
 *   0x00055360..<0x0005538C   44  i2c_3 open
 *   0x00055390..<0x000553DE   78  i2c_4 open (adds two Nordic-shape gpio cfg calls)
 *   0x000553E4..<0x00055410   44  i2c_5 open
 *   0x0005547C..<0x000554AA   46  i2c_2 read adapter  (u8 register, u8 count)
 *   0x000554B0..<0x000554DE   46  i2c_3 read adapter  (u8 register, u8 count)
 *   0x000554E4..<0x00055512   46  i2c_4 read adapter  (u16 register, u16 count)
 *   0x00055518..<0x00055542   42  i2c_5 read adapter  (u16 register, u8 count; merged errors)
 *   0x00055548..<0x000555F4  172  read byte (four byte-identical copies)
 *   0x000555F4..<0x000556A0  172    ""   (i2c_3 copy)
 *   0x000556A0..<0x0005574C  172    ""   (i2c_4 copy)
 *   0x0005574C..<0x000557F8  172    ""   (i2c_5 copy)
 *   0x000557F8..<0x00055878  128  i2c_2 read transaction (u8 register)
 *   0x00055878..<0x000558F8  128  i2c_3 read transaction (u8 register)
 *   0x000558F8..<0x00055988  144  i2c_4 read transaction (u16 register)
 *   0x00055988..<0x00055A18  144  i2c_5 read transaction (u16 register)
 *   0x00055A18..<0x00055A56   62  start (four byte-identical copies)
 *   0x00055A56..<0x00055A94   62    ""   (i2c_3 copy)
 *   0x00055A94..<0x00055AD2   62    ""   (i2c_4 copy)
 *   0x00055AD2..<0x00055B10   62    ""   (i2c_5 copy)
 *   0x00055B10..<0x00055B3C   44  stop (four byte-identical copies)
 *   0x00055B3C..<0x00055B68   44    ""   (i2c_3 copy)
 *   0x00055B68..<0x00055B94   44    ""   (i2c_4 copy)
 *   0x00055B94..<0x00055BC0   44    ""   (i2c_5 copy)
 *   0x00055BC0..<0x00055C08   72  wait-ACK (four byte-identical copies)
 *   0x00055C08..<0x00055C50   72    ""   (i2c_3 copy)
 *   0x00055C50..<0x00055C98   72    ""   (i2c_4 copy)
 *   0x00055C98..<0x00055CE0   72    ""   (i2c_5 copy)
 *   0x00055DBC..<0x00055E3C  128  i2c_2 write adapter
 *   0x00055E40..<0x00055EC0  128  i2c_3 write adapter
 *   0x00055EC4..<0x00055F58  148  i2c_4 write adapter (no register byte)
 *   0x00055F5C..<0x00055F9E   66  i2c_5 write adapter
 *   0x00055FA4..<0x00055FF2   78  write byte (four byte-identical copies)
 *   0x00055FF2..<0x00056040   78    ""   (i2c_3 copy)
 *   0x00056040..<0x0005608E   78    ""   (i2c_4 copy)
 *   0x0005608E..<0x000560DC   78    ""   (i2c_5 copy)
 *   0x000560DC..<0x0005613E   98  write transaction, u16 register + one byte
 *   0x0005613E..<0x000561A0   98  write transaction, u8 register + N bytes
 *   0x000561A0..<0x00056202   98    "" (second copy)
 *   0x00056202..<0x00056274  114  write transaction, u16 register + N bytes
 *
 * The four close/shutdown wrappers at 0x000551E8..0x00055280 and the four
 * bus-binding wrappers at 0x00056508..0x00056562 are NOT part of this family
 * (admitted R1 adapters / R1 board configuration respectively).
 *
 * Correlation doc: docs/correlation/SOFTWARE-TWI-REDUCTION-CORRELATION.md.
 */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Recovered family status scheme.  This family's codes interlock gap-free
 * with the generic-device-registry family's missing-operation codes
 * {1,2,3,5,6,7,9} into one positive status enum 0..12 (single-authorship
 * evidence; see the boundary doc). */
enum {
    SOFTWARE_TWI_STATUS_OK = 0,
    SOFTWARE_TWI_STATUS_BAD_ARGUMENT = 4,   /* NULL request (recovered) */
    SOFTWARE_TWI_STATUS_WRITE_NOT_OPEN = 8, /* write adapter, bus not open */
    SOFTWARE_TWI_STATUS_READ_NOT_OPEN = 10, /* read adapter, bus not open */
    SOFTWARE_TWI_STATUS_WRITE_NACK = 11,    /* write-side transaction NACK */
    SOFTWARE_TWI_STATUS_READ_NACK = 12      /* read adapter transaction failure */
};

/* Engine operation vtable (stock: runtime-installed function pointers inside
 * each per-bus record; the installer itself belongs to the still-blocked
 * registry/configuration wave, so the reconstruction binds them explicitly
 * through software_twi_initialize).  Pins are nRF52840 absolute GPIO numbers
 * (P0.n = n, P1.n = 32 + n). */
typedef void (*software_twi_pin_op_fn)(uint32_t pin);
typedef void (*software_twi_set_input_fn)(uint32_t pin, uint32_t pull);
typedef void (*software_twi_udelay_fn)(uint32_t context);
typedef uint32_t (*software_twi_read_pin_fn)(uint32_t pin);

/* Nordic nrf_gpio_cfg-shaped six-argument wrapper called only by the
 * divergent i2c_4 open (stock callee 0x00078EE6: builds the PIN_CNF word
 * dir | input<<1 | pull<<2 | drive<<8 | sense<<16). */
typedef void (*software_twi_gpio_configure_fn)(uint32_t pin, uint32_t direction,
                                               uint32_t input, uint32_t pull,
                                               uint32_t drive, uint32_t sense);

/* Recovered engine state (stock: per-bus record + 0x08). */
typedef struct {
    uint32_t delay_context;              /* +0x00 udelay operand (recovered 1/5/1/1) */
    uint32_t scl_pin;                    /* +0x04 */
    uint32_t sda_pin;                    /* +0x08 */
    software_twi_pin_op_fn drive_low;    /* +0x0C */
    software_twi_pin_op_fn release_high; /* +0x10 */
    software_twi_pin_op_fn set_output;   /* +0x14 */
    software_twi_set_input_fn set_input; /* +0x18 (pin, pull) */
    uint8_t input_pull;                  /* +0x1C pull operand passed to set_input */
    uint8_t reserved_1d[3];              /* +0x1D */
    software_twi_udelay_fn udelay;       /* +0x20 (context) */
    software_twi_read_pin_fn read_pin;   /* +0x24 */
} software_twi_engine;                   /* 0x28 bytes on the 32-bit target */

/* Recovered 0x70-byte per-bus record (stock: 0x20007400 + n*0x70).  Only the
 * open flag and the engine state are interpreted by this family; the name
 * pointer, the close-path pin-release op at +0x30, and the generic-registry
 * sub-record at +0x34 are installed/owned by other (still blocked or
 * separately admitted) waves and kept as opaque storage for layout
 * fidelity. */
typedef struct {
    const char *name;               /* +0x00 device name ("i2c_2"..) */
    uint8_t opened;                 /* +0x04 open flag */
    uint8_t reserved_05[3];         /* +0x05 */
    software_twi_engine engine;     /* +0x08 */
    software_twi_pin_op_fn pin_release; /* +0x30 close-path op (not this family) */
    uintptr_t registry_record[15];  /* +0x34..+0x6F registry sub-record (opaque) */
} software_twi_record;              /* 0x70 bytes on the 32-bit target */

typedef enum {
    SOFTWARE_TWI_BUS_I2C_2 = 0,
    SOFTWARE_TWI_BUS_I2C_3 = 1,
    SOFTWARE_TWI_BUS_I2C_4 = 2,
    SOFTWARE_TWI_BUS_I2C_5 = 3,
    SOFTWARE_TWI_BUS_COUNT = 4
} software_twi_bus_id;

/* Provider bindings.  Stock resolves every GPIO/delay operation through the
 * runtime-installed record vtable and calls the nrf_gpio_cfg-shaped wrapper
 * directly; the reconstruction binds all of them explicitly.  An unbound
 * mandatory provider fails explicitly (SOFTWARE_TWI_STATUS_BAD_ARGUMENT, or
 * the error-polarity result for the void/NACK-primitive cores) instead of
 * faulting. */
typedef struct {
    software_twi_pin_op_fn drive_low;
    software_twi_pin_op_fn release_high;
    software_twi_pin_op_fn set_output;
    software_twi_set_input_fn set_input;
    software_twi_udelay_fn udelay;
    software_twi_read_pin_fn read_pin;
    software_twi_gpio_configure_fn gpio_configure; /* i2c_4 open only */
    uint8_t input_pull; /* set_input pull operand; runtime-installed in stock,
                           not flash-recoverable, supplied by the binder */
} software_twi_providers;

/* Recovered registry-dispatch request blocks (stock field offsets; widths
 * noted per bus, end of used extent marked by the reserved tail). */
typedef struct {
    uint8_t address;               /* +0x00 7-bit address, R/W bit added by the engine */
    uint8_t reserved_01;           /* +0x01 */
    uint16_t register_address;     /* +0x02 (i2c_2/3 use the low byte only) */
    uint32_t reserved_04[2];       /* +0x04..+0x0B */
    uint8_t *buffer;               /* +0x0C */
    uint16_t length;               /* +0x10 (i2c_2/3/5 use the low byte only) */
    uint16_t reserved_12;          /* +0x12 */
} software_twi_read_request;

typedef struct {
    uint8_t address;               /* +0x00 */
    uint8_t reserved_01;           /* +0x01 */
    uint16_t register_address;     /* +0x02 (i2c_2/3 low byte only; i2c_4 ignores it) */
    const uint8_t *buffer;         /* +0x04 */
    uint16_t length;               /* +0x08 */
    uint16_t reserved_0a;          /* +0x0A */
} software_twi_write_request;

/* Zeroes the four per-bus records, installs the recovered board bindings
 * (pins, delay contexts, device names), and binds the provider vtable into
 * every engine.  NULL providers (or NULL members) leave the affected paths
 * failing explicitly. */
void software_twi_initialize(const software_twi_providers *providers);

/* Accessors for the static per-bus records (NULL for an out-of-range id).
 * The engine accessor exposes the stock engine-pointer calling convention;
 * the record accessor exists for the registry-installer wave (registry
 * sub-record ownership stays with that family). */
software_twi_engine *software_twi_bus_engine(software_twi_bus_id bus);
software_twi_record *software_twi_bus_record(software_twi_bus_id bus);

/* 0x00055A18 / 0x00055A56 / 0x00055A94 / 0x00055AD2 (byte-identical):
 * START condition.  set_output(SCL); set_output(SDA); release SCL; release
 * SDA; udelay; drive SDA low; udelay; drive SCL low; udelay. */
void software_twi_start(software_twi_engine *engine);

/* 0x00055B10 / 0x00055B3C / 0x00055B68 / 0x00055B94 (byte-identical):
 * STOP condition.  set_output(SCL); set_output(SDA); drive SDA low; release
 * SCL; udelay; release SDA. */
void software_twi_stop(software_twi_engine *engine);

/* 0x00055BC0 / 0x00055C08 / 0x00055C50 / 0x00055C98 (byte-identical):
 * wait for the slave ACK after a written byte.  release SDA; set_input(SDA,
 * pull); udelay; release SCL; udelay; sample SDA; drive SCL low;
 * set_output(SDA); udelay.  Returns 1 on NACK (error polarity — inverted
 * relative to upstream bit-bang libraries) and 0 on ACK. */
uint32_t software_twi_wait_ack(software_twi_engine *engine);

/* 0x00055548 / 0x000555F4 / 0x000556A0 / 0x0005574C (byte-identical):
 * read one byte MSB-first (SCL release / sample SDA / drive SCL low per
 * bit), then pulse an ACK (send_ack != 0: drive SDA low) or NACK (leave SDA
 * released); both paths end with release_high(SDA).  Returns the byte. */
uint8_t software_twi_read_byte(uint32_t send_ack, software_twi_engine *engine);

/* 0x00055FA4 / 0x00055FF2 / 0x00056040 / 0x0005608E (byte-identical):
 * write one byte MSB-first; per bit drive/release SDA, udelay, release SCL,
 * udelay, drive SCL low; releases SDA after bit 7 (in-loop ACK-window prep).
 * Does not sample the ACK (callers use software_twi_wait_ack). */
void software_twi_write_byte(uint8_t value, software_twi_engine *engine);

/* 0x000557F8 / 0x00055878 (i2c_2/i2c_3 copies): read transaction with an
 * 8-bit register address.  start / address(W) / register / repeated-start /
 * address|1 / count-1 bytes with ACK + final byte with NACK / stop.  Any
 * NACK aborts with SOFTWARE_TWI_STATUS_WRITE_NACK (11) and no STOP.  A zero
 * count still reads exactly one byte (recovered count-1 loop quirk). */
uint32_t software_twi_read_transaction_reg8(uint8_t address, uint8_t reg,
                                            uint8_t *buffer, uint8_t count,
                                            software_twi_engine *engine);

/* 0x000558F8 / 0x00055988 (i2c_4/i2c_5 copies): same transaction with a
 * 16-bit register address sent MSB-first.  Stock i2c_4 counts 16-bit and
 * i2c_5 counts 8-bit; callers truncate the count to their recovered width. */
uint32_t software_twi_read_transaction_reg16(uint8_t address, uint16_t reg,
                                             uint8_t *buffer, uint16_t count,
                                             software_twi_engine *engine);

/* 0x000560DC (census "i2c_2 write transaction"; calls the i2c_5 primitive
 * copies in stock): start / address(W) / 16-bit register MSB-first / one
 * data byte / stop; 11 on any NACK. */
uint32_t software_twi_write_transaction_reg16_byte(uint8_t address,
                                                   uint16_t reg, uint8_t data,
                                                   software_twi_engine *engine);

/* 0x0005613E / 0x000561A0 (two copies; called by the i2c_2 and i2c_3 write
 * adapters respectively): start / address(W) / 8-bit register / N data
 * bytes / stop; 11 on any NACK.  A zero count writes no data bytes. */
uint32_t software_twi_write_transaction_reg8(uint8_t address, uint8_t reg,
                                             const uint8_t *buffer,
                                             uint8_t count,
                                             software_twi_engine *engine);

/* 0x00056202 (i2c_5): start / address(W) / 16-bit register MSB-first / N
 * data bytes / stop; 11 on any NACK. */
uint32_t software_twi_write_transaction_reg16(uint8_t address, uint16_t reg,
                                              const uint8_t *buffer,
                                              uint8_t count,
                                              software_twi_engine *engine);

/* Opens (0x00055330 / 0x00055360 / 0x00055390 / 0x000553E4).  Idempotent via
 * the open flag: an already-open bus returns OK without re-driving the pins.
 * First open: set_output(SCL/SDA), release_high(SCL/SDA), set the flag.
 * i2c_4 additionally calls the bound gpio_configure provider twice with
 * (pin, 1, 1, 0, 0, 0) before setting the flag.  Stock always returns 0;
 * the reconstruction returns SOFTWARE_TWI_STATUS_BAD_ARGUMENT when a
 * mandatory provider is unbound (stock would fault). */
uint32_t software_twi_i2c_2_open(void);
uint32_t software_twi_i2c_3_open(void);
uint32_t software_twi_i2c_4_open(void);
uint32_t software_twi_i2c_5_open(void);

/* Registry-dispatch read adapters (0x0005547C / 0x000554B0 / 0x000554E4 /
 * 0x00055518).  The device and operation arguments are ignored in stock
 * (ops-table dispatch slots).  NULL request returns 4; a not-open bus
 * returns 10 (i2c_5 merges both failures into 4); a failed transaction
 * returns 12; success returns 0. */
uint32_t software_twi_i2c_2_read(uintptr_t device, uint32_t operation,
                                 const software_twi_read_request *request);
uint32_t software_twi_i2c_3_read(uintptr_t device, uint32_t operation,
                                 const software_twi_read_request *request);
uint32_t software_twi_i2c_4_read(uintptr_t device, uint32_t operation,
                                 const software_twi_read_request *request);
uint32_t software_twi_i2c_5_read(uintptr_t device, uint32_t operation,
                                 const software_twi_read_request *request);

/* Registry-dispatch write adapters (0x00055DBC / 0x00055E40 / 0x00055EC4 /
 * 0x00055F5C).  NULL request returns 4; a not-open bus returns 8.  A length
 * of 1 takes the single-byte path, anything else the multi-byte path with
 * the count truncated to 8 bits (i2c_4 counts 16-bit).  i2c_4 sends no
 * register byte (address + data only).  Transaction failure returns 11. */
uint32_t software_twi_i2c_2_write(uintptr_t device, uint32_t operation,
                                  const software_twi_write_request *request);
uint32_t software_twi_i2c_3_write(uintptr_t device, uint32_t operation,
                                  const software_twi_write_request *request);
uint32_t software_twi_i2c_4_write(uintptr_t device, uint32_t operation,
                                  const software_twi_write_request *request);
uint32_t software_twi_i2c_5_write(uintptr_t device, uint32_t operation,
                                  const software_twi_write_request *request);

#endif
