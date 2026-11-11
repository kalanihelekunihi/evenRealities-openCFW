/* Image-B native system init 0x1000314c..0x100031e3, written as the pinned
 * NationalChip arch/soc/grus/system.c system_init(): MPU region 0 = 4 GB
 * executable, RW, non-secure (csi_mpu_config_region), MPU on, clock init,
 * BSS clear unless memory is preserved, board init, VBR, VIC reset, then
 * exceptions and interrupts on. The CR accessors are the CSI csi_gcc.h ones
 * (that header needs include/utility, outside this unit's profile).
 * Child 0x3ffc is already selected as preserve_memory; clock init 0x3294 and
 * board init 0x34d4 remain real source obligations.
 */
#include <stdint.h>

extern void gx8002_image_b_clear_bss_10003128(void);
extern void gx8002_image_b_clock_init_10003294(void);
extern uint32_t gx8002_image_b_preserve_memory_10003ffc(void);
extern void gx8002_image_b_system_board_child_100034d4(void);
extern const uintptr_t gx8002_image_b_vectors_10003000[];

static inline uint32_t get_ccr(void)
{ uint32_t v; __asm__ volatile("mfcr %0, cr<18, 0>" : "=r"(v)); return v; }
static inline void set_ccr(uint32_t v)
{ __asm__ volatile("mtcr %0, cr<18, 0>" : : "r"(v) : "memory"); }
static inline uint32_t get_capr(void)
{ uint32_t v; __asm__ volatile("mfcr %0, cr<19, 0>" : "=r"(v)); return v; }
static inline void set_capr(uint32_t v)
{ __asm__ volatile("mtcr %0, cr<19, 0>" : : "r"(v) : "memory"); }
static inline uint32_t get_pacr(void)
{ uint32_t v; __asm__ volatile("mfcr %0, cr<20, 0>" : "=r"(v)); return v; }
static inline void set_pacr(uint32_t v)
{ __asm__ volatile("mtcr %0, cr<20, 0>" : : "r"(v) : "memory"); }
static inline uint32_t get_prsr(void)
{ uint32_t v; __asm__ volatile("mfcr %0, cr<21, 0>" : "=r"(v)); return v; }
static inline void set_prsr(uint32_t v)
{ __asm__ volatile("mtcr %0, cr<21, 0>" : : "r"(v) : "memory"); }
static inline void set_vbr(uint32_t v)
{ __asm__ volatile("mtcr %0, cr<1, 0>" : : "r"(v) : "memory"); }

#define VIC_BASE UINT32_C(0xe000e100)
#define VIC_WORD(offset) (*(volatile uint32_t *)(uintptr_t)(VIC_BASE + (offset)))

__attribute__((used, section(".text.image_b_system_init")))
void gx8002_image_b_system_init_1000314c(void)
{
    /* csi_mpu_config_region(0, 0, REGION_SIZE_4GB, {nx 0, AP_BOTH_RW, s 0}, 1) */
    uint32_t pacr = get_pacr() & UINT32_C(0x00000fff);   /* base address 0 */
    set_prsr(get_prsr() & ~UINT32_C(7));                  /* RID = 0 */
    pacr = (pacr & ~UINT32_C(0x3e)) | (31u << 1);         /* size = 4 GB */
    set_capr((get_capr() & UINT32_C(0xfefffcfe)) | (3u << 8)); /* nx0 0, ap0 RW, s0 0 */
    set_pacr(pacr | 1u);                                  /* E = 1 */
    set_ccr(get_ccr() | 3u);                              /* csi_mpu_enable: CCR.MP */

    gx8002_image_b_clock_init_10003294();
    if (gx8002_image_b_preserve_memory_10003ffc() == 0u)
        gx8002_image_b_clear_bss_10003128();
    gx8002_image_b_system_board_child_100034d4();

    set_vbr((uint32_t)(uintptr_t)gx8002_image_b_vectors_10003000);
    VIC_WORD(0xb10u) = 0xffu;                             /* TSPR */
    for (uint32_t i = 0u; i < 4u; ++i) {
        VIC_WORD(0x200u + i * 4u) = 0u;                   /* IABR[i] */
        VIC_WORD(0x180u + i * 4u) = UINT32_MAX;           /* ICPR[i] */
    }
    __asm__ volatile("psrset ee, ie" : : : "memory");     /* __enable_excp_irq */
}
