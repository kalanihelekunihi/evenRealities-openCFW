/* Authenticated Apollo UI registry 0x6a44b0..0x6a475f.
 * Function declarations provide address relocations only; callback ABI
 * and RAM context ownership must be established per entry. */
#include <stdint.h>

struct audio_uart_ui_registry_row {
    uint32_t id; uintptr_t primary; uintptr_t secondary; uintptr_t context;
};
_Static_assert(sizeof(struct audio_uart_ui_registry_row)==16u,"registry row ABI");

extern uint32_t audio_uart_registry_callback_43c400();
extern uint32_t audio_uart_registry_callback_43c496();
extern uint32_t audio_uart_registry_callback_4592dc();
extern uint32_t audio_uart_registry_callback_460638();
extern uint32_t audio_uart_registry_callback_46327e();
extern uint32_t audio_uart_registry_callback_46687c();
extern uint32_t audio_uart_registry_callback_4668ae();
extern uint32_t audio_uart_registry_callback_467e68();
extern uint32_t audio_uart_registry_callback_468484();
extern uint32_t audio_uart_registry_callback_468f24();
extern uint32_t audio_uart_registry_callback_46949a();
extern uint32_t audio_uart_registry_callback_469580();
extern uint32_t audio_uart_registry_callback_469d48();
extern uint32_t audio_uart_registry_callback_46aeea();
extern uint32_t audio_uart_registry_callback_4716ba();
extern uint32_t audio_uart_registry_callback_472102();
extern uint32_t audio_uart_registry_callback_47cf60();
extern uint32_t audio_uart_registry_callback_48e484();
extern uint32_t audio_uart_registry_callback_492f8c();
extern uint32_t audio_uart_registry_callback_492fdc();
extern uint32_t audio_uart_registry_callback_49ddb8();
extern uint32_t audio_uart_registry_callback_49e68c();
extern uint32_t audio_uart_registry_callback_49ed04();
extern uint32_t audio_uart_registry_callback_4acb40();
extern uint32_t audio_uart_registry_callback_4ae73c();
extern uint32_t audio_uart_registry_callback_4c5dbc();
extern uint32_t audio_uart_registry_callback_4d2bce();
extern uint32_t audio_uart_registry_callback_4d3354();
extern uint32_t audio_uart_registry_callback_4e1192();
extern uint32_t audio_uart_registry_callback_4e1490();
extern uint32_t audio_uart_registry_callback_4e1b30();
extern uint32_t audio_uart_registry_callback_4e1dd4();
extern uint32_t audio_uart_registry_callback_4e2976();
extern uint32_t audio_uart_registry_callback_4e2c40();
extern uint32_t audio_uart_registry_callback_4ffb38();
extern uint32_t audio_uart_registry_callback_4ffca2();
extern uint32_t audio_uart_registry_callback_501820();
extern uint32_t audio_uart_registry_callback_54f912();
extern uint32_t audio_uart_registry_callback_584ee4();
extern uint32_t audio_uart_registry_callback_585cca();
extern uint32_t audio_uart_registry_callback_58607a();
extern uint32_t audio_uart_registry_callback_589fe6();
extern uint32_t audio_uart_registry_callback_58a130();
extern uint32_t audio_uart_registry_callback_59f0ea();
extern uint32_t audio_uart_registry_callback_59f236();
extern uint32_t audio_uart_registry_callback_5b0476();
extern uint32_t audio_uart_registry_callback_5b06aa();
extern uint32_t audio_uart_registry_callback_5bf24a();
extern uint32_t audio_uart_registry_callback_5bf7b8();
extern uint32_t audio_uart_registry_callback_5ce690();
extern uint32_t audio_uart_registry_callback_5cf2e6();
extern uint32_t audio_uart_registry_callback_5cf330();
extern uint32_t audio_uart_registry_callback_5cf634();
extern uint32_t audio_uart_registry_callback_5cf67e();
extern uint32_t audio_uart_registry_callback_5cf7a8();
extern uint32_t audio_uart_registry_callback_5cf7f2();
extern uint32_t audio_uart_registry_callback_5e4488();
extern uint32_t audio_uart_registry_callback_5e44f6();
extern uint32_t audio_uart_registry_callback_5eeec4();
extern uint32_t audio_uart_registry_callback_5f958c();
extern uint32_t audio_uart_registry_callback_5f9924();
extern uint32_t audio_uart_registry_callback_5f9c8c();
extern uint32_t audio_uart_registry_callback_5f9ce0();
extern uint32_t audio_uart_registry_callback_5f9ff8();

