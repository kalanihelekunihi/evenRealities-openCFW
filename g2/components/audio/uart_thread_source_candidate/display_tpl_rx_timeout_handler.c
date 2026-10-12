/* Native TPL_RxPacketTimeoutHandler 0x4b8da2. The fourth ARM entry register
 * is the inherited fourth argument to the initial extended diagnostic. */
#include <stdint.h>
extern uint8_t audio_tpl_contexts[4u * 56u]; /* TPL_Init owns exact 0xe0 clear */
extern void tpl_context_free_004b8ba2(uint8_t *);
extern void audio_tpl_response(uint8_t pipe, uint8_t sync, uint8_t service, uint8_t code); /* native 0x4b9012 */
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "prot.tran";
static const char source[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\transport_protocol\\transport_protocol.c";
static const char function[] = "TPL_RxPacketTimeoutHandler";
static const char begin[] = "TPL_RxPacketTimeoutHandler: serviceID=%d, syncID=%d, pipeID=%d";
static const char begin_short[] = "[prot.tran]TPL_RxPacketTimeoutHandler: serviceID=%d, syncID=%d, pipeID=%d";
static const char found[] = "TPL_RxPacketTimeoutHandler: found ctx at index %d";
static const char found_short[] = "[prot.tran]TPL_RxPacketTimeoutHandler: found ctx at index %d";
static const char freeing[] = "TPL_RxPacketTimeoutHandler: freeing resources for ctx";
static const char freeing_short[] = "[prot.tran]TPL_RxPacketTimeoutHandler: freeing resources for ctx";
static const char already[] = "TPL_RxPacketTimeoutHandler: ctx already freed, isUsed=0";
static const char already_short[] = "[prot.tran]TPL_RxPacketTimeoutHandler: ctx already freed, isUsed=0";
static const char not_found[] = "TPL_RxPacketTimeoutHandler: ctx not found, may have been freed already";
static const char not_found_short[] = "[prot.tran]TPL_RxPacketTimeoutHandler: ctx not found, may have been freed already";

static uint8_t extended(void) { return (audio_log_level() & 2u) != 0u; }
static uint8_t compact(void)
{
    return (audio_log_level() & 1u) != 0u || (audio_log_level() & 4u) != 0u;
}
static void diagnostic(uint32_t line, const char *plain, const char *short_text,
                       uint32_t mask)
{
    if (extended()) audio_log_extended(2u, module, source, function, line, plain);
    if (compact()) (void)compressed_log_output(mask, short_text, short_text);
}

void audio_tpl_rx_timeout_handler_body(const uint8_t *ids, uint32_t ignored1,
                                        uint32_t ignored2, uint32_t inherited_r3)
{
    (void)ignored1; (void)ignored2;
    if (extended())
        audio_log_extended(2u, module, source, function, 0x11fu, begin,
                           ids[0], ids[1], ids[2], inherited_r3);
    if (compact())
        (void)compressed_log_output(0x08c00000u, begin_short, begin_short,
                                    ids[0], ids[1], ids[2]);
    uint8_t *context = 0;
    for (uint32_t i = 0u; i < 4u; ++i) {
        uint8_t *row = audio_tpl_contexts + i * 56u;
        if (row[0x30u] != 0u && row[0] == ids[0] && row[1] == ids[1] &&
            row[0x33u] == ids[2]) {
            context = row;
            if (extended()) audio_log_extended(2u, module, source, function,
                                               0x127u, found, i);
            if (compact()) (void)compressed_log_output(0x08400000u,
                                                       found_short, found_short, i);
            break;
        }
    }
    if (context == 0)
        diagnostic(0x134u, not_found, not_found_short, 0x08000000u);
    else if (context[0x30u] == 0u)
        diagnostic(0x131u, already, already_short, 0x08000000u);
    else {
        diagnostic(0x12eu, freeing, freeing_short, 0x08000000u);
        tpl_context_free_004b8ba2(context);
    }
    audio_tpl_response(ids[2], ids[1], ids[0], 3u);
}

__attribute__((naked)) void TPL_RxPacketTimeoutHandler(const uint8_t *ids __attribute__((unused)))
{
    __asm__ volatile("b audio_tpl_rx_timeout_handler_body");
}
