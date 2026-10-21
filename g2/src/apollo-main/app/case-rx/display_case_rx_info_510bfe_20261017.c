/* Stock Main PB_RxGlassesCaseInfo, 0x510bfe. */
#include <stdint.h>
struct case_fault {uint32_t code;uint16_t kind;uint16_t reserved;const char *path;const char *function;uint32_t line;};
_Static_assert(sizeof(struct case_fault)==20u,"fault record ABI");
extern void *audio_uart_checksum_copy(void *,const void *,uint32_t);
extern void audio_ring_pb_assert_509b48(const void *);
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,...);
static const char module[]="pb.glasses_case";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_glasses_case\\pb_service_glasses_case.c";
static const char function_name[]="PB_RxGlassesCaseInfo";
uint32_t audio_uart_case_rx_info_510bfe(uint32_t unused,const uint8_t *info)
{
    (void)unused;
    if (info!=0) return 0u;
    static const struct case_fault template={0u,0u,0u,path,function_name,0x56u};
    struct case_fault fault;
    (void)audio_uart_checksum_copy(&fault,&template,20u);
    fault.kind=1u;
    audio_ring_pb_assert_509b48(&fault);
    if (audio_log_level()&2u)
        audio_log_extended(1u,module,path,function_name,0x58u,"POINTER NULL");
    if ((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(0x04000000u,
            "[pb.glasses_case]POINTER NULL","[pb.glasses_case]POINTER NULL");
    return 2u;
}
