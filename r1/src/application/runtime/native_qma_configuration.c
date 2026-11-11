#include <stdint.h>
#include <stddef.h>
/* Owner-authorized reconstruction of authenticated native contracts, not QST source.
 * Only the observed 24-byte state prefix is owned; full object extent is gated.
 * Bus sequencing and register policies are expressed in C. */
struct r1_qma_sensor_prefix { uint8_t address,id,pad[2]; uint32_t scale; uint8_t state,pad9; uint16_t signs[3],maps[3]; uint8_t tail[2]; };
_Static_assert(sizeof(struct r1_qma_sensor_prefix)==24 && offsetof(struct r1_qma_sensor_prefix,scale)==4 && offsetof(struct r1_qma_sensor_prefix,signs)==10 && offsetof(struct r1_qma_sensor_prefix,maps)==16,"observed QMA state prefix");
struct r1_qma_sensor_prefix r1_qma_sensor_state __attribute__((section(".r1.qma.sensor"),aligned(4)));
const uint16_t r1_qma_axis_defaults[6] __attribute__((section(".r1.qma.axis"),aligned(2)))={1,1,1,0,1,2};
extern uint32_t r1_qma_write_retry(uint32_t, uint32_t);
extern uint32_t r1_qma_read_retry(uint32_t, uint8_t *, uint32_t);
extern uint32_t r1_qma_delay_units(uint32_t);
extern uint32_t r1_qma6100_chip_id(void);
uint32_t r1_qma_setup(uint32_t rate);
uint32_t r1_qma_range(uint32_t range)
{
 uint32_t scale = range == 2 ? 2048 : range == 4 ? 1024 :
                  range == 8 ? 512 : range == 15 ? 256 : 4096;
 ((volatile struct r1_qma_sensor_prefix *)&r1_qma_sensor_state)->scale = scale;
 return r1_qma_write_retry(0x0f, range);
}
uint32_t r1_qma_steps(uint32_t enabled)
{
 uint8_t value = 0;
 (void)r1_qma_write_retry(0x13, 0x80);
 (void)r1_qma_delay_units(1);
 uint32_t status = r1_qma_write_retry(0x13, 0x7f);
 if (enabled == 0)
  return status;
 const volatile struct r1_qma_sensor_prefix *live = &r1_qma_sensor_state;
 uint8_t id = live->id;
 uint32_t a = 0, b = 0, c = 0;
 if (id == 0x90 || id == 0xfa) {
  a = 0x89;
  b = 0x0b;
  c = id == 0x90 ? 0x0c : 0x0e;
 }
 (void)r1_qma_write_retry(0x12, a);
 (void)r1_qma_write_retry(0x14, b);
 (void)r1_qma_write_retry(0x15, c);
 (void)r1_qma_read_retry(0x1e, &value, 1);
 value &= 0x3f;
 (void)r1_qma_write_retry(0x1e, value);
 id = live->id;
 if (id == 0x90)
  return r1_qma_write_retry(0x1f, 0xa9);
 if (id == 0xfa)
  return r1_qma_write_retry(0x1f, 0xaa);
 return id;
}