extern uint8_t audio_uart_registry_context_20000044;
extern uint8_t audio_uart_registry_context_200004d8;
extern uint8_t audio_uart_registry_context_200005bc;
extern uint8_t audio_uart_registry_context_200009a4;
extern uint8_t audio_uart_registry_context_20000b1c;
extern uint8_t audio_uart_registry_context_20000b38;
extern uint8_t audio_uart_registry_context_200014cc;
extern uint8_t audio_uart_registry_context_20002ca8;
extern uint8_t audio_uart_registry_context_20002cc4;
extern uint8_t audio_uart_registry_context_20002ce0;
extern uint8_t audio_uart_registry_context_20002e34;
extern uint8_t audio_uart_registry_context_20003064;
extern uint8_t audio_uart_registry_context_20003080;
extern uint8_t audio_uart_registry_context_200030a0;
extern uint8_t audio_uart_registry_context_20003a40;
extern uint8_t audio_uart_registry_context_20003a5c;
extern uint8_t audio_uart_registry_context_20003bd0;
extern uint8_t audio_uart_registry_context_20003bf0;
extern uint8_t audio_uart_registry_context_20003da4;
extern uint8_t audio_uart_registry_context_20003e50;
extern uint8_t audio_uart_registry_context_2000418c;

const struct audio_uart_ui_registry_row audio_uart_display_registry_begin[43]={
    /* 00 native 0x6a44b0 */ {0x104u,(uintptr_t)&audio_uart_registry_callback_43c400,(uintptr_t)&audio_uart_registry_callback_43c496,(uintptr_t)&audio_uart_registry_context_20000044},
    /* 01 native 0x6a44c0 */ {0x10eu,(uintptr_t)&audio_uart_registry_callback_4ae73c,0u,0u},
    /* 02 native 0x6a44d0 */ {0xbu,(uintptr_t)&audio_uart_registry_callback_5b0476,(uintptr_t)&audio_uart_registry_callback_5b06aa,(uintptr_t)&audio_uart_registry_context_200004d8},
    /* 03 native 0x6a44e0 */ {0x1u,(uintptr_t)&audio_uart_registry_callback_49ddb8,(uintptr_t)&audio_uart_registry_callback_49e68c,(uintptr_t)&audio_uart_registry_context_200005bc},
    /* 04 native 0x6a44f0 */ {0x1fu,(uintptr_t)&audio_uart_registry_callback_501820,0u,0u},
    /* 05 native 0x6a4500 */ {0x7u,(uintptr_t)&audio_uart_registry_callback_4e2976,(uintptr_t)&audio_uart_registry_callback_4e2c40,(uintptr_t)&audio_uart_registry_context_200009a4},
    /* 06 native 0x6a4510 */ {0xffeu,(uintptr_t)&audio_uart_registry_callback_492f8c,(uintptr_t)&audio_uart_registry_callback_492fdc,(uintptr_t)&audio_uart_registry_context_20000b1c},
    /* 07 native 0x6a4520 */ {0xe0u,(uintptr_t)&audio_uart_registry_callback_4e1192,(uintptr_t)&audio_uart_registry_callback_4e1490,(uintptr_t)&audio_uart_registry_context_20000b38},
    /* 08 native 0x6a4530 */ {0x20u,(uintptr_t)&audio_uart_registry_callback_4716ba,0u,0u},
    /* 09 native 0x6a4540 */ {0xeu,(uintptr_t)&audio_uart_registry_callback_4ffca2,0u,0u},
    /* 10 native 0x6a4550 */ {0x109u,(uintptr_t)&audio_uart_registry_callback_5bf24a,(uintptr_t)&audio_uart_registry_callback_5bf7b8,(uintptr_t)&audio_uart_registry_context_200014cc},
    /* 11 native 0x6a4560 */ {0xfu,(uintptr_t)&audio_uart_registry_callback_4592dc,0u,0u},
    /* 12 native 0x6a4570 */ {0x3u,(uintptr_t)&audio_uart_registry_callback_460638,(uintptr_t)&audio_uart_registry_callback_46327e,(uintptr_t)&audio_uart_registry_context_20002ca8},
    /* 13 native 0x6a4580 */ {0x4u,(uintptr_t)&audio_uart_registry_callback_4e1b30,(uintptr_t)&audio_uart_registry_callback_4e1dd4,(uintptr_t)&audio_uart_registry_context_20002cc4},
    /* 14 native 0x6a4590 */ {0x8u,(uintptr_t)&audio_uart_registry_callback_585cca,(uintptr_t)&audio_uart_registry_callback_58607a,(uintptr_t)&audio_uart_registry_context_20002ce0},
    /* 15 native 0x6a45a0 */ {0x10u,(uintptr_t)&audio_uart_registry_callback_468484,(uintptr_t)&audio_uart_registry_callback_468f24,(uintptr_t)&audio_uart_registry_context_20002e34},
    /* 16 native 0x6a45b0 */ {0x91u,(uintptr_t)&audio_uart_registry_callback_5ce690,0u,0u},
    /* 17 native 0x6a45c0 */ {0x110u,(uintptr_t)&audio_uart_registry_callback_5cf2e6,(uintptr_t)&audio_uart_registry_callback_5cf330,(uintptr_t)&audio_uart_registry_context_20003064},
    /* 18 native 0x6a45d0 */ {0x10fu,(uintptr_t)&audio_uart_registry_callback_5cf634,(uintptr_t)&audio_uart_registry_callback_5cf67e,(uintptr_t)&audio_uart_registry_context_20003080},
    /* 19 native 0x6a45e0 */ {0x10bu,(uintptr_t)&audio_uart_registry_callback_5cf7a8,(uintptr_t)&audio_uart_registry_callback_5cf7f2,(uintptr_t)&audio_uart_registry_context_200030a0},
    /* 20 native 0x6a45f0 */ {0xcu,(uintptr_t)&audio_uart_registry_callback_4ffb38,0u,0u},
    /* 21 native 0x6a4600 */ {0x10cu,(uintptr_t)&audio_uart_registry_callback_54f912,0u,0u},
    /* 22 native 0x6a4610 */ {0x81u,(uintptr_t)&audio_uart_registry_callback_4acb40,0u,0u},
    /* 23 native 0x6a4620 */ {0x108u,(uintptr_t)&audio_uart_registry_callback_4c5dbc,0u,0u},
    /* 24 native 0x6a4630 */ {0x10du,(uintptr_t)&audio_uart_registry_callback_46687c,0u,0u},
    /* 25 native 0x6a4640 */ {0x9u,(uintptr_t)&audio_uart_registry_callback_4668ae,(uintptr_t)&audio_uart_registry_callback_467e68,(uintptr_t)&audio_uart_registry_context_20003a40},
    /* 26 native 0x6a4650 */ {0x10au,(uintptr_t)&audio_uart_registry_callback_46949a,(uintptr_t)&audio_uart_registry_callback_469580,(uintptr_t)&audio_uart_registry_context_20003a5c},
    /* 27 native 0x6a4660 */ {0xdu,(uintptr_t)&audio_uart_registry_callback_472102,0u,0u},
    /* 28 native 0x6a4670 */ {0xffu,(uintptr_t)&audio_uart_registry_callback_584ee4,0u,0u},
    /* 29 native 0x6a4680 */ {0x21u,(uintptr_t)&audio_uart_registry_callback_4d2bce,(uintptr_t)&audio_uart_registry_callback_4d3354,(uintptr_t)&audio_uart_registry_context_20003bd0},
    /* 30 native 0x6a4690 */ {0x22u,(uintptr_t)&audio_uart_registry_callback_469d48,(uintptr_t)&audio_uart_registry_callback_46aeea,(uintptr_t)&audio_uart_registry_context_20003bf0},
    /* 31 native 0x6a46a0 */ {0x6u,(uintptr_t)&audio_uart_registry_callback_589fe6,(uintptr_t)&audio_uart_registry_callback_58a130,(uintptr_t)&audio_uart_registry_context_20003da4},
    /* 32 native 0x6a46b0 */ {0x30u,(uintptr_t)&audio_uart_registry_callback_5e4488,(uintptr_t)&audio_uart_registry_callback_5e44f6,(uintptr_t)&audio_uart_registry_context_20003e50},
    /* 33 native 0x6a46c0 */ {0x101u,(uintptr_t)&audio_uart_registry_callback_48e484,0u,0u},
    /* 34 native 0x6a46d0 */ {0x11u,(uintptr_t)&audio_uart_registry_callback_5eeec4,0u,0u},
    /* 35 native 0x6a46e0 */ {0x5u,(uintptr_t)&audio_uart_registry_callback_59f0ea,(uintptr_t)&audio_uart_registry_callback_59f236,(uintptr_t)&audio_uart_registry_context_2000418c},
    /* 36 native 0x6a46f0 */ {0x105u,(uintptr_t)&audio_uart_registry_callback_5f958c,0u,0u},
    /* 37 native 0x6a4700 */ {0x102u,(uintptr_t)&audio_uart_registry_callback_5f9924,0u,0u},
    /* 38 native 0x6a4710 */ {0x90u,(uintptr_t)&audio_uart_registry_callback_5f9ff8,0u,0u},
    /* 39 native 0x6a4720 */ {0x80u,(uintptr_t)&audio_uart_registry_callback_5f9c8c,0u,0u},
    /* 40 native 0x6a4730 */ {0x100u,(uintptr_t)&audio_uart_registry_callback_5f9ce0,0u,0u},
    /* 41 native 0x6a4740 */ {0x103u,(uintptr_t)&audio_uart_registry_callback_47cf60,0u,0u},
    /* 42 native 0x6a4750 */ {0x107u,(uintptr_t)&audio_uart_registry_callback_49ed04,0u,0u},
};
_Static_assert(sizeof(audio_uart_display_registry_begin)==43u*16u,"registry byte count");
/* One-past-end section-relative alias; a linker absolute defsym
 * would lose the table relocation in the final image. */
__asm__(".globl audio_uart_display_registry_end\n"
        ".set audio_uart_display_registry_end, audio_uart_display_registry_begin + 688");
