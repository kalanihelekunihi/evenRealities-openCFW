/* Reconstructed call-site adapters, not stock function-body replacements.
 * Only the documented fixed caller lines are supported. Stock strings are
 * readonly metadata. See logger-call-metadata/ for instruction provenance. */
#include <stdint.h>
extern void opencfw_boot_elog_output(uint32_t,const char *,const char *,const char *,long,const char *,...);
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define H(n) W(0x20026ef8u+4u*(n))
static const char path[]="ota/s200_firmware_ota.bin";
void opencfw_dfu_log_detail_native(uint32_t level,uint32_t line,uint32_t detail){
 switch(line){
 case 356u:opencfw_boot_elog_output(level,"task.dfu","D:\\01_workspace\\s200_ap510b_iar_git\\product\\s200\\bootloader\\threads\\thread_dfu.c","dfu_task_msg_send",356,"dfu_task_msg_send queue null");return;
 case 361u:opencfw_boot_elog_output(level,"task.dfu","D:\\01_workspace\\s200_ap510b_iar_git\\product\\s200\\bootloader\\threads\\thread_dfu.c","dfu_task_msg_send",361,"msg missed");return;
 case 409u:opencfw_boot_elog_output(level,"task.dfu","D:\\01_workspace\\s200_ap510b_iar_git\\product\\s200\\bootloader\\threads\\thread_dfu.c","thread_dfu",409,"Notify error!");return;
 case 523u:opencfw_boot_elog_output(level,"task.dfu","D:\\01_workspace\\s200_ap510b_iar_git\\product\\s200\\bootloader\\threads\\thread_dfu.c","_thread_msg_handler",523,"EVENT_DFU_VALID,updata firmware");return;
 case 526u:opencfw_boot_elog_output(level,"task.dfu","D:\\01_workspace\\s200_ap510b_iar_git\\product\\s200\\bootloader\\threads\\thread_dfu.c","_thread_msg_handler",526,"ERR-Open failed %s",path);return;
 case 532u:opencfw_boot_elog_output(level,"task.dfu","D:\\01_workspace\\s200_ap510b_iar_git\\product\\s200\\bootloader\\threads\\thread_dfu.c","_thread_msg_handler",532,"ERR-Read failed %s : %zu",path,detail);return;
 case 538u:opencfw_boot_elog_output(level,"task.dfu","D:\\01_workspace\\s200_ap510b_iar_git\\product\\s200\\bootloader\\threads\\thread_dfu.c","_thread_msg_handler",538,"blobSize = %d(0x%x)",H(0)&0x00ffffffu,H(0)&0x00ffffffu);return;
 case 539u:opencfw_boot_elog_output(level,"task.dfu","D:\\01_workspace\\s200_ap510b_iar_git\\product\\s200\\bootloader\\threads\\thread_dfu.c","_thread_msg_handler",539,"crcCheck = %d",(H(0)>>26)&1u);return;
 case 540u:opencfw_boot_elog_output(level,"task.dfu","D:\\01_workspace\\s200_ap510b_iar_git\\product\\s200\\bootloader\\threads\\thread_dfu.c","_thread_msg_handler",540,"crc = 0x%x",H(1));return;
 case 541u:opencfw_boot_elog_output(level,"task.dfu","D:\\01_workspace\\s200_ap510b_iar_git\\product\\s200\\bootloader\\threads\\thread_dfu.c","_thread_msg_handler",541,"magicNum = %d(0x%x)",H(4)&255u,H(4)&255u);return;
 case 542u:opencfw_boot_elog_output(level,"task.dfu","D:\\01_workspace\\s200_ap510b_iar_git\\product\\s200\\bootloader\\threads\\thread_dfu.c","_thread_msg_handler",542,"targetRunAddr = 0x%x",H(5));return;
 case 553u:opencfw_boot_elog_output(level,"task.dfu","D:\\01_workspace\\s200_ap510b_iar_git\\product\\s200\\bootloader\\threads\\thread_dfu.c","_thread_msg_handler",553,"bootMetadataInfo.targetRunAddr = 0x%x(0x%x)",H(5),0x438000u);return;
 case 558u:opencfw_boot_elog_output(level,"task.dfu","D:\\01_workspace\\s200_ap510b_iar_git\\product\\s200\\bootloader\\threads\\thread_dfu.c","_thread_msg_handler",558,"updata firmware success SP = 0x%x",W(H(5)));return;
 case 559u:opencfw_boot_elog_output(level,"task.dfu","D:\\01_workspace\\s200_ap510b_iar_git\\product\\s200\\bootloader\\threads\\thread_dfu.c","_thread_msg_handler",559,"APP jumpaddr app(0x%x) = 0x%x",H(5),W(H(5)+4u));return;
 case 567u:opencfw_boot_elog_output(level,"task.dfu","D:\\01_workspace\\s200_ap510b_iar_git\\product\\s200\\bootloader\\threads\\thread_dfu.c","_thread_msg_handler",567,"app firmware SP = 0x%x",W(H(5)));return;
 case 568u:opencfw_boot_elog_output(level,"task.dfu","D:\\01_workspace\\s200_ap510b_iar_git\\product\\s200\\bootloader\\threads\\thread_dfu.c","_thread_msg_handler",568,"just jump to app(0x%x) = 0x%x",H(5),W(H(5)+4u));return;
 default:return; /* No corresponding fixed source callsite. */
 }
}
void opencfw_dfu_log_native(uint32_t level,uint32_t line){opencfw_dfu_log_detail_native(level,line,0);}
void opencfw_allocator_log_native(uint32_t line){if(line==19u)opencfw_boot_elog_output(4,"tlsf","D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\tlsf\\tlsf_init.c","tlsf_adapter_init",19,"tlsf init.");}
void opencfw_control_log_native(uint32_t level,uint32_t line){if(line==505u)opencfw_boot_elog_output(level,"task.dfu","D:\\01_workspace\\s200_ap510b_iar_git\\product\\s200\\bootloader\\threads\\thread_dfu.c","bootloader_error_reset",505,"Bootloader ota fail, system reset!!!");}
