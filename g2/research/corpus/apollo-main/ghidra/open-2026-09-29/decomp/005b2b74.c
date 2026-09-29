
undefined8 FUN_005b2b74(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  
  iVar2 = DAT_005b2d38;
  iVar1 = 0;
  if (*(int *)(DAT_005b2d38 + 100) != 0) {
    iVar1 = FUN_0044dce2(*(undefined4 *)(DAT_005b2d38 + 100),0);
  }
  if (*(int *)(iVar2 + 0x7c) == 0) {
    if (*(char *)(iVar2 + 0x8c) == '\0') {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_3 = 0x113;
        FUN_0043d574(2,DAT_005b2d30,DAT_005b2d2c,PTR_s_conversate_ui_action_main_page_s_005b34fc,
                     0x113,DAT_005b32a4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_005b32a8,DAT_005b32a8);
      }
      uVar4 = 0xffffffff;
      goto LAB_005b2c66;
    }
    uVar4 = 0;
    iVar3 = iVar1;
  }
  else {
    uVar4 = 0xffffffff;
    iVar3 = *(int *)(iVar2 + 0x7c);
  }
  if (iVar3 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_3 = 0x11b;
      FUN_0043d574(2,DAT_005b2d30,DAT_005b2d2c,PTR_s_conversate_ui_action_main_page_s_005b34fc,0x11b
                   ,PTR_s_Main_selected_skipped__no_valid_s_005b3500);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__conversate_ui_Main_selected_ski_005b3504);
    }
    uVar4 = 0xffffffff;
  }
  else {
    if (iVar1 != 0) {
      FUN_0044ea2e(iVar1,0);
    }
    FUN_0058c622(iVar3,0xfa,0);
    *(int *)(iVar2 + 0x80) = iVar3;
    *(undefined4 *)(iVar2 + 0x84) = uVar4;
    *(undefined1 *)(iVar2 + 0x96) = 1;
    FUN_005b0edc(2,1,PTR_s_main_selected_005b3508);
    uVar4 = 0;
  }
LAB_005b2c66:
  return CONCAT44(param_3,uVar4);
}

