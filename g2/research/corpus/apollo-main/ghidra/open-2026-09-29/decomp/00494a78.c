
undefined8 FUN_00494a78(byte param_1,int param_2,undefined *param_3,uint param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 uVar3;
  int iVar4;
  
  iVar4 = param_2;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_4 = (uint)param_1;
    iVar4 = 0x31e;
    param_3 = PTR_s_common_text_event_callback__is_t_004954d8;
    FUN_0043d574(4,PTR_s_evenhub_ui_00494b84,DAT_00494b80,PTR_s_common_text_event_callback_004954dc,
                 0x31e,PTR_s_common_text_event_callback__is_t_004954d8,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_00494ac8;
  }
  compress_log_output(0x10400000,PTR_s__evenhub_ui_common_text_event_ca_004954e0,
                      PTR_s__evenhub_ui_common_text_event_ca_004954e0,param_1,iVar4,param_3,param_4)
  ;
LAB_00494ac8:
  if (param_2 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      iVar4 = 0x321;
      FUN_0043d574(1,PTR_s_evenhub_ui_00494b84,DAT_00494b80,
                   PTR_s_common_text_event_callback_004954dc,0x321,
                   PTR_s_common_text_event_callback__mana_004954e4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__evenhub_ui_common_text_event_ca_004954e8,
                          PTR_s__evenhub_ui_common_text_event_ca_004954e8);
    }
    uVar2 = 0xffffffff;
  }
  else {
    if (param_1 == 0) {
      uVar3 = 2;
    }
    else {
      uVar3 = 1;
    }
    iVar4 = 0;
    FUN_004da16a(2,*(undefined4 *)(param_2 + 0x1c),param_2 + 0x20,uVar3,0,0);
    uVar2 = 0;
  }
  return CONCAT44(iVar4,uVar2);
}

