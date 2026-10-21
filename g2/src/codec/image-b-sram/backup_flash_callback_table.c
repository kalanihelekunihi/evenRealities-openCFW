/* Native image-B flash API pointer table 0x10016d80..0x10016dfb,
 * RAM alias 0x20016d80. Each nonzero stock word is a function entry;
 * source relocations deliberately expose the still missing callback bodies.
 * The zero slots are authenticated initial values. */
#include <stdint.h>

extern uint32_t gx8002_image_b_flash_chunked_write_10006e64(
    uint32_t, const uint8_t *, uint32_t);
extern int32_t gx8002_image_b_flash_erase_all_callback_10007f78(void);
extern int32_t gx8002_image_b_flash_erase_1000764c(uint32_t, uint32_t);
extern uint32_t gx8002_image_b_flash_size_10007f58(void);
extern uint32_t gx8002_image_b_flash_query_10006eb8(uint32_t);
extern int32_t gx8002_image_b_flash_info_read_10007bd4(
    uint8_t *, uint32_t, uint32_t *);

/* These entries are genuine callable source obligations. Their native
 * addresses are known, but their whole C bodies have not been selected. */
extern uint32_t gx8002_image_b_flash_callback_10007d78(void);
extern int32_t gx8002_image_b_flash_callback_100074c0(
    uint32_t, const uint8_t *, uint32_t);
extern uint32_t gx8002_image_b_flash_callback_10007118(void);
extern void gx8002_image_b_flash_callback_100075d0(
    uint32_t, uint32_t, uint32_t *, uint32_t *);
extern int32_t gx8002_image_b_flash_callback_10006fc8(void);
extern int32_t gx8002_image_b_flash_callback_10006fac(uint32_t *);
extern uint32_t gx8002_image_b_flash_callback_100070f8(uint32_t);
extern uint32_t gx8002_image_b_flash_callback_10007108(void);
extern int32_t gx8002_image_b_flash_callback_1000715c(void);
extern int32_t gx8002_image_b_flash_callback_100071d4(uint8_t *);
extern uint32_t gx8002_image_b_flash_callback_1000723c(void);
extern uint32_t gx8002_image_b_flash_callback_10007884(
    uint32_t, const uint8_t *, uint32_t);
extern uint32_t gx8002_image_b_flash_callback_100079e8(
    uint32_t, uint8_t *, uint32_t);
extern uint32_t gx8002_image_b_flash_callback_100072e8(uint32_t *);
extern uint32_t gx8002_image_b_flash_callback_100072fc(uint32_t);
extern uint32_t gx8002_image_b_flash_callback_10007324(uint32_t *);
extern uint32_t gx8002_image_b_flash_callback_1000733c(uint32_t *);

_Static_assert(sizeof(uintptr_t) == 4u, "image-B pointer table ABI");

__attribute__((section(".data.image_b.flash_callback_table"), aligned(4)))
uintptr_t gx8002_image_b_flash_probe_callback_20016d80[31] = {
    (uintptr_t)&gx8002_image_b_flash_callback_10007d78,
    (uintptr_t)&gx8002_image_b_flash_chunked_write_10006e64,
    (uintptr_t)&gx8002_image_b_flash_erase_all_callback_10007f78,
    (uintptr_t)&gx8002_image_b_flash_erase_1000764c,
    (uintptr_t)&gx8002_image_b_flash_callback_100074c0,
    (uintptr_t)&gx8002_image_b_flash_callback_10007118,
    0u,
    (uintptr_t)&gx8002_image_b_flash_callback_100075d0,
    0u, 0u, 0u, 0u,
    (uintptr_t)&gx8002_image_b_flash_size_10007f58,
    (uintptr_t)&gx8002_image_b_flash_query_10006eb8,
    (uintptr_t)&gx8002_image_b_flash_callback_10006fc8,
    (uintptr_t)&gx8002_image_b_flash_callback_10006fac,
    (uintptr_t)&gx8002_image_b_flash_callback_100070f8,
    (uintptr_t)&gx8002_image_b_flash_callback_10007108,
    (uintptr_t)&gx8002_image_b_flash_callback_1000715c,
    (uintptr_t)&gx8002_image_b_flash_callback_100071d4,
    (uintptr_t)&gx8002_image_b_flash_callback_1000723c,
    (uintptr_t)&gx8002_image_b_flash_callback_10007884,
    (uintptr_t)&gx8002_image_b_flash_callback_100079e8,
    (uintptr_t)&gx8002_image_b_flash_callback_100072e8,
    (uintptr_t)&gx8002_image_b_flash_callback_100072fc,
    (uintptr_t)&gx8002_image_b_flash_callback_10007324,
    (uintptr_t)&gx8002_image_b_flash_callback_1000733c,
    0u, 0u, 0u,
    (uintptr_t)&gx8002_image_b_flash_info_read_10007bd4,
};
