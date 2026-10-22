/* uLED driver manager entry points, stock
 * D:\01_workspace\s200_ap510b_iar_git\driver\uled\drv_mspi_uled.c.
 * Native 0x4c9d44..0x4c9d9b, 0x4ca070..0x4ca125 and 0x4ca24a..0x4ca2a9;
 * literal pool 0x4ca664..0x4ca6dc.
 *
 * uled_driver_identify (0x4c9d9c) picks one of two 64-byte option records by
 * its type byte (+0x3c: 0 = JBD4010 at ROM 0x70b024, 1 = Hongshi A6N-G at ROM
 * 0x70afe4) and publishes it at RAM 0x20074530. Every manager call indirects
 * through that record. The other manager wrappers (init, clearScreen,
 * power_up/down, setBrightness, PartialReflash_async, status_check_and_recovery,
 * set_mode) are implemented in display-uled/display_driver_uled_status.c. */
#include <stdint.h>
#include <stddef.h>

typedef struct {
    void (*term)(void);                                    /* +0x00 */
    uint32_t (*read_chip_id)(uint16_t *chip_id);           /* +0x04 */
    uint32_t (*init)(void (*)(void), void *, void *);      /* +0x08 */
    uint32_t (*configure)(uint32_t power_cycle);           /* +0x0c */
    uint32_t (*power_up)(void);                            /* +0x10 */
    uint32_t (*power_down)(void);                          /* +0x14 */
    uint32_t (*set_brightness)(uint32_t, uint32_t, uint32_t); /* +0x18 */
    uint32_t (*clear)(void);                               /* +0x1c */
    uint32_t (*set_current_6bit)(uint8_t);                 /* +0x20 */
    uint32_t (*set_display_offset)(uint8_t x, uint8_t y);  /* +0x24 */
    uint32_t (*reflash_async)(uint32_t, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t); /* +0x28 */
    uint32_t (*reflash)(int32_t, int32_t, int32_t, int32_t, int32_t, int32_t);             /* +0x2c */
    uint32_t (*status_check_and_recovery)(void);           /* +0x30 */
    uint32_t (*set_mode)(uint8_t);                         /* +0x34 */
    uint32_t (*read_sn)(void *);                           /* +0x38 A6N-G only */
    uint8_t type;                                          /* +0x3c */
} g2_uled_driver_t;
_Static_assert(sizeof(g2_uled_driver_t) == 0x40, "stock uLED option record is 64 bytes");

extern void * volatile display_driver_uled_instance; /* RAM 0x20074530, g2_uled_driver_t * */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...);

static const char module_tag[] = "driver.uled"; /* ROM 0x78a8ec */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\uled\\drv_mspi_uled.c"; /* ROM 0x70b064 */
static const char term_fn[] = "am_mspi0_isr"; /* ROM 0x785ca0, stock reuses the ISR name in uled_mspi_term */
static const char chip_id_fn[] = "uled_safe_get_chip_id"; /* ROM 0x776db4 */
static const char offset_fn[] = "uled_set_display_offset"; /* ROM 0x776e14 */
static const char no_driver[] = "Error - Failed to find uled driver.\r\n"; /* ROM 0x7499ac */
static const char no_driver_short[] = "[driver.uled]Error - Failed to find uled driver.\r\n"; /* ROM 0x728fa8 */
static const char chip_id_text[] = "uled_safe_get_chip_id chip_id %d\r\n"; /* ROM 0x753ce4 */
static const char chip_id_text_short[] = "[driver.uled]uled_safe_get_chip_id chip_id %d\r\n"; /* ROM 0x733764 */

static void log_no_driver(const char *fn, uint32_t line)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(1u, module_tag, source_file, fn, line, no_driver);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x04000000u, no_driver_short, no_driver_short);
}

void uled_mspi_term(void)
{
    const g2_uled_driver_t *driver = (const g2_uled_driver_t *)display_driver_uled_instance;

    if (driver == NULL) {
        log_no_driver(term_fn, 0x4bu);
        return;
    }
    driver->term();
}

/* Returns the panel chip ID (0xffff without a driver). The driver's status is
 * ignored; a failed read leaves the ID at 0. */
uint16_t uled_safe_get_chip_id(void)
{
    const g2_uled_driver_t *driver = (const g2_uled_driver_t *)display_driver_uled_instance;
    uint16_t chip_id = 0u;

    if (driver == NULL) {
        log_no_driver(chip_id_fn, 0xb1u);
        return 0xffffu;
    }
    (void)driver->read_chip_id(&chip_id);
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, chip_id_fn, 0xb7u, chip_id_text, (uint32_t)chip_id);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x10400000u, chip_id_text_short, chip_id_text_short, (uint32_t)chip_id);
    return chip_id;
}

uint32_t uled_set_display_offset(uint8_t x, uint8_t y)
{
    const g2_uled_driver_t *driver = (const g2_uled_driver_t *)display_driver_uled_instance;

    if (driver == NULL) {
        log_no_driver(offset_fn, 0xe5u);
        return UINT32_MAX;
    }
    return driver->set_display_offset(x, y);
}
