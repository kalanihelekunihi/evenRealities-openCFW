#!/usr/bin/env python3
"""Trial-link eight source-owned option callbacks into Apollo-main display C."""
import hashlib,json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[4]
base=root/'build/c-firmware/root-main-round604'
display=root/'build/c-firmware/root-main-display-driver-relocated-fifteen-round711'
option=root/'build/c-firmware/root-main-uled-option-service-round681'
out=root/'build/c-firmware/root-main-uled-option-fifteen-sync-alias-integration-round749'
out.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
selected_receipt=json.loads((base/'receipt.json').read_text())
selected_link=selected_receipt['images']['apollo_main']['relocatable_link']
display_audit=json.loads((display/'link-audit.json').read_text())
option_audit=json.loads((option/'link-audit.json').read_text())
selected=base/'apollo_main/candidate.o'
display_object=display/'display-driver-combined.o'
option_object=option/'uled-option-service-candidate.o'
leaf_object=out/'display_driver_uled_option_leaf_pair.o'
leaf_source=Path(__file__).resolve().parent/'display_driver_uled_option_leaf_pair.c'
setup_source=Path(__file__).resolve().parent/'display_driver_uled_option_setup_pair.c'
enable_source=Path(__file__).resolve().parent/'display_driver_uled_option_enable_pair_bothfinishbound.c'
setup_object=out/'display_driver_uled_option_setup_pair.o'
enable_object=out/'display_driver_uled_option_enable_pair.o'
pin_source=Path(__file__).resolve().parent/'display_driver_uled_option_pin_prepare_pair.c'
pin_object=out/'display_driver_uled_option_pin_prepare_pair.o'
pre_source=Path(__file__).resolve().parent/'display_driver_uled_option_type1_pre.c'
pre_object=out/'display_driver_uled_option_type1_pre.o'
power_source=Path(__file__).resolve().parent/'display_driver_uled_option_type1_power_pmicbound.c'
power_object=out/'display_driver_uled_option_type1_power_pmicbound.o'
pmic_source=Path(__file__).resolve().parent/'display_driver_uled_option_pmic_helpers.c'
pmic_object=out/'display_driver_uled_option_pmic_helpers.o'
transport_source=Path(__file__).resolve().parent/'display_driver_uled_option_pmic_transport.c'
transport_object=out/'display_driver_uled_option_pmic_transport.o'
type0_pre_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_pre.c'
type0_pre_object=out/'display_driver_uled_option_type0_pre.o'
mode4_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_mode4.c'
mode4_object=out/'display_driver_uled_option_type0_mode4.o'
ldo_find_source=Path(__file__).resolve().parent/'display_driver_uled_option_ldo_find.c'
ldo_find_object=out/'display_driver_uled_option_ldo_find.o'
ldo_helpers_source=Path(__file__).resolve().parent/'display_driver_uled_option_ldo_helpers.c'
ldo_helpers_object=out/'display_driver_uled_option_ldo_helpers.o'
frame_source=Path(__file__).resolve().parent/'display_driver_uled_option_frame_start_pair.c'
frame_object=out/'display_driver_uled_option_frame_start_pair.o'
finish_source=Path(__file__).resolve().parent/'display_driver_uled_option_type1_finish.c'
finish_object=out/'display_driver_uled_option_type1_finish.o'
buck_source=Path(__file__).resolve().parent/'display_driver_uled_option_buck0_enable.c'
buck_object=out/'display_driver_uled_option_buck0_enable.o'
bus_source=Path(__file__).resolve().parent/'display_driver_uled_flash_bus_prepare.c'
bus_object=out/'display_driver_uled_flash_bus_prepare.o'
type0_finish_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_finish.c'
type0_finish_object=out/'display_driver_uled_option_type0_finish.o'
mode4_finish_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_mode4_finish.c'
mode4_finish_object=out/'display_driver_uled_option_type0_mode4_finish.o'
get_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_get.c'
get_object=out/'display_driver_uled_option_type0_get.o'
read_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_read.c'
read_object=out/'display_driver_uled_option_type0_read.o'
packet_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_packet_reused.c'
packet_object=out/'display_driver_uled_option_type0_packet.o'
encode_source=Path(__file__).resolve().parent/'display_driver_uled_option_packet_encode.c'
encode_object=out/'display_driver_uled_option_packet_encode.o'
validate_source=Path(__file__).resolve().parent/'display_driver_uled_option_packet_validate.c'
validate_object=out/'display_driver_uled_option_packet_validate.o'
begin_source=Path(__file__).resolve().parent/'display_driver_uled_option_packet_begin_reused.c'
begin_object=out/'display_driver_uled_option_packet_begin.o'
check_source=Path(__file__).resolve().parent/'display_driver_uled_option_device_check_fully_reused.c'
check_object=out/'display_driver_uled_option_device_check.o'
end_source=Path(__file__).resolve().parent/'display_driver_uled_option_packet_end.c'
end_object=out/'display_driver_uled_option_packet_end.o'
aux_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_aux_finish.c'
aux_object=out/'display_driver_uled_option_type0_aux_finish.o'
complete_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_aux_complete.c'
complete_object=out/'display_driver_uled_option_type0_aux_complete.o'
status_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_aux_status.c'
status_object=out/'display_driver_uled_option_type0_aux_status.o'
regwrite_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_aux_reg_write.c'
regwrite_object=out/'display_driver_uled_option_type0_aux_reg_write.o'
packetwrite_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_packet_write.c'
packetwrite_object=out/'display_driver_uled_option_type0_packet_write.o'
recover_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_aux_recover.c'
recover_object=out/'display_driver_uled_option_type0_aux_recover.o'
context_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_context.c'
context_object=out/'display_driver_uled_option_type0_context.o'
snapshot_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_context_snapshot.c'
snapshot_object=out/'display_driver_uled_option_type0_context_snapshot.o'
aux_config_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_aux_config.c'
aux_config_object=out/'display_driver_uled_option_type0_aux_config.o'
command_lower_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_command_lower.c'
command_lower_object=out/'display_driver_uled_option_type0_command_lower.o'
frame_lower_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_frame_lower.c'
frame_lower_object=out/'display_driver_uled_option_type0_frame_lower.o'
delay_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_delay.c'
delay_object=out/'display_driver_uled_option_type0_delay.o'
qspi_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_qspi_write.c'
qspi_object=out/'display_driver_uled_option_type0_qspi_write.o'
modes_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_mspi_modes.c'
modes_object=out/'display_driver_uled_option_type0_mspi_modes.o'
reconfigure_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_device_reconfigure.c'
reconfigure_object=out/'display_driver_uled_option_type0_device_reconfigure.o'
mspi_power_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_mspi_power.c'
mspi_power_object=out/'display_driver_uled_option_type0_mspi_power.o'
lifecycle_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_mspi_lifecycle.c'
lifecycle_object=out/'display_driver_uled_option_type0_mspi_lifecycle.o'
stop_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_transfer_stop.c'
stop_object=out/'display_driver_uled_option_type0_transfer_stop.o'
prepare_stop_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_transfer_prepare_stop.c'
prepare_stop_object=out/'display_driver_uled_option_type0_transfer_prepare_stop.o'
pin_mode_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_mspi_pin_mode.c'
pin_mode_object=out/'display_driver_uled_option_type0_mspi_pin_mode.o'
pin_apply_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_pin_apply.c'
pin_apply_object=out/'display_driver_uled_option_type0_pin_apply.o'
transfer_setup_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_transfer_setup.c'
transfer_setup_object=out/'display_driver_uled_option_type0_transfer_setup.o'
interrupt_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_mspi_interrupt.c'
interrupt_object=out/'display_driver_uled_option_type0_mspi_interrupt.o'
cache_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_cache_prepare.c'
cache_object=out/'display_driver_uled_option_type0_cache_prepare.o'
irq_context_source=Path(__file__).resolve().parent/'display_driver_uled_irq_context.c'
irq_context_object=out/'display_driver_uled_irq_context.o'
scheduler_source=Path(__file__).resolve().parent/'display_driver_uled_scheduler_state.c'
scheduler_object=out/'display_driver_uled_scheduler_state.o'
type1_frame_lower_source=Path(__file__).resolve().parent/'display_driver_uled_type1_frame_lower.c'
type1_frame_lower_object=out/'display_driver_uled_type1_frame_lower.o'
type1_chip_id_source=Path(__file__).resolve().parent/'display_driver_uled_type1_chip_id.c'
type1_chip_id_object=out/'display_driver_uled_type1_chip_id.o'
type1_bank_source=Path(__file__).resolve().parent/'display_driver_uled_type1_read_bank.c'
type1_bank_object=out/'display_driver_uled_type1_read_bank.o'
type1_register_source=Path(__file__).resolve().parent/'display_driver_uled_type1_read_register.c'
type1_register_object=out/'display_driver_uled_type1_read_register.o'
type1_sn_source=Path(__file__).resolve().parent/'display_driver_uled_type1_read_sn.c'
type1_sn_object=out/'display_driver_uled_type1_read_sn.o'
type1_write_source=Path(__file__).resolve().parent/'display_driver_uled_type1_write_register.c'
type1_write_object=out/'display_driver_uled_type1_write_register.o'
type0_configure_source=Path(__file__).resolve().parent/'display_driver_uled_type0_configure.c'
type0_configure_object=out/'display_driver_uled_type0_configure.o'
type0_offset_source=Path(__file__).resolve().parent/'display_driver_uled_type0_set_offset.c'
type0_offset_object=out/'display_driver_uled_type0_set_offset.o'
mspi_init_source=Path(__file__).resolve().parent/'display_driver_uled_option_config.c'
mspi_init_object=out/'display_driver_uled_option_config.o'
for source,obj in ((mspi_init_source,mspi_init_object),(type0_offset_source,type0_offset_object),(type0_configure_source,type0_configure_object),(type1_sn_source,type1_sn_object),(type1_write_source,type1_write_object),(type1_bank_source,type1_bank_object),(type1_register_source,type1_register_object),(type1_chip_id_source,type1_chip_id_object),(type1_frame_lower_source,type1_frame_lower_object),(irq_context_source,irq_context_object),(scheduler_source,scheduler_object),(setup_source,setup_object),(enable_source,enable_object),(pin_source,pin_object),(pre_source,pre_object),(power_source,power_object),(pmic_source,pmic_object),(transport_source,transport_object),(type0_pre_source,type0_pre_object),(mode4_source,mode4_object),(ldo_find_source,ldo_find_object),(ldo_helpers_source,ldo_helpers_object),(frame_source,frame_object),(finish_source,finish_object),(buck_source,buck_object),(bus_source,bus_object),(type0_finish_source,type0_finish_object),(mode4_finish_source,mode4_finish_object),(get_source,get_object),(read_source,read_object),(packet_source,packet_object),(encode_source,encode_object),(validate_source,validate_object),(begin_source,begin_object),(check_source,check_object),(end_source,end_object),(aux_source,aux_object),(complete_source,complete_object),(status_source,status_object),(regwrite_source,regwrite_object),(packetwrite_source,packetwrite_object),(recover_source,recover_object),(context_source,context_object),(snapshot_source,snapshot_object),(aux_config_source,aux_config_object),(command_lower_source,command_lower_object),(frame_lower_source,frame_lower_object),(delay_source,delay_object),(qspi_source,qspi_object),(modes_source,modes_object),(reconfigure_source,reconfigure_object),(mspi_power_source,mspi_power_object),(lifecycle_source,lifecycle_object),(stop_source,stop_object),(prepare_stop_source,prepare_stop_object),(pin_mode_source,pin_mode_object),(pin_apply_source,pin_apply_object),(transfer_setup_source,transfer_setup_object),(interrupt_source,interrupt_object),(cache_source,cache_object)):
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-c',str(source),'-o',str(obj)],check=True)
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-c',str(leaf_source),'-o',str(leaf_object)],check=True)
assert sha(selected)==selected_link['output_sha256']
assert sha(display_object)==display_audit['combined_sha256']
assert sha(option_object)==option_audit['combined_sha256']
groups={'selected':set(selected_link['defined_symbols']),
        'display':set(display_audit['defined']),
        'option_service':set(option_audit['defined']),
        'leaf':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(leaf_object)],text=True).splitlines()},
        'setup':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(setup_object)],text=True).splitlines()},
        'enable':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(enable_object)],text=True).splitlines()},
        'pin_prepare':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(pin_object)],text=True).splitlines()},
        'type1_pre':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(pre_object)],text=True).splitlines()},
        'type1_power':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(power_object)],text=True).splitlines()},
        'pmic_helpers':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(pmic_object)],text=True).splitlines()},
        'pmic_transport':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(transport_object)],text=True).splitlines()},
        'type0_pre':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(type0_pre_object)],text=True).splitlines()},
        'mode4':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(mode4_object)],text=True).splitlines()},
        'ldo_find':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(ldo_find_object)],text=True).splitlines()},
        'ldo_helpers':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(ldo_helpers_object)],text=True).splitlines()},
        'frame_start':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(frame_object)],text=True).splitlines()},
        'type1_finish':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(finish_object)],text=True).splitlines()},
        'buck0_enable':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(buck_object)],text=True).splitlines()},
        'flash_bus':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(bus_object)],text=True).splitlines()},
        'type0_finish':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(type0_finish_object)],text=True).splitlines()},
        'mode4_finish':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(mode4_finish_object)],text=True).splitlines()},
        'type0_get':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(get_object)],text=True).splitlines()},
        'type0_read':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(read_object)],text=True).splitlines()},
        'type0_packet':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(packet_object)],text=True).splitlines()},
        'packet_encode':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(encode_object)],text=True).splitlines()},
        'packet_validate':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(validate_object)],text=True).splitlines()},
        'packet_begin':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(begin_object)],text=True).splitlines()},
        'device_check':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(check_object)],text=True).splitlines()},
        'packet_end':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(end_object)],text=True).splitlines()},
        'type0_aux_finish':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(aux_object)],text=True).splitlines()},
        'type0_aux_complete':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(complete_object)],text=True).splitlines()},
        'type0_aux_status':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(status_object)],text=True).splitlines()},
        'type0_aux_reg_write':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(regwrite_object)],text=True).splitlines()},
        'type0_packet_write':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(packetwrite_object)],text=True).splitlines()},
        'type0_aux_recover':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(recover_object)],text=True).splitlines()},
        'type0_context':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(context_object)],text=True).splitlines()},
        'type0_snapshot':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(snapshot_object)],text=True).splitlines()},
        'type0_aux_config':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(aux_config_object)],text=True).splitlines()},
        'type0_command_lower':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(command_lower_object)],text=True).splitlines()},
        'type0_frame_lower':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(frame_lower_object)],text=True).splitlines()},
        'type0_delay':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(delay_object)],text=True).splitlines()},
        'type0_qspi_write':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(qspi_object)],text=True).splitlines()},
        'type0_mspi_modes':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(modes_object)],text=True).splitlines()},
        'type0_device_reconfigure':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(reconfigure_object)],text=True).splitlines()},
        'type0_mspi_power':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(mspi_power_object)],text=True).splitlines()},
        'type0_mspi_lifecycle':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(lifecycle_object)],text=True).splitlines()},
        'type0_transfer_stop':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(stop_object)],text=True).splitlines()},
        'type0_prepare_stop':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(prepare_stop_object)],text=True).splitlines()},
        'type0_pin_mode':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(pin_mode_object)],text=True).splitlines()},
        'type0_pin_apply':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(pin_apply_object)],text=True).splitlines()},
        'type0_transfer_setup':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(transfer_setup_object)],text=True).splitlines()},
        'type0_mspi_interrupt':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(interrupt_object)],text=True).splitlines()},
        'irq_context':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(irq_context_object)],text=True).splitlines()},
        'scheduler_state':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(scheduler_object)],text=True).splitlines()},
        'type1_frame_lower':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(type1_frame_lower_object)],text=True).splitlines()},
        'type1_chip_id':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(type1_chip_id_object)],text=True).splitlines()},
        'type1_bank':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(type1_bank_object)],text=True).splitlines()},
        'type1_register':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(type1_register_object)],text=True).splitlines()},
        'type1_sn':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(type1_sn_object)],text=True).splitlines()},
        'type1_write':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(type1_write_object)],text=True).splitlines()},
        'type0_configure':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(type0_configure_object)],text=True).splitlines()},
        'type0_offset':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(type0_offset_object)],text=True).splitlines()},
        'mspi_init':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(mspi_init_object)],text=True).splitlines()},
        'type0_cache_prepare':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(cache_object)],text=True).splitlines()}}
