/* Stock 0x1000b748/0x1000b7a0 follows pinned NationalChip
 * lvp/lvp_mode.c with exactly two product records: IDLE(0), mode5(5).
 * Native ROM table 0x10013664 and records 0x1001366c/0x100136b0
 * authenticate the field order and callback addresses below.
 */
#include <stdint.h>

typedef int32_t (*mode_init)(uint32_t);
typedef void (*mode_done)(uint32_t);
typedef void (*mode_tick)(void);
typedef int32_t (*buffer_init)(void);
typedef struct {
    uint32_t type;
    mode_init init;
    mode_done done;
    mode_tick tick;
    buffer_init buffer_init;
} mode_info;
_Static_assert(sizeof(mode_info) == 20, "native mode-info width");

extern int32_t gx8002_image_b_idle_init_1000b7d8(uint32_t);
extern void gx8002_image_b_idle_done_1000b7c8(uint32_t);
extern void gx8002_image_b_idle_tick_1000b7c0(void);
extern int32_t gx8002_image_b_idle_buffer_1000b7c4(void);
extern int32_t gx8002_image_b_mode5_init_1000bc44(uint32_t);
extern void gx8002_image_b_mode5_done_1000b7e8(uint32_t);
extern void gx8002_image_b_mode5_tick_1000b958(void);
extern int32_t gx8002_image_b_mode5_buffer_1000b7f8(void);

__attribute__((used, section(".rodata.image_b_mode_idle")))
const mode_info gx8002_image_b_idle_mode_info = {
    0u, gx8002_image_b_idle_init_1000b7d8,
    gx8002_image_b_idle_done_1000b7c8, gx8002_image_b_idle_tick_1000b7c0,
    gx8002_image_b_idle_buffer_1000b7c4,
};
__attribute__((used, section(".rodata.image_b_mode5")))
const mode_info gx8002_image_b_mode5_info = {
    5u, gx8002_image_b_mode5_init_1000bc44,
    gx8002_image_b_mode5_done_1000b7e8, gx8002_image_b_mode5_tick_1000b958,
    gx8002_image_b_mode5_buffer_1000b7f8,
};
__attribute__((used, section(".rodata.image_b_mode_list")))
const mode_info *const gx8002_image_b_mode_list[2] = {
    &gx8002_image_b_idle_mode_info, &gx8002_image_b_mode5_info,
};

__attribute__((section(".bss.image_b_mode_loop")))
volatile uint32_t gx8002_image_b_mode_loop_2002d2b4;
__attribute__((section(".bss.image_b_mode_index")))
volatile uint32_t gx8002_image_b_mode_index_2002d2b8;

uint32_t gx8002_image_b_main_mode_1000b748(uint32_t type)
{
    gx8002_image_b_mode_loop_2002d2b4 = 1u;
    gx8002_image_b_mode_index_2002d2b8 = 0u;
    for (uint32_t i = 0; i < 2u; ++i) {
        if (gx8002_image_b_mode_list[i]->type == type) {
            gx8002_image_b_mode_index_2002d2b8 = i;
            break;
        }
    }
    const mode_info *mode = gx8002_image_b_mode_list[gx8002_image_b_mode_index_2002d2b8];
    (void)mode->buffer_init();
    (void)mode->init(UINT32_C(0xffff));
    return mode->type;
}

uint32_t gx8002_image_b_main_poll_1000b7a0(void)
{
    const mode_info *mode = gx8002_image_b_mode_list[gx8002_image_b_mode_index_2002d2b8];
    if (mode->tick != 0) mode->tick();
    return gx8002_image_b_mode_loop_2002d2b4;
}
