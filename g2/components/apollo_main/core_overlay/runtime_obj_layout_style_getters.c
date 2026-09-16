/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room LVGL style getter veneers from AM-020. Each function forwards to
 * the retained `lv_obj_get_style_prop` core with the recovered property id.
 */

extern unsigned int open_cfw_retained_obj_get_style_prop(
    const void *obj,
    unsigned int part,
    unsigned int prop
);

#define OPEN_CFW_STYLE_GETTER(name, prop_id) \
    __attribute__((used, noinline)) \
    unsigned int name(const void *obj, unsigned int part) \
    { \
        unsigned int result = \
            open_cfw_retained_obj_get_style_prop(obj, part, (prop_id)); \
        __asm__ volatile("" : "+r"(result)); \
        return result; \
    }

#define OPEN_CFW_STYLE_GETTER_NAKED(name, prop_id) \
    __attribute__((used, naked)) \
    unsigned int name(const void *obj, unsigned int part) \
    { \
        __asm__ volatile( \
            "push {r7, lr}\n" \
            "movs r2, %0\n" \
            "bl open_cfw_retained_obj_get_style_prop\n" \
            "pop {r1, pc}\n" \
            : \
            : "I"(prop_id) \
        ); \
    }

#if defined(OPEN_CFW_AM020_STYLE_6E_ONLY)
OPEN_CFW_STYLE_GETTER(open_cfw_runtime_obj_get_style_layout_prop_6e, 0x6eU)
#endif

#if defined(OPEN_CFW_AM020_STYLE_6F_ONLY)
OPEN_CFW_STYLE_GETTER(open_cfw_runtime_obj_get_style_layout_prop_6f, 0x6fU)
#endif

#if defined(OPEN_CFW_AM020_STYLE_70_ONLY)
OPEN_CFW_STYLE_GETTER(open_cfw_runtime_obj_get_style_layout_prop_70, 0x70U)
#endif

#if defined(OPEN_CFW_AM020_STYLE_71_ONLY)
OPEN_CFW_STYLE_GETTER(open_cfw_runtime_obj_get_style_layout_prop_71, 0x71U)
#endif

#if defined(OPEN_CFW_AM020_STYLE_72_ONLY)
OPEN_CFW_STYLE_GETTER(open_cfw_runtime_obj_get_style_layout_prop_72, 0x72U)
#endif

#if defined(OPEN_CFW_AM020_STYLE_73_ONLY)
OPEN_CFW_STYLE_GETTER(open_cfw_runtime_obj_get_style_layout_prop_73, 0x73U)
#endif

#if defined(OPEN_CFW_AM020_STYLE_74_ONLY)
OPEN_CFW_STYLE_GETTER(open_cfw_runtime_obj_get_style_layout_prop_74, 0x74U)
#endif

#if defined(OPEN_CFW_AM020_STYLE_0C_ONLY)
OPEN_CFW_STYLE_GETTER(open_cfw_runtime_obj_get_style_layout_prop_0c, 0x0cU)
#endif

#if defined(OPEN_CFW_AM004_STYLE_01_ONLY)
OPEN_CFW_STYLE_GETTER_NAKED(open_cfw_runtime_obj_get_style_prop_01, 0x01)
#endif

#if defined(OPEN_CFW_AM004_STYLE_04_ONLY)
OPEN_CFW_STYLE_GETTER_NAKED(open_cfw_runtime_obj_get_style_prop_04, 0x04)
#endif

#if defined(OPEN_CFW_AM004_STYLE_05_ONLY)
OPEN_CFW_STYLE_GETTER_NAKED(open_cfw_runtime_obj_get_style_prop_05, 0x05)
#endif

#if defined(OPEN_CFW_AM004_STYLE_02_ONLY)
OPEN_CFW_STYLE_GETTER_NAKED(open_cfw_runtime_obj_get_style_prop_02, 0x02)
#endif

#if defined(OPEN_CFW_AM004_STYLE_06_ONLY)
OPEN_CFW_STYLE_GETTER_NAKED(open_cfw_runtime_obj_get_style_prop_06, 0x06)
#endif

#if defined(OPEN_CFW_AM004_STYLE_07_ONLY)
OPEN_CFW_STYLE_GETTER_NAKED(open_cfw_runtime_obj_get_style_prop_07, 0x07)
#endif

#if defined(OPEN_CFW_AM004_STYLE_08_ONLY)
OPEN_CFW_STYLE_GETTER_NAKED(open_cfw_runtime_obj_get_style_prop_08, 0x08)
#endif

#if defined(OPEN_CFW_AM004_STYLE_09_ONLY)
OPEN_CFW_STYLE_GETTER_NAKED(open_cfw_runtime_obj_get_style_prop_09, 0x09)
#endif

