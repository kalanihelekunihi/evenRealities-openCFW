/* Product FreeRTOS-Plus-CLI "xmodem" command, stock directory
 * D:\01_workspace\s200_ap510b_iar_git\kernel\FreeRTOS-Plus-CLI\prvCommand\
 * (file name not retained). Native handler 0x581774..0x581839, inline
 * strings 0x581844..0x58184f, pool 0x581850..0x581857. The registrar
 * 0x58183a is in a-59-cli-commands/prvCommand_registrars.c.
 *
 *   xmodem -r <file>   receive <cwd>/<file> over the shell UART (XMODEM)
 *   xmodem -s <file>   send <cwd>/<file>
 * EasyLogger output is stopped for the transfer so log lines do not
 * corrupt the XMODEM stream. */
#include <stddef.h>
#include <stdint.h>
#include "../a-59-cli-commands/cli_commands.h"

#define XMODEM_PATH_BYTES 256u

extern int32_t g2_lfs_memcmp(const void *a, const void *b, uint32_t len); /* 0x4751c8 memcmp */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern char *g2_strcpy_48d540(char *dst, const char *src);
extern uint32_t g2_log_module_length(const char *text);            /* 0x44a43c strlen */
extern uint8_t *g2_strcat(uint8_t *dst, const uint8_t *src);       /* 0x567c80 strcat */
extern void elog_start_43d19a(void);                               /* EasyLogger elog_start */
extern void elog_stop_43d1fc(void);                                /* EasyLogger elog_stop */
/* File-backed XMODEM receive (sends 'C', CRC mode) / transmit; the size
 * argument is 0 at this call site. */
extern int32_t xmodem_receive_file_595af2(const char *path, int32_t size);
extern int32_t xmodem_transmit_file_595cda(const char *path, int32_t size);
extern char g2_cli_cwd[128];                                       /* RAM 0x200031b4 */
extern char g2_cli_xmodem_path_200707ec[XMODEM_PATH_BYTES];        /* RAM 0x200707ec */

static const char s_receive[] = "-r"; /* ROM 0x581844 */
static const char s_slash[] = "/";    /* ROM 0x581848 */
static const char s_send[] = "-s";    /* ROM 0x58184c */

int32_t cli_cmd_xmodem_581774(char *write_buffer, size_t write_buffer_len, const char *command_string);

static void xmodem_build_path(const char *name)
{
    char *path = g2_cli_xmodem_path_200707ec;

    (void)aeabi_memset_43c0e4(path, XMODEM_PATH_BYTES, 0);
    if (path[g2_log_module_length(g2_strcpy_48d540(path, g2_cli_cwd)) - 1u] != '/')
        (void)g2_strcat((uint8_t *)path, (const uint8_t *)s_slash);
    (void)g2_strcat((uint8_t *)path, (const uint8_t *)name);
}

int32_t cli_cmd_xmodem_581774(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    int32_t length;
    const char *option;
    const char *name;

    (void)write_buffer;
    (void)write_buffer_len;
    option = freertos_cli_get_parameter_5848fc(command_string, 1u, &length);
    name = freertos_cli_get_parameter_5848fc(command_string, 2u, &length);
    if (g2_lfs_memcmp(option, s_receive, 2u) == 0) {
        elog_stop_43d1fc();
        xmodem_build_path(name);
        (void)xmodem_receive_file_595af2(g2_cli_xmodem_path_200707ec, 0);
        elog_start_43d19a();
    } else if (g2_lfs_memcmp(option, s_send, 2u) == 0) {
        elog_stop_43d1fc();
        xmodem_build_path(name);
        (void)xmodem_transmit_file_595cda(g2_cli_xmodem_path_200707ec, 0);
        elog_start_43d19a();
    }
    return 0;
}
