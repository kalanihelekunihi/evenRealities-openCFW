#include <stdint.h>

/* Authenticated 10x5 callback table at native 0x334ba4..0x334c6c.
 * Values are decoded function identities, never executable bytes.
 * Source: em-inspection.bin, flash base 0x302400, offset 0x327a4,
 * SHA256 0de6e945a56ec886a92e44d4eaefe02fbca6db11f8747876e30bffb45cffce03.
 * The 30 external bodies are genuine code obligations until independently
 * mapped to selected source. Null cells are authenticated native data. */
typedef uint32_t (*opencfw_em9305_mode_callback_fn)(uintptr_t,uintptr_t);
#define CALLBACK(address) \
 extern uint32_t opencfw_em9305_mode_callback_##address(uintptr_t,uintptr_t)
CALLBACK(31635c);CALLBACK(3163ac);CALLBACK(316594);CALLBACK(323668);
CALLBACK(325a68);CALLBACK(325b14);CALLBACK(325b98);CALLBACK(325dec);
CALLBACK(325df4);CALLBACK(325f0c);CALLBACK(325f50);CALLBACK(326090);
CALLBACK(3260e4);CALLBACK(3269ec);CALLBACK(326a64);CALLBACK(326aa8);
CALLBACK(32c828);CALLBACK(32c86c);CALLBACK(32c884);CALLBACK(32c908);
CALLBACK(32ca90);CALLBACK(32cae4);CALLBACK(32cb0c);CALLBACK(32cde0);
CALLBACK(32ce84);CALLBACK(32cf50);CALLBACK(32cf80);CALLBACK(32cf94);
CALLBACK(32cfe8);CALLBACK(32cffc);
#define C(address) opencfw_em9305_mode_callback_##address
__attribute__((used,section(".rodata.em9305.mode_callbacks")))
const opencfw_em9305_mode_callback_fn opencfw_em9305_mode_callbacks_334ba4[10][5]={
 {C(32ca90),C(326a64),C(32cfe8),0,0},
 {C(32c86c),C(325a68),C(32c828),0,0},
 {0,C(325f0c),C(32cffc),C(325f50),C(32cffc)},
 {0,C(326aa8),C(32cf50),C(326aa8),C(32cf50)},
 {C(32cae4),C(325dec),C(32ce84),C(325df4),C(32ce84)},
 {C(32cb0c),C(3269ec),C(32cf94),C(323668),0},
 {C(316594),C(3163ac),C(31635c),C(323668),0},
 {C(32cf80),C(326090),C(32cde0),C(3260e4),C(32cde0)},
 {0,C(325b14),C(32c884),C(323668),0},
 {0,C(325b98),C(32c908),C(323668),0}
};
