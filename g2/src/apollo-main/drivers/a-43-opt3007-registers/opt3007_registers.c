/* Stock D:\01_workspace\s200_ap510b_iar_git\driver\sensor\als\opt3007\opt3007_registers.c
 * (log tag "drv.opt.r"). Native 0x51357c..0x5137b7; literal pool 0x513734..0x513747.
 * Only ti_opt3007_assignRegistermap carries the path string; the field helpers
 * before it and the raw I2C accessors after it have no strings and are kept in
 * the same unit because they are contiguous with it.
 *
 * TI OPT3007 ambient light sensor on product I2C bus 2, 7-bit address 0x45.
 * Registers are 16 bits, big-endian on the wire: 0x00 result (E[15:12],
 * R[11:0]), 0x01 configuration, 0x02 low limit, 0x03 high limit,
 * 0x7e manufacturer ID (0x5449), 0x7f device ID (0x3001).
 * Callers: drivers/peripherals/als-driver/als_opt3007.c and
 * drivers/p-10-als-pt (production test). */
#include <stdint.h>
#include "g2_als.h"
#include "g2_hal_i2c.h"

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t level, const char *module, const char *file, const char *function,
                               uint32_t line, const char *format, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t code, const char *format, const char *text, ...); /* 0x43ce9e */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value); /* 0x43c0e4 */

uint16_t opt3007_register_read_513748(uint8_t reg);
void opt3007_register_write_513780(uint8_t reg, uint16_t value);

static const char s_module[] = "drv.opt.r"; /* ROM 0x78b654 */
static const char s_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\sensor\\als\\opt3007\\opt3007_registers.c"; /* ROM 0x6e8f20 */
static const char s_assign_fn[] = "ti_opt3007_assignRegistermap"; /* ROM 0x762bd0 */
static const char s_assigning[] = "Assigning register map\n\n"; /* ROM 0x76ee6c */
static const char s_assigning_short[] = "[drv.opt.r]Assigning register map\n\n"; /* ROM 0x757350 */

/* Read-modify-write of one bit field; the register is written only when the
 * value changes. The stock loads lsb with ldrsb (signed) for the shifts. */
void opt3007_field_write_51357c(const g2_opt3007_field_t *field, uint32_t value)
{
    uint16_t current = opt3007_register_read_513748(field->reg);
    uint32_t width = (uint32_t)field->msb + 1u - field->lsb;
    uint32_t keep = ~((0xffffu << field->lsb) ^ (0xffffu << (field->msb + 1u)));
    uint32_t updated = ((uint32_t)(uint16_t)(value & ~(0xffffu << width)) << field->lsb) | (keep & current);

    if (current != (uint16_t)updated)
        opt3007_register_write_513780(field->reg, (uint16_t)updated);
}

/* Whole register that holds the field. The stock passes a second argument
 * (r1 = 0) that the reader ignores. */
uint16_t opt3007_register_get_5135d2(const g2_opt3007_field_t *field)
{
    return opt3007_register_read_513748(field->reg);
}

/* Fills the 19 {msb, lsb, reg} triples (stock store order: reg, msb, lsb, with
 * the exponent field written before the mantissa field). */
void ti_opt3007_assignRegistermap(g2_opt3007_regmap_t *map)
{
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, s_module, s_file, s_assign_fn, 69u, s_assigning);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compress_log_output(0x10000000u, s_assigning_short, s_assigning_short);

    map->result_exponent.reg = 0x00u;  map->result_exponent.msb = 15u;  map->result_exponent.lsb = 12u;
    map->result_mantissa.reg = 0x00u;  map->result_mantissa.msb = 11u;  map->result_mantissa.lsb = 0u;
    map->range_number.reg = 0x01u;     map->range_number.msb = 15u;     map->range_number.lsb = 12u;
    map->conversion_time.reg = 0x01u;  map->conversion_time.msb = 11u;  map->conversion_time.lsb = 11u;
    map->mode.reg = 0x01u;             map->mode.msb = 10u;             map->mode.lsb = 9u;
    map->overflow.reg = 0x01u;         map->overflow.msb = 8u;          map->overflow.lsb = 8u;
    map->conversion_ready.reg = 0x01u; map->conversion_ready.msb = 7u;  map->conversion_ready.lsb = 7u;
    map->flag_high.reg = 0x01u;        map->flag_high.msb = 6u;         map->flag_high.lsb = 6u;
    map->flag_low.reg = 0x01u;         map->flag_low.msb = 5u;          map->flag_low.lsb = 5u;
    map->latch.reg = 0x01u;            map->latch.msb = 4u;             map->latch.lsb = 4u;
    map->polarity.reg = 0x01u;         map->polarity.msb = 3u;          map->polarity.lsb = 3u;
    map->mask_exponent.reg = 0x01u;    map->mask_exponent.msb = 2u;     map->mask_exponent.lsb = 2u;
    map->fault_count.reg = 0x01u;      map->fault_count.msb = 1u;       map->fault_count.lsb = 0u;
    map->low_exponent.reg = 0x02u;     map->low_exponent.msb = 15u;     map->low_exponent.lsb = 12u;
    map->low_mantissa.reg = 0x02u;     map->low_mantissa.msb = 11u;     map->low_mantissa.lsb = 0u;
    map->high_exponent.reg = 0x03u;    map->high_exponent.msb = 15u;    map->high_exponent.lsb = 12u;
    map->high_mantissa.reg = 0x03u;    map->high_mantissa.msb = 11u;    map->high_mantissa.lsb = 0u;
    map->manufacturer_id.reg = 0x7eu;  map->manufacturer_id.msb = 15u;  map->manufacturer_id.lsb = 0u;
    map->device_id.reg = 0x7fu;        map->device_id.msb = 15u;        map->device_id.lsb = 0u;
}

/* Register pointer write + 2-byte read in one transfer; MSB first. The I2C
 * status is ignored (a failed read returns 0 from the cleared buffer). */
uint16_t opt3007_register_read_513748(uint8_t reg)
{
    uint8_t data[2];

    (void)aeabi_memset_43c0e4(data, sizeof(data), 0);
    (void)hal_i2c_transfer_full(G2_ALS_I2C_BUS, G2_ALS_I2C_ADDR, &reg, 1u, data, 2u);
    return (uint16_t)(((uint32_t)data[0] << 8) | data[1]);
}

/* Register pointer + 2 data bytes (MSB first) as one joined write. */
void opt3007_register_write_513780(uint8_t reg, uint16_t value)
{
    uint8_t data[2];

    (void)aeabi_memset_43c0e4(data, sizeof(data), 0);
    data[1] = (uint8_t)value;
    data[0] = (uint8_t)(value >> 8);
    (void)hal_i2c_transfer_joined(G2_ALS_I2C_BUS, G2_ALS_I2C_ADDR, &reg, 1u, data, 2u);
}
