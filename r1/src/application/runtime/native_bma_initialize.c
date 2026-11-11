#include <stdint.h>
#include <stddef.h>
#include "bma456w.h"
struct r1_bma_remap_span {struct bma4_axes_remap remap;uint8_t observed_following_bytes[2];};
_Static_assert(sizeof(struct bma4_axes_remap)==6 && sizeof(struct r1_bma_remap_span)==8 && offsetof(struct r1_bma_remap_span,observed_following_bytes)==6,"native eight-byte read span");
/* Six designated defaults are attributable to Bosch. The two following bytes
 * are an authenticated native literal-read contract, with their origin gated. */
const struct r1_bma_remap_span r1_bma_default_remap_span __attribute__((section(".r1.bma.remap.span"),aligned(4)))={.remap={.x_axis=BMA4_MAP_X_AXIS,.x_axis_sign=BMA4_MAP_POSITIVE,.y_axis=BMA4_MAP_Y_AXIS,.y_axis_sign=BMA4_MAP_POSITIVE,.z_axis=BMA4_MAP_Z_AXIS,.z_axis_sign=BMA4_MAP_POSITIVE},.observed_following_bytes={0x80,0x2e}};
const char r1_bma_config_string_53ed4[40] __attribute__((section(".r1.bma.config.s53ed4")))="[RING]BMA456 interface init failed: %d";
const char r1_bma_config_string_53efc[36] __attribute__((section(".r1.bma.config.s53efc")))="BMA456 interface init failed: %d";
const char r1_bma_config_string_53f20[32] __attribute__((section(".r1.bma.config.s53f20")))="[RING]BMA456W init failed: %d";
const char r1_bma_config_string_53f40[24] __attribute__((section(".r1.bma.config.s53f40")))="BMA456W init failed: %d";
const char r1_bma_config_string_53f58[44] __attribute__((section(".r1.bma.config.s53f58")))="[RING]BMA456 set accel config failed: %d";
const char r1_bma_config_string_53f84[36] __attribute__((section(".r1.bma.config.s53f84")))="BMA456 set accel config failed: %d";
const char r1_bma_config_string_53fa8[40] __attribute__((section(".r1.bma.config.s53fa8")))="[RING]BMA456 enable accel failed: %d";
const char r1_bma_config_string_53fd0[32] __attribute__((section(".r1.bma.config.s53fd0")))="BMA456 enable accel failed: %d";
const char r1_bma_config_string_53ff0[52] __attribute__((section(".r1.bma.config.s53ff0")))="[RING]BMA456 disable advance power save failed: %d";
const char r1_bma_config_string_54024[48] __attribute__((section(".r1.bma.config.s54024")))="BMA456 disable advance power save failed: %d";
const char r1_bma_config_string_54054[44] __attribute__((section(".r1.bma.config.s54054")))="[RING]BMA456 clear fifo config failed: %d";
const char r1_bma_config_string_54080[36] __attribute__((section(".r1.bma.config.s54080")))="BMA456 clear fifo config failed: %d";
const char r1_bma_config_string_540a4[44] __attribute__((section(".r1.bma.config.s540a4")))="[RING]BMA456 enable fifo accel failed: %d";
const char r1_bma_config_string_540d0[36] __attribute__((section(".r1.bma.config.s540d0")))="BMA456 enable fifo accel failed: %d";
const char r1_bma_config_string_540f4[44] __attribute__((section(".r1.bma.config.s540f4")))="[RING]BMA456 disable fifo header failed: %d";
const char r1_bma_config_string_54120[40] __attribute__((section(".r1.bma.config.s54120")))="BMA456 disable fifo header failed: %d";
const char r1_bma_config_string_54148[52] __attribute__((section(".r1.bma.config.s54148")))="[RING]BMA456 enable advance power save failed: %d";
const char r1_bma_config_string_5417c[44] __attribute__((section(".r1.bma.config.s5417c")))="BMA456 enable advance power save failed: %d";
extern int8_t r1_bma4_null_pointer_check(const struct bma4_dev *dev);
extern uint32_t r1_bma4_read_regs_boundary(uint32_t, uint8_t *, uint32_t,
                                         struct bma4_dev *);
uint32_t r1_bma4_initialize(struct bma4_dev *dev)
{
 uint8_t chip = 0;
 uint8_t dummy = 0;
 uint32_t status = (uint32_t)(int32_t)r1_bma4_null_pointer_check(dev);
 if (status != 0)
  return status;
 volatile struct bma4_dev *live = dev;
 if (live->intf == 0) {
  live->dummy_byte = 1;
  status = r1_bma4_read_regs_boundary(0, &dummy, 1, dev);
  if (status != 0)
   return status;
 } else {
  live->dummy_byte = 0;
 }
 status = r1_bma4_read_regs_boundary(0, &chip, 1, dev);
 if (status == 0)
  live->chip_id = chip;
 return status;
}
/* Native remap stores are unaligned word/halfword accesses. May-alias packed
 * views describe those accesses without assuming natural alignment. */
