/* Apollo main CLI state: the initialised cells that share the CLI command
 * .data region 0x200030e4..0x20003663 and the zero-initialised per-command
 * working storage. Sizes are the sizeof of the referencing declarations and
 * agree with the gap to the next stock RAM object; initial values are from
 * the decoded startup init image (RAM 0x20000000..0x20004557). */
#include <stdint.h>

/* RAM 0x200031b4 (.data): current working directory, initial "/". */
char g2_cli_cwd[128] = "/";

/* RAM 0x20003324 (.data): last erased XIP sector, initial 0xffffffff. */
uint32_t g2_xip_last_erased_sector_20003324 = 0xffffffffu;

/* RAM 0x200035e8 / 0x20003604 (.data, 26 bytes each, 2 bytes alignment
 * padding before the next object). */
char g2_translate_cli_source_200035e8[26] = "this is a src sentence 00";
char g2_translate_cli_target_20003604[26] = "this is a dst sentence 00";

/* ROM 0x6a9a88 (619 bytes + NUL): terminal "long query" test prompt. */
static const char terminal_long_query[] =
    "Please choose the best option \n"
    "for this very long query prompt.1 It is used to verify scroll behavior a"
    "nd bottom selection logic 2 It is used to verify scroll behavior and bot"
    "tom selection logic 3 It is used to verify scroll behavior and bottom se"
    "lection logic 4 It is used to verify scroll behavior and bottom selectio"
    "n logic 5 It is used to verify scroll behavior and bottom selection logi"
    "c 6 It is used to verify scroll behavior and bottom selection logic 7 It"
    " is used to verify scroll behavior and bottom selection logic 8 It is us"
    "ed to verify scroll behavior and bottom selection logic in the terminal "
    "query panel.";

/* RAM 0x20003630 (.data): pointer initialised to ROM 0x6a9a88. */
const char *g2_terminal_cli_long_query_20003630 = terminal_long_query;

/* Zero-initialised (.bss) state. */
uint8_t g2_cli_sync_test_data_2006c130[1024] __attribute__((aligned(4))); /* RAM 0x2006c130 */
char g2_cli_xmodem_path_200707ec[256];                                    /* RAM 0x200707ec */
char g2_codec_version_text_20073ce8[20];                                  /* RAM 0x20073ce8 */
uint32_t g2_translate_cli_counter_200748c0;                               /* RAM 0x200748c0 */
uint8_t g2_translate_cli_message_200651c0[0x850] __attribute__((aligned(4))); /* RAM 0x200651c0 */

/* Conversate CLI (SSRAM). */
uint8_t g2_conversate_cli_tag_200fa738[0x48c] __attribute__((aligned(4)));      /* RAM 0x200fa738 */
uint8_t g2_conversate_cli_start_200fabc4[0x94] __attribute__((aligned(4)));     /* RAM 0x200fabc4 */
uint8_t g2_conversate_cli_preplist_200fac58[0xaa8] __attribute__((aligned(4))); /* RAM 0x200fac58 */
uint8_t g2_conversate_cli_packet_200fb700[0xfa8] __attribute__((aligned(4)));   /* RAM 0x200fb700 */
uint8_t g2_conversate_cli_pkg_200fc6a8[0xfac] __attribute__((aligned(4)));      /* RAM 0x200fc6a8 */
uint8_t g2_conversate_cli_pb_buffer_200fd654[0xfb2];                            /* RAM 0x200fd654 */
uint8_t g2_conversate_cli_magic_2013be6c;                                       /* RAM 0x2013be6c */
uint8_t g2_conversate_cli_note_sent_2013be6d;                                   /* RAM 0x2013be6d */

/* Teleprompt CLI (SSRAM). */
uint8_t g2_teleprompt_cli_page_200fe608[0x40c] __attribute__((aligned(4)));     /* RAM 0x200fe608 */
uint8_t g2_teleprompt_cli_start_200fea14[0x30] __attribute__((aligned(4)));     /* RAM 0x200fea14 */
uint8_t g2_teleprompt_cli_aisync_200fea44[0xc] __attribute__((aligned(4)));     /* RAM 0x200fea44 */
uint8_t g2_teleprompt_cli_pkg_200fea50[0xf58] __attribute__((aligned(4)));      /* RAM 0x200fea50 */
uint8_t g2_teleprompt_cli_pb_buffer_200ff9a8[0xfa9];                            /* RAM 0x200ff9a8 */
uint8_t g2_teleprompt_cli_magic_20075001;                                       /* RAM 0x20075001 */

/* Terminal CLI. */
uint8_t g2_terminal_cli_msg_20100954[0x850] __attribute__((aligned(4)));        /* RAM 0x20100954 */
uint8_t g2_terminal_cli_pb_buffer_201011a4[0x878];                              /* RAM 0x201011a4 */
uint8_t g2_terminal_cli_magic_20075002;                                         /* RAM 0x20075002 */

/* SetLanguage CLI. */
uint8_t g2_language_cli_pb_buffer_2037cdac[0x80];                               /* RAM 0x2037cdac */
uint8_t g2_language_cli_pkg_2037ce3c[8] __attribute__((aligned(4)));            /* RAM 0x2037ce3c */