#if defined(OPEN_CFW_AM004_STYLE_0A_BYTE_ONLY)
__attribute__((used, naked))
unsigned int open_cfw_runtime_obj_get_style_prop_0a_byte(
    const void *obj,
    unsigned int part
)
{
    __asm__ volatile(
        "push {r7, lr}\n"
        "movs r2, #0x0a\n"
        "bl open_cfw_retained_obj_get_style_prop\n"
        "uxtb r0, r0\n"
        "pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM004_STYLE_6C_ONLY)
OPEN_CFW_STYLE_GETTER_NAKED(open_cfw_runtime_obj_get_style_prop_6c, 0x6c)
#endif

#if defined(OPEN_CFW_AM004_STYLE_6D_ONLY)
OPEN_CFW_STYLE_GETTER_NAKED(open_cfw_runtime_obj_get_style_prop_6d, 0x6d)
#endif

#if defined(OPEN_CFW_AM004_STYLE_6E_ONLY)
OPEN_CFW_STYLE_GETTER_NAKED(open_cfw_runtime_obj_get_style_prop_6e, 0x6e)
#endif

#if defined(OPEN_CFW_AM004_STYLE_6F_ONLY)
OPEN_CFW_STYLE_GETTER_NAKED(open_cfw_runtime_obj_get_style_prop_6f, 0x6f)
#endif

#if defined(OPEN_CFW_AM004_STYLE_70_ONLY)
OPEN_CFW_STYLE_GETTER_NAKED(open_cfw_runtime_obj_get_style_prop_70, 0x70)
#endif

#if defined(OPEN_CFW_AM004_STYLE_71_ONLY)
OPEN_CFW_STYLE_GETTER_NAKED(open_cfw_runtime_obj_get_style_prop_71, 0x71)
#endif

#if defined(OPEN_CFW_AM004_STYLE_72_ONLY)
OPEN_CFW_STYLE_GETTER_NAKED(open_cfw_runtime_obj_get_style_prop_72, 0x72)
#endif

#if defined(OPEN_CFW_AM004_STYLE_10_ONLY)
OPEN_CFW_STYLE_GETTER_NAKED(open_cfw_runtime_obj_get_style_prop_10, 0x10)
#endif

#if defined(OPEN_CFW_AM004_STYLE_11_ONLY)
OPEN_CFW_STYLE_GETTER_NAKED(open_cfw_runtime_obj_get_style_prop_11, 0x11)
#endif

#if defined(OPEN_CFW_AM004_STYLE_12_ONLY)
OPEN_CFW_STYLE_GETTER_NAKED(open_cfw_runtime_obj_get_style_prop_12, 0x12)
#endif

#if defined(OPEN_CFW_AM004_STYLE_13_ONLY)
OPEN_CFW_STYLE_GETTER_NAKED(open_cfw_runtime_obj_get_style_prop_13, 0x13)
#endif

#if defined(OPEN_CFW_AM021_STYLE_2D_BOOL_ONLY)
__attribute__((used, naked))
unsigned int open_cfw_runtime_obj_get_style_prop_2d_bool(
    const void *obj,
    unsigned int part
)
{
    __asm__ volatile(
        "push {r7, lr}\n"
        "movs r2, #0x2d\n"
        "bl open_cfw_retained_obj_get_style_prop\n"
        "cmp r0, #0\n"
        "beq 1f\n"
        "movs r0, #1\n"
        "b 2f\n"
        "1:\n"
        "movs r0, #0\n"
        "2:\n"
        "uxtb r0, r0\n"
        "pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM021_STYLE_62_BYTE_ONLY)
__attribute__((used, naked))
unsigned int open_cfw_runtime_obj_get_style_prop_62_byte(
    const void *obj,
    unsigned int part
)
{
    __asm__ volatile(
        "push {r7, lr}\n"
        "movs r2, #0x62\n"
        "bl open_cfw_retained_obj_get_style_prop\n"
        "uxtb r0, r0\n"
        "pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM021_STYLE_63_BYTE_ONLY)
__attribute__((used, naked))
unsigned int open_cfw_runtime_obj_get_style_prop_63_byte(
    const void *obj,
    unsigned int part
)
{
    __asm__ volatile(
        "push {r7, lr}\n"
        "movs r2, #0x63\n"
        "bl open_cfw_retained_obj_get_style_prop\n"
        "uxtb r0, r0\n"
        "pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM021_STYLE_69_BYTE_ONLY)
__attribute__((used, naked))
unsigned int open_cfw_runtime_obj_get_style_prop_69_byte(
    const void *obj,
    unsigned int part
)
{
    __asm__ volatile(
        "push {r7, lr}\n"
        "movs r2, #0x69\n"
        "bl open_cfw_retained_obj_get_style_prop\n"
        "uxtb r0, r0\n"
        "pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM021_STYLE_75_ONLY)
__attribute__((used, naked))
unsigned int open_cfw_runtime_obj_get_style_prop_75(
    const void *obj,
    unsigned int part
)
{
    __asm__ volatile(
        "push {r7, lr}\n"
        "movs r2, #0x75\n"
        "bl open_cfw_retained_obj_get_style_prop\n"
        "pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM021_STYLE_16_U16_ONLY)
__attribute__((used, naked))
unsigned int open_cfw_runtime_obj_get_style_prop_16_u16(
    const void *obj,
    unsigned int part
)
{
    __asm__ volatile(
        "push {r7, lr}\n"
        "movs r2, #0x16\n"
        "bl open_cfw_retained_obj_get_style_prop\n"
        "uxth r0, r0\n"
        "pop {r1, pc}\n"
    );
}
#endif
