
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00511342(void)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  undefined4 uVar7;
  int iVar8;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined4 uStack_24;
  
  uVar7 = DAT_00511984;
  uVar1 = FUN_0055ef6c(DAT_00511984,0);
  uVar2 = FUN_0055eff0(uVar7,0);
  uVar3 = FUN_0055ee8c(uVar7,0);
  uVar4 = FUN_0055f4f2(uVar7,0);
  func_0x0055ed9a(uVar7,PTR_FUN_0051124c_1_00511bf4,4);
  iVar5 = FUN_0055edca(uVar7,4,8);
  iVar8 = DAT_00511964;
  if (iVar5 != DAT_00511964) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00511958,DAT_00511954,PTR_s_npmx_application_configure_00511bfc,0x1aa,
                   PTR_s_ERROR__npmx_core_event_interrupt_00511bf8,iVar5);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x4400000,PTR_s__npmx_driver_ERROR__npmx_core_ev_00511c00,
                          PTR_s__npmx_driver_ERROR__npmx_core_ev_00511c00,iVar5);
    }
  }
  uStack_2c = *(undefined4 *)PTR_DAT_00511c04;
  uStack_28 = *(undefined4 *)(PTR_DAT_00511c04 + 4);
  uStack_24 = *(undefined4 *)(PTR_DAT_00511c04 + 8);
  iVar5 = FUN_0055ef80(uVar1,&uStack_2c);
  if (iVar5 != iVar8) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00511958,DAT_00511954,PTR_s_npmx_application_configure_00511bfc,0x1b8,
                   PTR_s_ERROR__npmx_timer_config_set__d_00511c08,iVar5);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x4400000,PTR_s__npmx_driver_ERROR__npmx_timer_c_00511c0c,
                          PTR_s__npmx_driver_ERROR__npmx_timer_c_00511c0c,iVar5);
    }
  }
  func_0x0055ed9a(uVar7,PTR_FUN_00511294_1_00511c10,5);
  iVar5 = FUN_0055edca(uVar7,5,3);
  if (iVar5 != iVar8) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00511958,DAT_00511954,PTR_s_npmx_application_configure_00511bfc,0x1c9,
                   PTR_s_ERROR__npmx_core_event_interrupt_00511bf8,iVar5);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x4400000,PTR_s__npmx_driver_ERROR__npmx_core_ev_00511c00,
                          PTR_s__npmx_driver_ERROR__npmx_core_ev_00511c00,iVar5);
    }
  }
  iVar5 = FUN_0055f134(uVar2,0x60);
  if (iVar5 != iVar8) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00511958,DAT_00511954,PTR_s_npmx_application_configure_00511bfc,0x1cf,
                   PTR_s_ERROR__npmx_charger_charging_cur_00511c14,iVar5);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x4400000,PTR_s__npmx_driver_ERROR__npmx_charger_00511c18,
                          PTR_s__npmx_driver_ERROR__npmx_charger_00511c18,iVar5);
    }
  }
  iVar5 = func_0x0055f1b8(uVar2,1000);
  if (iVar5 != iVar8) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00511958,DAT_00511954,PTR_s_npmx_application_configure_00511bfc,0x1d5,
                   PTR_s_ERROR__npmx_charger_discharging__00511c1c,iVar5);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x4400000,PTR_s__npmx_driver_ERROR__npmx_charger_00511c20,
                          PTR_s__npmx_driver_ERROR__npmx_charger_00511c20,iVar5);
    }
  }
  uVar7 = func_0x0055effa(0x1162);
  iVar5 = func_0x0055f25c(uVar2,uVar7);
  if (iVar5 != iVar8) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00511958,DAT_00511954,PTR_s_npmx_application_configure_00511bfc,0x1dc,
                   PTR_s_ERROR__npmx_charger_termination__00511fd8,iVar5);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x4400000,PTR_s__npmx_driver_ERROR__npmx_charger_00511fdc,
                          PTR_s__npmx_driver_ERROR__npmx_charger_00511fdc,iVar5);
    }
  }
  uVar7 = func_0x0055effa(4000);
  iVar5 = func_0x0055f278(uVar2,uVar7);
  if (iVar5 != iVar8) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00511958,DAT_00511954,PTR_s_npmx_application_configure_00511bfc,0x1e3,
                   PTR_s_ERROR__npmx_charger_termination__00511fe0,iVar5);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x4400000,PTR_s__npmx_driver_ERROR__npmx_charger_00511fe4,
                          PTR_s__npmx_driver_ERROR__npmx_charger_00511fe4,iVar5);
    }
  }
  iVar5 = FUN_0055f07a(uVar2,1);
  if (iVar5 != iVar8) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00511958,DAT_00511954,PTR_s_npmx_application_configure_00511bfc,0x1ea,
                   PTR_s_ERROR__npmx_charger_module_enabl_00511fe8,iVar5);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x4400000,PTR_s__npmx_driver_ERROR__npmx_charger_00511fec,
                          PTR_s__npmx_driver_ERROR__npmx_charger_00511fec,iVar5);
    }
  }
  uVar7 = func_0x0055ee96(500);
  iVar5 = func_0x0055ef1e(uVar3,uVar7);
  if (iVar5 != iVar8) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00511958,DAT_00511954,PTR_s_npmx_application_configure_00511bfc,500,
                   PTR_s_ERROR__npmx_vbusin_current_limit_00511ff0,iVar5);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x4400000,PTR_s__npmx_driver_ERROR__npmx_vbusin__00511ff4,
                          PTR_s__npmx_driver_ERROR__npmx_vbusin__00511ff4,iVar5);
    }
  }
  iVar5 = FUN_0055ef02(uVar3,0);
  if (iVar5 != iVar8) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00511958,DAT_00511954,PTR_s_npmx_application_configure_00511bfc,0x1fa,
                   PTR_s_ERROR__npmx_vbusin_task_trigger__00511ff8,iVar5);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x4400000,PTR_s__npmx_driver_ERROR__npmx_vbusin__00511ffc,
                          PTR_s__npmx_driver_ERROR__npmx_vbusin__00511ffc,iVar5);
    }
  }
  uStack_34 = *(undefined4 *)PTR_DAT_00512000;
  uStack_30 = *(undefined4 *)(PTR_DAT_00512000 + 4);
  uStack_34 = func_0x0055f4fe(_DAT_00512004);
  iVar5 = func_0x0055f58a(uVar4,&uStack_34);
  if (iVar5 != iVar8) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00511958,DAT_00511954,PTR_s_npmx_application_configure_00511bfc,0x204,
                   PTR_s_ERROR__npmx_adc_ntc_config_set___00512008,iVar5);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x4400000,PTR_s__npmx_driver_ERROR__npmx_adc_ntc_0051200c,
                          PTR_s__npmx_driver_ERROR__npmx_adc_ntc_0051200c,iVar5);
    }
  }
  iVar5 = FUN_0055f6f0(uVar4,1);
  if (iVar5 != iVar8) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00511958,DAT_00511954,PTR_s_npmx_application_configure_00511bfc,0x20a,
                   PTR_s_ERROR__npmx_adc_ibat_meas_enable_00512010,iVar5);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x4400000,PTR_s__npmx_driver_ERROR__npmx_adc_iba_00512014,
                          PTR_s__npmx_driver_ERROR__npmx_adc_iba_00512014,iVar5);
    }
  }
  iVar5 = FUN_0055f544(uVar4,0);
  if (iVar5 != iVar8) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00511958,DAT_00511954,PTR_s_npmx_application_configure_00511bfc,0x212,
                   DAT_00512018,iVar5);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00512370,DAT_00512370,iVar5);
    }
  }
  iVar5 = FUN_0055f544(uVar4,1);
  if (iVar5 != iVar8) {
    iVar8 = FUN_0043d0ce();
    if (iVar8 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00511958,DAT_00511954,PTR_s_npmx_application_configure_00511bfc,0x216,
                   DAT_00512018,iVar5);
    }
    iVar8 = FUN_0043d0ce();
    if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00512370,DAT_00512370,iVar5);
    }
  }
  return;
}

