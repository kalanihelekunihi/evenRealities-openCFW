
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_00555c04(char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  
  iVar2 = _DAT_00556260;
  iVar1 = DAT_005560cc;
  FUN_0043dfa4(*(undefined4 *)(_DAT_00556260 + 0x10),1);
  *(undefined4 *)(iVar2 + 0x38) = 0x7fff;
  uVar4 = *(uint *)(iVar1 + 0xc);
  iVar3 = *(int *)(iVar1 + 4);
  if (uVar4 < 5) {
    *(undefined4 *)(iVar2 + 0x2c) = 0;
  }
  else {
    if (iVar3 == 0) {
      iVar5 = 0;
    }
    else {
      iVar5 = iVar3 + -1;
    }
    *(int *)(iVar2 + 0x2c) = iVar5;
    if (uVar4 < *(int *)(iVar2 + 0x2c) + 4U) {
      *(uint *)(iVar2 + 0x2c) = uVar4 - 4;
    }
  }
  *(int *)(iVar2 + 0x30) = iVar3;
  *(undefined4 *)(iVar2 + 0x34) = *(undefined4 *)(iVar1 + 8);
  teleprompt_page_data_set_window(*(undefined4 *)(iVar2 + 0x2c));
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(3,PTR_s_teleprompt_ui_0055648c,PTR_s_D__01_workspace_s200_ap510b_iar__00556488,
                 PTR_s_teleprompt_ui_action_display_mai_00556668,0x55e,
                 PTR_s_window_start_page_id____d__curre_00556664,*(undefined4 *)(iVar2 + 0x2c),
                 *(undefined4 *)(iVar2 + 0x30),*(undefined4 *)(iVar2 + 0x34),param_4);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0xcc00000,PTR_s__teleprompt_ui_window_start_page_0055666c,
                        PTR_s__teleprompt_ui_window_start_page_0055666c,
                        *(undefined4 *)(iVar2 + 0x2c),*(undefined4 *)(iVar2 + 0x30),
                        *(undefined4 *)(iVar2 + 0x34));
  }
  FUN_0055553c(iVar2,*(undefined4 *)(iVar2 + 0x2c));
  uVar4 = *(int *)(iVar2 + 0x30) - *(int *)(iVar2 + 0x2c);
  if (3 < uVar4) {
    uVar4 = 3;
  }
  FUN_0044ea04(*(undefined4 *)(iVar2 + 0x18),uVar4 * 0x118 + *(int *)(iVar1 + 8) * 0x1c,0);
  if (param_1 == '\x02') {
    FUN_0058c238(*_DAT_0055627c,0xfa,0);
  }
  return 0;
}