overlap={f'{a}/{b}':sorted(groups[a]&groups[b]) for i,a in enumerate(groups) for b in list(groups)[i+1:]}
assert all(not x for x in overlap.values()),overlap
candidate=out/'candidate.o'
subprocess.run(['arm-none-eabi-ld','-r',str(selected),str(display_object),
                str(option_object),str(leaf_object),str(setup_object),str(enable_object),str(pin_object),str(pre_object),str(power_object),str(pmic_object),str(transport_object),str(type0_pre_object),str(mode4_object),str(ldo_find_object),str(ldo_helpers_object),str(frame_object),str(finish_object),str(buck_object),str(bus_object),str(type0_finish_object),str(mode4_finish_object),str(get_object),str(read_object),str(packet_object),str(encode_object),str(validate_object),str(begin_object),str(check_object),str(end_object),str(aux_object),str(complete_object),str(status_object),str(regwrite_object),str(packetwrite_object),str(recover_object),str(context_object),str(snapshot_object),str(aux_config_object),str(command_lower_object),str(frame_lower_object),str(delay_object),str(qspi_object),str(modes_object),str(reconfigure_object),str(mspi_power_object),str(lifecycle_object),str(stop_object),str(prepare_stop_object),str(pin_mode_object),str(pin_apply_object),str(transfer_setup_object),str(interrupt_object),str(cache_object),str(irq_context_object),str(scheduler_object),str(type1_frame_lower_object),str(type1_chip_id_object),str(type1_bank_object),str(type1_register_object),str(type1_sn_object),str(type1_write_object),str(type0_configure_object),str(type0_offset_object),str(mspi_init_object),'-o',str(candidate)],check=True)