uint32_t r1_qma6100_configure_boundary(uint32_t rate)
{
 volatile struct r1_qma_sensor_prefix *live = &r1_qma_sensor_state;
 uint32_t id = 0;
 for (uint32_t attempt = 0; attempt < 2; ++attempt) {
  live->id = 0;
  live->address = (uint8_t)(0x12u + attempt);
  id = r1_qma6100_chip_id();
  live->id = (uint8_t)id;
  if (id == 0xfa || (id >> 4) == 9)
   break;
 }
 uint32_t status = 0;
 if (id == 0xfa || ((uint8_t)id >> 4) == 9)
  status = r1_qma_setup((uint8_t)rate);
 const volatile uint16_t *defaults = r1_qma_axis_defaults;
 live->state = 0;
 live->maps[0] = defaults[3];
 live->maps[1] = defaults[4];
 live->maps[2] = defaults[5];
 live->signs[0] = defaults[0];
 live->signs[1] = defaults[1];
 live->signs[2] = defaults[2];
 return status;
}
uint32_t r1_qma_reset(void);
uint64_t r1_qma_any_motion(uint32_t, uint32_t);
uint32_t r1_qma_tap(uint32_t, uint32_t, uint32_t);
uint32_t r1_qma_setup(uint32_t rate)
{
 (void)r1_qma_reset();
 (void)r1_qma_write_retry(0x4a, 0x20);
 (void)r1_qma_write_retry(0x50, 0x51);
 (void)r1_qma_write_retry(0x56, 1);
 (void)r1_qma_range(4);
 switch (rate) {
 case 25:
  (void)r1_qma_write_retry(0x10, 0);
  (void)r1_qma_write_retry(0x11, 0x86);
  break;
 case 50:
  (void)r1_qma_write_retry(0x10, 6);
  (void)r1_qma_write_retry(0x11, 0x84);
  break;
 case 100:
  (void)r1_qma_write_retry(0x10, 1);
  (void)r1_qma_write_retry(0x11, 0x85);
  break;
 case 150:
 case 200:
  (void)r1_qma_write_retry(0x10, 2);
  (void)r1_qma_write_retry(0x11, 0x85);
  break;
 default:
  break;
 }
 (void)r1_qma_write_retry(0x3e, 0x87);
 (void)r1_qma_write_retry(0x4a, 0x28);
 (void)r1_qma_write_retry(0x20, 5);
 (void)r1_qma_delay_units(5);
 (void)r1_qma_write_retry(0x5f, 0x80);
 (void)r1_qma_delay_units(5);
 (void)r1_qma_write_retry(0x5f, 0);
 (void)r1_qma_delay_units(5);
 (void)r1_qma_steps(1);
 (void)r1_qma_any_motion(0, 1);
 (void)r1_qma_tap(0x31, 0, 1);
 return 1;
}
uint64_t r1_qma_any_motion(uint32_t axis, uint32_t enabled)
{
 /* Native POP restores both parameter words; each low byte is scratch. */
 uint32_t axis_word = axis & UINT32_C(0xffffff00);
 uint32_t enabled_word = enabled & UINT32_C(0xffffff00);
 uint8_t b = 0, wake = 0;
 volatile uint8_t *control = (volatile uint8_t *)&axis_word;
 volatile uint8_t *live_a = (volatile uint8_t *)&enabled_word;
 volatile uint8_t *live_b = &b, *live_wake = &wake;
 (void)r1_qma_read_retry(0x18, (uint8_t *)&axis_word, 1);
 (void)r1_qma_read_retry(0x1a, (uint8_t *)&enabled_word, 1);
 (void)r1_qma_read_retry(0x1c, &b, 1);
 (void)r1_qma_read_retry(0x2c, &wake, 1);
 uint32_t value = *live_wake | 1u;
 *live_wake = (uint8_t)value;
 (void)r1_qma_write_retry(0x2c, value);
 uint8_t id = ((const volatile struct r1_qma_sensor_prefix *)&r1_qma_sensor_state)->id;
 if (id == 0x90 || id == 0xfa)
  (void)r1_qma_write_retry(0x2e, 0x10);
 (void)r1_qma_write_retry(0x2f, 0);
 (void)r1_qma_write_retry(0x30, 0xff);
 uint32_t bits = *control;
 uint32_t route = *live_a;
 if (enabled != 0) {
  bits |= 7u;
  *control = (uint8_t)bits;
  *live_a = (uint8_t)(route | 1u);
  *live_b = (uint8_t)(*live_b | 1u);
  (void)r1_qma_write_retry(0x18, bits);
  if (axis == 0)
   (void)r1_qma_write_retry(0x1a, *live_a);
  else if (axis == 1)
   (void)r1_qma_write_retry(0x1c, *live_b);
 } else {
  bits &= ~UINT32_C(7);
  *control = (uint8_t)bits;
  *live_a = (uint8_t)(route & ~UINT32_C(1));
  *live_b = (uint8_t)(*live_b & ~UINT32_C(1));
  (void)r1_qma_write_retry(0x18, bits);
  (void)r1_qma_write_retry(0x1a, *live_a);
  (void)r1_qma_write_retry(0x1c, *live_b);
 }
 uint64_t low = *(const volatile uint32_t *)&axis_word;
 uint64_t high = *(const volatile uint32_t *)&enabled_word;
 return low | (high << 32);
}

uint32_t r1_qma_reset(void)
{
 uint8_t power = 0;
 uint8_t ready = 0;
 const volatile uint8_t *live_power = &power;
 const volatile uint8_t *live_ready = &ready;
 (void)r1_qma_write_retry(0x36, 0xb6);
 (void)r1_qma_delay_units(5);
 (void)r1_qma_write_retry(0x36, 0);
 (void)r1_qma_delay_units(100);
 uint32_t attempt = 0;
 while (*live_power != 0x80) {
  (void)r1_qma_write_retry(0x11, 0x80);
  (void)r1_qma_delay_units(2);
  (void)r1_qma_read_retry(0x11, &power, 1);
  uint32_t before = attempt++;
  if (before > 100)
   break;
 }
 (void)r1_qma_write_retry(0x33, 8);
 (void)r1_qma_delay_units(5);
 attempt = 0;
 while (*live_ready != 5) {
  (void)r1_qma_read_retry(0x33, &ready, 1);
  (void)r1_qma_delay_units(10);
  uint32_t before = attempt++;
  if (before > 100)
   break;
 }
 return 0;
}

/* Unwritten register bytes start at zero instead of private stack history. */
uint32_t r1_qma_tap(uint32_t axes,uint32_t route,uint32_t enabled)
{
 volatile uint8_t scratch[20]={0};
 uint32_t mask = (uint8_t)axes;
 (void)r1_qma_read_retry(0x16, (uint8_t *)(uintptr_t)scratch, 1);
 (void)r1_qma_read_retry(0x19, (uint8_t *)(uintptr_t)(scratch+4), 1);
 (void)r1_qma_read_retry(0x1a, (uint8_t *)(uintptr_t)(scratch+8), 1);
 (void)r1_qma_read_retry(0x1b, (uint8_t *)(uintptr_t)(scratch+12), 1);
 (void)r1_qma_read_retry(0x1c, (uint8_t *)(uintptr_t)(scratch+16), 1);
 (void)r1_qma_write_retry(0x1e, 3);
 (void)r1_qma_write_retry(0x2a, 0x86);
 (void)r1_qma_write_retry(0x2b, 0x85);
 uint32_t value = scratch[0];
 value = enabled != 0 ? value | mask : value & ~mask;
 scratch[0] = (uint8_t)value;
 uint32_t status = r1_qma_write_retry(0x16, value);
 if (route != 0 && route != 1)
  return status;
 if ((axes & 1u) != 0) {
  uint32_t offset = route == 0 ? 8 : 16;
  value = scratch[offset];
  value = enabled != 0 ? value | 2u : value & ~UINT32_C(2);
  scratch[offset] = (uint8_t)value;
  (void)r1_qma_write_retry(route == 0 ? 0x1a : 0x1c, value);
 }
 uint32_t offset = route == 0 ? 4 : 12;
 value = scratch[offset];
 value = enabled != 0 ? value | mask : value & ~mask;
 scratch[offset] = (uint8_t)value;
 return r1_qma_write_retry(route == 0 ? 0x19 : 0x1b, value);
}
