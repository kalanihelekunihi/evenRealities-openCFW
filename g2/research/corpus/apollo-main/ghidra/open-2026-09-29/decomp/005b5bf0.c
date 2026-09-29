
undefined8
conversate_ui_menu_event_callback
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  ushort *puVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = DAT_005b5cc8;
  puVar1 = (ushort *)FUN_005b43e8(0);
  if ((puVar1 == (ushort *)0x0) || (*puVar1 == 0)) {
    uVar2 = 0;
  }
  else if (*(int *)(iVar4 + 0x84) < (int)(*puVar1 - 1)) {
    iVar3 = FUN_0044dce2(*(undefined4 *)(iVar4 + 100),*(int *)(iVar4 + 0x84) + 1);
    if (iVar3 == 0) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        param_2 = 0xe8;
        FUN_0043d574(1,DAT_005b5cd8,DAT_005b5cd4,PTR_s_conversate_ui_action_menu_page_s_005b5d1c,
                     0xe8,PTR_s_No_next_button_found_005b5d24,param_4);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__conversate_ui_No_next_button_fo_005b5d28);
      }
      uVar2 = 0xffffffff;
    }
    else {
      FUN_005896fc(*(undefined4 *)(iVar4 + 0x80),iVar3,200);
      *(int *)(iVar4 + 0x80) = iVar3;
      *(int *)(iVar4 + 0x84) = *(int *)(iVar4 + 0x84) + 1;
      uVar2 = 0;
    }
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0xe2;
      FUN_0043d574(4,DAT_005b5cd8,DAT_005b5cd4,PTR_s_conversate_ui_action_menu_page_s_005b5d1c,0xe2,
                   PTR_s_Reached_bottom_button_during_scr_005b5d18,*(undefined4 *)(iVar4 + 0x84));
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__conversate_ui_Reached_bottom_bu_005b5d20,
                          PTR_s__conversate_ui_Reached_bottom_bu_005b5d20,
                          *(undefined4 *)(iVar4 + 0x84));
    }
    uVar2 = 0;
  }
  return CONCAT44(param_2,uVar2);
}

