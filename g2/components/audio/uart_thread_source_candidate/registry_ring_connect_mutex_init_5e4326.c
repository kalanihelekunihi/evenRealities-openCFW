/* Apollo TerminalActionMutex initialization 0x5e4326. */
#include <stdint.h>

struct os_mutex_attr_candidate {
    const char *name;
    uint32_t attr_bits;
    void *cb_mem;
    uint32_t cb_size;
};
_Static_assert(sizeof(struct os_mutex_attr_candidate)==16u,"CMSIS mutex attribute ABI");

uint32_t audio_registry_ring_connect_mutex_handle; /* native BSS 0x20074a84 */
static const struct os_mutex_attr_candidate attr={"TerminalActionMutex",0u,0,0u};
extern void *audio_uart_mutex_new(const void *); /* selected 0x44971c */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="terminal";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal.c";
static const char function[]="terminal_action_mutex_init_internal";
static const char message[]="terminal action mutex create failed";
static const char compact[]="[terminal]terminal action mutex create failed";

uint32_t audio_registry_ring_connect_mutex_init_5e4326(void) {
    if(audio_registry_ring_connect_mutex_handle!=0u) return 0u;
    audio_registry_ring_connect_mutex_handle=(uint32_t)(uintptr_t)audio_uart_mutex_new(&attr);
    if(audio_registry_ring_connect_mutex_handle!=0u) return 0u;
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(1u,module,path,function,56u,message);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x04000000u,compact,compact);
    return UINT32_MAX;
}
