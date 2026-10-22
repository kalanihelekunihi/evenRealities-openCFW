/* FreeRTOS-Plus-CLI command registration stubs for the product shell commands.
 * Stock source paths not proven by strings; each stub follows its command interpreter in a
 * prvCommand_*.c file under D:\01_workspace\s200_ap510b_iar_git\kernel\FreeRTOS-Plus-CLI\prvCommand\
 * (compare prvCommand_filesystem.c). They are collected here until those interpreters are
 * reconstructed; move each stub into its interpreter's unit then.
 * The shell task shell_task_541600 calls them in this order at 0x541640..0x541658, right after
 * cli_register_terminal_command_5836b8 (cli_terminal_command.c).
 *
 * The CLI_Command_Definition_t records live in initialised RAM (decoded from the 0x20000000
 * init stream); the fourth word is cExpectedNumberOfParameters (-1 = variable):
 *   0x200034a8 "set"           -> 0x583918, -1      0x20003458 "SetLanguage" -> 0x58421c, 1
 *   0x20003184 "buzzer"        -> 0x583df8, -1      0x20003478 "onboarding"  -> 0x58435c, -1
 *   0x20003328 "gpio"          -> 0x58402a, 2       0x200034b8 "get"         -> 0x5844fe, -1
 *   0x20003174 "box_force_out" -> 0x584128, 1 */
#include <stdint.h>

typedef struct {
    const char *command;   /* +0x0 */
    const char *help;      /* +0x4 */
    void *handler;         /* +0x8 pdCOMMAND_LINE_CALLBACK */
    int8_t expected_params; /* +0xc */
} g2_cli_command_definition_t;
_Static_assert(sizeof(g2_cli_command_definition_t) == 16, "CLI definition is 16 bytes");

extern g2_cli_command_definition_t g2_cli_cmd_set_200034a8;           /* RAM 0x200034a8 */
extern g2_cli_command_definition_t g2_cli_cmd_buzzer_20003184;        /* RAM 0x20003184 */
extern g2_cli_command_definition_t g2_cli_cmd_gpio_20003328;          /* RAM 0x20003328 */
extern g2_cli_command_definition_t g2_cli_cmd_box_force_out_20003174; /* RAM 0x20003174 */
extern g2_cli_command_definition_t g2_cli_cmd_set_language_20003458;  /* RAM 0x20003458 */
extern g2_cli_command_definition_t g2_cli_cmd_onboarding_20003478;    /* RAM 0x20003478 */
extern g2_cli_command_definition_t g2_cli_cmd_get_200034b8;           /* RAM 0x200034b8 */

extern int32_t freertos_cli_register_command_5847ac(const g2_cli_command_definition_t *definition); /* FreeRTOS_CLIRegisterCommand */

void cli_register_set_command_583cec(void);
void cli_register_buzzer_command_583f74(void);
void cli_register_gpio_command_5840f4(void);
void cli_register_box_force_out_command_5841ee(void);
void cli_register_set_language_command_584320(void);
void cli_register_onboarding_command_584430(void);
void cli_register_get_command_584702(void);

void cli_register_set_command_583cec(void)
{
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_set_200034a8);
}

void cli_register_buzzer_command_583f74(void)
{
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_buzzer_20003184);
}

void cli_register_gpio_command_5840f4(void)
{
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_gpio_20003328);
}

void cli_register_box_force_out_command_5841ee(void)
{
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_box_force_out_20003174);
}

void cli_register_set_language_command_584320(void)
{
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_set_language_20003458);
}

void cli_register_onboarding_command_584430(void)
{
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_onboarding_20003478);
}

void cli_register_get_command_584702(void)
{
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_get_200034b8);
}