undefined=sorted({line.split()[-1] for line in subprocess.check_output(
    ['arm-none-eabi-nm','-u',str(candidate)],text=True).splitlines()})
assert len(undefined)>=617,len(undefined)
relocations=subprocess.check_output(['arm-none-eabi-readelf','-r',
                                     str(display/'display_driver_uled_options_relocated_fifteen.o')],
                                    text=True)
assert 'contains 15 entries' in relocations,relocations
assert relocations.count('R_ARM_ABS32')==15,relocations
audit={'status':'candidate relocatable link with fifteen source-owned uLED option callback entries',
       'selected_round':604,'selected_object_sha256':sha(selected),
       'display_object_sha256':sha(display_object),
       'option_service_object_sha256':sha(option_object),
       'integrated_object_sha256':sha(candidate),
       'acquire_alias':'audio_semaphore_acquire at native 0x44994e',
       'delay_alias':'audio_uart_task_delay at native 0x454b4c',
       'semaphore_alias':'audio_uart_sync_sem_new at native 0x44989a',
       'mspi_init_source_sha256':sha(mspi_init_source),
       'mspi_init_object_sha256':sha(mspi_init_object),
       'type0_offset_source_sha256':sha(type0_offset_source),
       'type0_offset_object_sha256':sha(type0_offset_object),
       'type0_configure_source_sha256':sha(type0_configure_source),
       'type0_configure_object_sha256':sha(type0_configure_object),
       'type1_sn_source_sha256':sha(type1_sn_source),
       'type1_write_source_sha256':sha(type1_write_source),
       'type1_sn_object_sha256':sha(type1_sn_object),
       'type1_write_object_sha256':sha(type1_write_object),
       'type1_bank_source_sha256':sha(type1_bank_source),
       'type1_register_source_sha256':sha(type1_register_source),
       'type1_bank_object_sha256':sha(type1_bank_object),
       'type1_register_object_sha256':sha(type1_register_object),
       'type1_chip_id_source_sha256':sha(type1_chip_id_source),
       'type1_chip_id_object_sha256':sha(type1_chip_id_object),
       'type1_frame_lower_source_sha256':sha(type1_frame_lower_source),
       'type1_frame_lower_object_sha256':sha(type1_frame_lower_object),
       'irq_context_source_sha256':sha(irq_context_source),
       'scheduler_source_sha256':sha(scheduler_source),
       'irq_context_object_sha256':sha(irq_context_object),
       'scheduler_object_sha256':sha(scheduler_object),
       'command_lower_source_sha256':sha(command_lower_source),
       'writer_alias':'display_driver_uled_type0_packet_write_59ccdc',
       'validator_alias':'display_driver_uled_packet_validate_59cb42',
       'qspi_source_sha256':sha(qspi_source),
       'provider_alias_source_sha256':{p.name:sha(p) for p in (enable_source,reconfigure_source,mspi_power_source,modes_source)},
       'duplicate_definitions':overlap,
       'unresolved_symbols':undefined,'integrated_unresolved_after':len(undefined),
       'option_callback_unique_total':29,
       'option_callback_C_bodies':15,
       'option_callback_relocation_entries':15,
       'option_callback_native_addresses_remaining':14,
       'leaf_object_sha256':sha(leaf_object),
       'setup_object_sha256':sha(setup_object),
       'enable_object_sha256':sha(enable_object),
       'pin_prepare_object_sha256':sha(pin_object),
       'type1_pre_object_sha256':sha(pre_object),
       'type1_power_object_sha256':sha(power_object),
       'pmic_helpers_object_sha256':sha(pmic_object),
       'pmic_transport_object_sha256':sha(transport_object),
       'type0_pre_object_sha256':sha(type0_pre_object),
       'mode4_object_sha256':sha(mode4_object),
       'ldo_find_object_sha256':sha(ldo_find_object),
       'ldo_helpers_object_sha256':sha(ldo_helpers_object),
       'frame_start_object_sha256':sha(frame_object),
       'type1_finish_object_sha256':sha(finish_object),
       'buck0_enable_object_sha256':sha(buck_object),
       'flash_bus_object_sha256':sha(bus_object),
       'type0_finish_object_sha256':sha(type0_finish_object),
       'mode4_finish_object_sha256':sha(mode4_finish_object),
       'type0_get_object_sha256':sha(get_object),
       'type0_read_object_sha256':sha(read_object),
       'type0_packet_object_sha256':sha(packet_object),
       'packet_encode_object_sha256':sha(encode_object),
       'packet_validate_object_sha256':sha(validate_object),
       'packet_begin_object_sha256':sha(begin_object),
       'device_check_object_sha256':sha(check_object),
       'packet_end_object_sha256':sha(end_object),
       'type0_aux_finish_object_sha256':sha(aux_object),
       'type0_aux_complete_object_sha256':sha(complete_object),
       'type0_aux_status_object_sha256':sha(status_object),
       'type0_aux_reg_write_object_sha256':sha(regwrite_object),
       'type0_packet_write_object_sha256':sha(packetwrite_object),
       'type0_aux_recover_object_sha256':sha(recover_object),
       'type0_context_object_sha256':sha(context_object),
       'type0_snapshot_object_sha256':sha(snapshot_object),
       'type0_aux_config_object_sha256':sha(aux_config_object),
       'type0_command_lower_object_sha256':sha(command_lower_object),
       'type0_frame_lower_object_sha256':sha(frame_lower_object),
       'type0_delay_object_sha256':sha(delay_object),
       'type0_qspi_write_object_sha256':sha(qspi_object),
       'type0_mspi_modes_object_sha256':sha(modes_object),
       'type0_device_reconfigure_object_sha256':sha(reconfigure_object),
       'type0_mspi_power_object_sha256':sha(mspi_power_object),
       'type0_mspi_lifecycle_object_sha256':sha(lifecycle_object),
       'type0_transfer_stop_object_sha256':sha(stop_object),
       'type0_prepare_stop_object_sha256':sha(prepare_stop_object),
       'type0_pin_mode_object_sha256':sha(pin_mode_object),
       'type0_pin_apply_object_sha256':sha(pin_apply_object),
       'type0_transfer_setup_object_sha256':sha(transfer_setup_object),
       'type0_mspi_interrupt_object_sha256':sha(interrupt_object),
       'type0_cache_prepare_object_sha256':sha(cache_object),
       'source_complete':False,'whole_image_linked':False}
(out/'link-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
print('PASS_ULED_OPTION_FIFTEEN_CACHE_PREPARE_APOLLO_INTEGRATION',len(undefined),15,14)
