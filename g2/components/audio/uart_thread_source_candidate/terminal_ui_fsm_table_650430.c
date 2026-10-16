/* Stock Terminal UI FSM table 0x650430, 13 x 40 x 8 bytes.
 * Source slice SHA-256 f14e57748e2148f596d9db59a74661cea2c4f28839059aaf42010d17fdd1fad0; callbacks retain explicit C imports. */
#include <stdint.h>

struct audio_terminal_ui_fsm_cell {
    uint32_t next_state;
    int32_t (*action)(uint32_t old_state, uint32_t event_payload);
};
_Static_assert(sizeof(struct audio_terminal_ui_fsm_cell) == 8u, "stock FSM row ABI");

extern int32_t audio_terminal_ui_action_5e522e(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e5290(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e52c2(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e5320(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e5386(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e53b8(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e5442(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e54a2(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e5580(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e576c(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e57c6(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e583c(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e58ba(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e598a(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e5a7e(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e5a94(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e5aae(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e5bc6(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e5cb0(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e5de0(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e5ed4(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e6018(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e6268(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e63b4(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e6400(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e6410(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e641c(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e6548(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e66d8(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e68b4(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e68dc(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e69a0(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e6b18(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e6ba0(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e6cb8(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e6d58(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e6dd0(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e6e30(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e6e88(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e6f60(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e7022(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e7068(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5ed208(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5ed318(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5ed492(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5ed4f8(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5ed748(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5ed758(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5ed870(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5ed8e0(uint32_t, uint32_t);

const struct audio_terminal_ui_fsm_cell audio_terminal_ui_fsm_table[13][40]
    __attribute__((section(".rodata.opencfw.terminal.ui_fsm"), used, aligned(4))) = {
    [0] = {
        [1] = {1u, audio_terminal_ui_action_5e576c},
    },
    [1] = {
        [2] = {3u, audio_terminal_ui_action_5e522e},
        [3] = {3u, audio_terminal_ui_action_5e5290},
        [4] = {3u, audio_terminal_ui_action_5e52c2},
        [22] = {10u, audio_terminal_ui_action_5e6548},
        [27] = {11u, audio_terminal_ui_action_5ed208},
        [28] = {1u, audio_terminal_ui_action_5ed318},
        [35] = {2u, audio_terminal_ui_action_5e5580},
    },
    [2] = {
        [2] = {3u, audio_terminal_ui_action_5e522e},
        [3] = {3u, audio_terminal_ui_action_5e5290},
        [4] = {3u, audio_terminal_ui_action_5e52c2},
        [8] = {4u, audio_terminal_ui_action_5e58ba},
        [15] = {7u, audio_terminal_ui_action_5e6018},
        [16] = {2u, audio_terminal_ui_action_5e6268},
        [17] = {2u, audio_terminal_ui_action_5e5ed4},
        [18] = {2u, audio_terminal_ui_action_5e63b4},
        [22] = {10u, audio_terminal_ui_action_5e6548},
        [27] = {11u, audio_terminal_ui_action_5ed208},
        [28] = {2u, audio_terminal_ui_action_5ed318},
        [35] = {2u, audio_terminal_ui_action_5e5580},
        [36] = {2u, audio_terminal_ui_action_5e7022},
        [37] = {2u, audio_terminal_ui_action_5e7022},
        [39] = {2u, audio_terminal_ui_action_5e5442},
    },
    [3] = {
        [2] = {3u, audio_terminal_ui_action_5e5320},
        [3] = {3u, audio_terminal_ui_action_5e5386},
        [4] = {3u, audio_terminal_ui_action_5e53b8},
        [5] = {2u, audio_terminal_ui_action_5e57c6},
        [6] = {7u, audio_terminal_ui_action_5e583c},
        [7] = {9u, audio_terminal_ui_action_5e641c},
        [16] = {3u, audio_terminal_ui_action_5e6268},
        [17] = {3u, audio_terminal_ui_action_5e5ed4},
        [18] = {3u, audio_terminal_ui_action_5e63b4},
        [27] = {11u, audio_terminal_ui_action_5ed208},
        [28] = {3u, audio_terminal_ui_action_5ed318},
        [35] = {3u, audio_terminal_ui_action_5e5580},
        [36] = {3u, audio_terminal_ui_action_5e7022},
        [37] = {3u, audio_terminal_ui_action_5e7022},
        [39] = {3u, audio_terminal_ui_action_5e5442},
    },
    [4] = {
        [2] = {3u, audio_terminal_ui_action_5e522e},
        [3] = {3u, audio_terminal_ui_action_5e5290},
        [4] = {3u, audio_terminal_ui_action_5e52c2},
        [9] = {5u, audio_terminal_ui_action_5e598a},
        [10] = {4u, audio_terminal_ui_action_5e5a7e},
        [11] = {6u, audio_terminal_ui_action_5e5aae},
        [12] = {2u, audio_terminal_ui_action_5e5de0},
        [16] = {2u, audio_terminal_ui_action_5e6268},
        [17] = {2u, audio_terminal_ui_action_5e5ed4},
        [18] = {4u, audio_terminal_ui_action_5e63b4},
        [35] = {2u, audio_terminal_ui_action_5e5580},
    },
    [5] = {
        [2] = {3u, audio_terminal_ui_action_5e522e},
        [3] = {3u, audio_terminal_ui_action_5e5290},
        [4] = {3u, audio_terminal_ui_action_5e52c2},
        [10] = {5u, audio_terminal_ui_action_5e5a94},
        [11] = {6u, audio_terminal_ui_action_5e5aae},
        [12] = {2u, audio_terminal_ui_action_5e5de0},
        [14] = {2u, audio_terminal_ui_action_5e5cb0},
        [16] = {2u, audio_terminal_ui_action_5e6268},
        [17] = {2u, audio_terminal_ui_action_5e5ed4},
        [18] = {5u, audio_terminal_ui_action_5e63b4},
        [35] = {2u, audio_terminal_ui_action_5e5580},
    },
    [6] = {
        [2] = {3u, audio_terminal_ui_action_5e522e},
        [3] = {3u, audio_terminal_ui_action_5e5290},
        [4] = {3u, audio_terminal_ui_action_5e52c2},
        [12] = {2u, audio_terminal_ui_action_5e5de0},
        [13] = {7u, audio_terminal_ui_action_5e5bc6},
        [14] = {2u, audio_terminal_ui_action_5e5cb0},
        [16] = {2u, audio_terminal_ui_action_5e6268},
        [17] = {2u, audio_terminal_ui_action_5e5ed4},
        [18] = {6u, audio_terminal_ui_action_5e63b4},
        [35] = {2u, audio_terminal_ui_action_5e5580},
        [36] = {6u, audio_terminal_ui_action_5e6dd0},
        [37] = {6u, audio_terminal_ui_action_5e6e30},
    },
    [7] = {
        [2] = {3u, audio_terminal_ui_action_5e522e},
        [3] = {3u, audio_terminal_ui_action_5e5290},
        [4] = {3u, audio_terminal_ui_action_5e52c2},
        [15] = {7u, audio_terminal_ui_action_5e6018},
        [16] = {2u, audio_terminal_ui_action_5e6268},
        [17] = {2u, audio_terminal_ui_action_5e5ed4},
        [18] = {7u, audio_terminal_ui_action_5e63b4},
        [19] = {7u, audio_terminal_ui_action_5e6400},
        [20] = {7u, audio_terminal_ui_action_5e6410},
        [21] = {9u, audio_terminal_ui_action_5e641c},
        [22] = {10u, audio_terminal_ui_action_5e6548},
        [26] = {8u, audio_terminal_ui_action_5e6b18},
        [27] = {11u, audio_terminal_ui_action_5ed208},
        [28] = {7u, audio_terminal_ui_action_5ed318},
        [35] = {2u, audio_terminal_ui_action_5e5580},
        [36] = {7u, audio_terminal_ui_action_5e7022},
        [37] = {7u, audio_terminal_ui_action_5e7022},
        [38] = {2u, audio_terminal_ui_action_5e7068},
        [39] = {7u, audio_terminal_ui_action_5e5442},
    },
    [8] = {
        [2] = {3u, audio_terminal_ui_action_5e522e},
        [3] = {3u, audio_terminal_ui_action_5e5290},
        [4] = {3u, audio_terminal_ui_action_5e52c2},
        [14] = {7u, audio_terminal_ui_action_5e6ba0},
        [15] = {8u, audio_terminal_ui_action_5e6018},
        [16] = {2u, audio_terminal_ui_action_5e6268},
        [17] = {2u, audio_terminal_ui_action_5e5ed4},
        [18] = {8u, audio_terminal_ui_action_5e63b4},
        [21] = {8u, audio_terminal_ui_action_5e6d58},
        [27] = {11u, audio_terminal_ui_action_5ed208},
        [28] = {8u, audio_terminal_ui_action_5ed318},
        [35] = {2u, audio_terminal_ui_action_5e5580},
        [36] = {8u, audio_terminal_ui_action_5e6cb8},
        [37] = {8u, audio_terminal_ui_action_5e6cb8},
        [38] = {2u, audio_terminal_ui_action_5e7068},
        [39] = {8u, audio_terminal_ui_action_5e5442},
    },
    [9] = {
        [2] = {3u, audio_terminal_ui_action_5e522e},
        [3] = {3u, audio_terminal_ui_action_5e5290},
        [4] = {3u, audio_terminal_ui_action_5e52c2},
        [15] = {7u, audio_terminal_ui_action_5e6018},
        [16] = {2u, audio_terminal_ui_action_5e6268},
        [17] = {2u, audio_terminal_ui_action_5e5ed4},
        [18] = {9u, audio_terminal_ui_action_5e63b4},
        [25] = {7u, audio_terminal_ui_action_5e69a0},
        [28] = {9u, audio_terminal_ui_action_5ed318},
        [35] = {2u, audio_terminal_ui_action_5e5580},
        [36] = {9u, audio_terminal_ui_action_5e6e88},
        [37] = {9u, audio_terminal_ui_action_5e6f60},
    },
    [10] = {
        [2] = {3u, audio_terminal_ui_action_5e522e},
        [3] = {3u, audio_terminal_ui_action_5e5290},
        [4] = {3u, audio_terminal_ui_action_5e52c2},
        [15] = {10u, audio_terminal_ui_action_5e6018},
        [16] = {2u, audio_terminal_ui_action_5e6268},
        [17] = {2u, audio_terminal_ui_action_5e5ed4},
        [18] = {10u, audio_terminal_ui_action_5e63b4},
        [19] = {10u, audio_terminal_ui_action_5e6400},
        [23] = {10u, audio_terminal_ui_action_5e66d8},
        [24] = {10u, audio_terminal_ui_action_5e68b4},
        [28] = {10u, audio_terminal_ui_action_5ed318},
        [31] = {10u, audio_terminal_ui_action_5e68dc},
        [35] = {10u, audio_terminal_ui_action_5e5580},
        [39] = {10u, audio_terminal_ui_action_5e5442},
    },
    [11] = {
        [2] = {3u, audio_terminal_ui_action_5e522e},
        [3] = {3u, audio_terminal_ui_action_5e5290},
        [4] = {3u, audio_terminal_ui_action_5e52c2},
        [5] = {11u, audio_terminal_ui_action_5ed318},
        [6] = {11u, audio_terminal_ui_action_5ed318},
        [7] = {11u, audio_terminal_ui_action_5ed318},
        [18] = {11u, audio_terminal_ui_action_5e63b4},
        [22] = {10u, audio_terminal_ui_action_5e6548},
        [28] = {11u, audio_terminal_ui_action_5ed318},
        [29] = {11u, audio_terminal_ui_action_5ed4f8},
        [30] = {11u, audio_terminal_ui_action_5ed748},
        [31] = {11u, audio_terminal_ui_action_5ed758},
        [32] = {12u, audio_terminal_ui_action_5ed870},
        [33] = {11u, audio_terminal_ui_action_5ed8e0},
        [34] = {2u, audio_terminal_ui_action_5e54a2},
        [35] = {2u, audio_terminal_ui_action_5e5580},
        [36] = {11u, audio_terminal_ui_action_5ed492},
        [37] = {11u, audio_terminal_ui_action_5ed492},
    },
    [12] = {
        [2] = {3u, audio_terminal_ui_action_5e522e},
        [3] = {3u, audio_terminal_ui_action_5e5290},
        [4] = {3u, audio_terminal_ui_action_5e52c2},
        [8] = {4u, audio_terminal_ui_action_5e58ba},
        [22] = {10u, audio_terminal_ui_action_5e6548},
        [27] = {11u, audio_terminal_ui_action_5ed208},
        [28] = {12u, audio_terminal_ui_action_5ed318},
        [35] = {2u, audio_terminal_ui_action_5e5580},
    },
};

_Static_assert(sizeof audio_terminal_ui_fsm_table == 4160u, "stock FSM table extent");
