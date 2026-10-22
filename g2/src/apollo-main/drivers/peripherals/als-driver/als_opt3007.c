/* ALS sensor access (TI OPT3007), stock driver\sensor\als\als.c.
 * Native DRV_ALSInit 0x4adf74..0x4ae076, power off 0x4ae076..0x4ae082 and
 * DRV_ALSReadData 0x4ae082..0x4ae10a; literal pool 0x4ae958..0x4ae980.
 *
 * The register helpers 0x5135d2/0x51357c/0x513748 (stock opt3007 driver) run
 * on product I2C bus 2, address 0x45: a register read is
 * hal_i2c_transfer_full(2, 0x45, &reg, 1, buf, 2) returning buf[0] << 8 | buf[1];
 * a field write is a read-modify-write that skips the bus write when the
 * register value would not change.
 *
 * Power: sensor rail on codec GPIO channel 9 (shared with channel 6 on pad
 * 0x86 through g2_codec_gpio_write 0x509024), 5 ms settle before access.
 *
 * Lux: raw = (R & 0xfff) << (R >> 12) of result register 0x00 (0.01 lux per
 * LSB). Without a production calibration (word +0x28 of the factory record at
 * 0x20003994; build default 0x13469 = 78953) the value is raw / 10, else
 * raw * calibration / 1000000; the pitch filter then applies. */
#include <stdint.h>
#include "g2_als.h"
#include "als_log.h"

#define SENSOR_POWER_CHANNEL 9u
#define POWER_SETTLE_MS 5u
#define OPT3007_RESULT_REGISTER 0u
#define OPT3007_MODE_CONTINUOUS 3u
#define OPT3007_CONVERSION_100MS 0u
#define FACTORY_LUX_CALIBRATION 0x28u
#define CALIBRATION_ONE 1000000u
#define UNCALIBRATED_DIVISOR 10u

extern uint32_t g2_codec_gpio_write(uint32_t channel, uint32_t value,
                                    uint32_t unused_r2, uint32_t passthrough_r3); /* 0x509024 */
extern uint32_t audio_delay(uint32_t ticks); /* osDelay 0x449376 */
extern void ti_opt3007_assignRegistermap(g2_opt3007_regmap_t *map); /* 0x5135e0 */
extern uint16_t opt3007_register_get_5135d2(const g2_opt3007_field_t *field);
extern void opt3007_field_write_51357c(const g2_opt3007_field_t *field, uint32_t value);
extern uint16_t opt3007_register_read_513748(uint8_t reg);
extern uint8_t display_driver_ratio_cells_20003994[0xac]; /* RAM 0x20003994 factory record */

static const char init_function[] = "DRV_ALSInit"; /* ROM 0x789f98 */
static const char id_error[] = "ALS device id error"; /* ROM 0x77d8a8 */
static const char id_error_short[] = "[sensor_als]ALS device id error"; /* ROM 0x75d4d0 */
static const char id_ok[] = "ALS device id ok, id:0x%04X, did:0x%04X"; /* ROM 0x746dc4 */
static const char id_ok_short[] =
    "[sensor_als]ALS device id ok, id:0x%04X, did:0x%04X"; /* ROM 0x726360 */
static const char read_function[] = "DRV_ALSReadData"; /* ROM 0x784b80 */
static const char no_calibration[] = "lux base protuction calibration is 0"; /* ROM 0x746dec */
static const char no_calibration_short[] =
    "[sensor_als]lux base protuction calibration is 0"; /* ROM 0x726394 */

/* Power the sensor, verify the OPT3007 IDs and start continuous 100 ms
 * conversions. Returns 0, or -1 on an ID mismatch (sensor left powered). */
int32_t als_function_25(void)
{
    g2_opt3007_regmap_t *map = &g2_als_opt3007_regmap;
    (void)g2_codec_gpio_write(SENSOR_POWER_CHANNEL, 1u, 0u, 0u);
    (void)audio_delay(POWER_SETTLE_MS);
    ti_opt3007_assignRegistermap(map);
    uint16_t manufacturer = opt3007_register_get_5135d2(&map->manufacturer_id);
    uint16_t device = opt3007_register_get_5135d2(&map->device_id);
    if (manufacturer != G2_ALS_OPT3007_MANUFACTURER_ID ||
        device != G2_ALS_OPT3007_DEVICE_ID) {
        ALS_LOG(1u, init_function, 400u, 0x04000000u, id_error, id_error_short);
        return -1;
    }
    ALS_LOG(3u, init_function, 0x193u, 0x0c800000u, id_ok, id_ok_short,
            (uint32_t)manufacturer, (uint32_t)device);
    opt3007_field_write_51357c(&map->mode, OPT3007_MODE_CONTINUOUS);
    opt3007_field_write_51357c(&map->conversion_time, OPT3007_CONVERSION_100MS);
    return 0;
}

void als_function_26(void)
{
    (void)g2_codec_gpio_write(SENSOR_POWER_CHANNEL, 0u, 0u, 0u);
}

uint32_t als_function_27(void)
{
    uint16_t result = opt3007_register_read_513748(OPT3007_RESULT_REGISTER);
    uint32_t raw = (result & 0xfffu) * (1u << (result >> 12));
    uint32_t calibration = *(const uint32_t *)(const void *)
        &display_driver_ratio_cells_20003994[FACTORY_LUX_CALIBRATION];
    uint32_t lux;
    if (calibration == 0u) {
        ALS_LOG(4u, read_function, 0x1aau, 0x10000000u, no_calibration,
                no_calibration_short);
        lux = raw / UNCALIBRATED_DIVISOR;
    } else {
        lux = raw * calibration / CALIBRATION_ONE;
    }
    return als_function_08(lux);
}
