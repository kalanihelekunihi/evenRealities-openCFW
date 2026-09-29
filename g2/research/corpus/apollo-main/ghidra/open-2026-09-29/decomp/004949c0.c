
undefined4 FUN_004949c0(int param_1,undefined *param_2,int param_3,undefined *param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined *puVar4;
  
  puVar4 = param_2;
  iVar2 = param_3;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    puVar4 = PTR_s_common_list_event_callback__sele_00494be8;
    iVar2 = param_1;
    param_4 = param_2;
    FUN_0043d574(4,PTR_s_evenhub_ui_00494b84,DAT_00494b80,PTR_s_common_list_event_callback_004954c8,
                 0x312,PTR_s_common_list_event_callback__sele_00494be8,param_1,param_2);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_00494a0e;
  }
  compress_log_output(0x10800000,PTR_s__evenhub_ui_common_list_event_ca_004954cc,
                      PTR_s__evenhub_ui_common_list_event_ca_004954cc,param_1,param_2,puVar4,iVar2,
                      param_4);
LAB_00494a0e:
  if (param_3 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_evenhub_ui_00494b84,DAT_00494b80,
                   PTR_s_common_list_event_callback_004954c8,0x315,
                   PTR_s_common_list_event_callback__mana_004954d0);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__evenhub_ui_common_list_event_ca_004954d4,
                          PTR_s__evenhub_ui_common_list_event_ca_004954d4);
    }
    uVar3 = 0xffffffff;
  }
  else {
    FUN_004da16a(1,*(undefined4 *)(param_3 + 0x1c),param_3 + 0x20,0,param_1,0);
    uVar3 = 0;
  }
  return uVar3;
}