struct __attribute__((packed, may_alias)) r1_bma_native_word { uint32_t value; };
struct __attribute__((packed, may_alias)) r1_bma_native_half { uint16_t value; };
_Static_assert(offsetof(struct bma4_dev, resolution)==12 &&
               offsetof(struct bma4_dev, feature_len)==22 &&
               offsetof(struct bma4_dev, config_size)==48 &&
               offsetof(struct bma4_dev, remap)==29,
               "native Bosch device initialization fields");
uint32_t r1_bma456w_initialize(struct bma4_dev *dev)
{
 const uint8_t *span = (const uint8_t *)&r1_bma_default_remap_span;
 uint32_t low = ((const volatile struct r1_bma_native_word *)span)->value;
 uint32_t high = ((const volatile struct r1_bma_native_word *)(span+4))->value;
 uint32_t status = r1_bma4_initialize(dev);
 if (status != 0)
  return status;
 volatile struct bma4_dev *live = dev;
 if (live->chip_id != 0x16)
  return UINT32_MAX - 3;
 live->resolution = 16;
 live->feature_len = 76;
 live->config_size = 5016;
 ((volatile struct r1_bma_native_word *)((uint8_t *)dev+29))->value = low;
 ((volatile struct r1_bma_native_half *)((uint8_t *)dev+33))->value = (uint16_t)high;
 return 0;
}

extern struct bma4_dev r1_bma_context;
extern uint32_t r1_bma_interface_initialize(struct bma4_dev *);
extern uint32_t r1_bma4_set_accel_config(struct bma4_accel_config *, struct bma4_dev *);
extern uint32_t r1_bma4_set_accel_enable(uint32_t, struct bma4_dev *);
extern uint32_t r1_bma4_set_advance_power_save_boundary(uint32_t, struct bma4_dev *);
extern uint32_t r1_bma4_set_fifo_config(uint32_t, uint32_t, struct bma4_dev *);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t, const char *, const char *, ...);
extern void nrf_log_frontend_std_1(uint32_t, const char *, uint32_t);
_Static_assert(sizeof(struct bma4_accel_config)==4 &&
               offsetof(struct bma4_accel_config,odr)==0 &&
               offsetof(struct bma4_accel_config,bandwidth)==1 &&
               offsetof(struct bma4_accel_config,perf_mode)==2 &&
               offsetof(struct bma4_accel_config,range)==3,
               "native accelerometer configuration bytes");
static void r1_bma_config_log_failure(const char *ring, const char *sdk, uint32_t status)
{
 if ((r1_structured_log_mode_get() & 1u) ||
     (r1_structured_log_mode_get() & 4u))
  r1_structured_log_format(UINT32_C(0x04400000), ring, ring, status);
 if (r1_structured_log_mode_get() & 2u)
  nrf_log_frontend_std_1(UINT32_C(0x001c0001), sdk, status);
}
#define R1_BMA_CONFIG_TRY(call, ring, sdk) do { \
 uint32_t status = (call); \
 if (status != 0) { r1_bma_config_log_failure((ring), (sdk), status); return 0; } \
} while (0)
uint32_t r1_bma456w_configure_boundary(uint32_t rate)
{
 struct bma4_accel_config config = {0};
 R1_BMA_CONFIG_TRY(r1_bma_interface_initialize(&r1_bma_context),
                   r1_bma_config_string_53ed4, r1_bma_config_string_53efc);
 R1_BMA_CONFIG_TRY(r1_bma456w_initialize(&r1_bma_context),
                   r1_bma_config_string_53f20, r1_bma_config_string_53f40);
 config.odr = rate == 50 ? 7 : rate == 100 ? 8 : rate == 200 ? 9 : 6;
 config.bandwidth = 0;
 config.perf_mode = 0;
 config.range = 2;
 R1_BMA_CONFIG_TRY(r1_bma4_set_accel_config(&config, &r1_bma_context),
                   r1_bma_config_string_53f58, r1_bma_config_string_53f84);
 R1_BMA_CONFIG_TRY(r1_bma4_set_accel_enable(1, &r1_bma_context),
                   r1_bma_config_string_53fa8, r1_bma_config_string_53fd0);
 R1_BMA_CONFIG_TRY(r1_bma4_set_advance_power_save_boundary(0, &r1_bma_context),
                   r1_bma_config_string_53ff0, r1_bma_config_string_54024);
 R1_BMA_CONFIG_TRY(r1_bma4_set_fifo_config(0x7f, 0, &r1_bma_context),
                   r1_bma_config_string_54054, r1_bma_config_string_54080);
 R1_BMA_CONFIG_TRY(r1_bma4_set_fifo_config(0x40, 1, &r1_bma_context),
                   r1_bma_config_string_540a4, r1_bma_config_string_540d0);
 R1_BMA_CONFIG_TRY(r1_bma4_set_fifo_config(0x10, 0, &r1_bma_context),
                   r1_bma_config_string_540f4, r1_bma_config_string_54120);
 R1_BMA_CONFIG_TRY(r1_bma4_set_advance_power_save_boundary(1, &r1_bma_context),
                   r1_bma_config_string_54148, r1_bma_config_string_5417c);
 return 1;
}
#undef R1_BMA_CONFIG_TRY
