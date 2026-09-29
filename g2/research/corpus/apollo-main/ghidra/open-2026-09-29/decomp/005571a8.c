
void FUN_005571a8(char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 uStack_78;
  undefined *puStack_74;
  undefined *puStack_68;
  undefined *puStack_58;
  undefined4 uStack_48;
  undefined4 uStack_18;
  
  iVar1 = DAT_005573fc;
  uStack_18 = param_4;
  if (*(int *)(DAT_005573fc + 0x18) == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      puStack_74 = PTR_s_collapse_animate_skip__scroll_co_00557474;
      uStack_78 = 0x869;
      FUN_0043d574(2,PTR_s_teleprompt_ui_00557448,PTR_s_D__01_workspace_s200_ap510b_iar__00557444,
                   PTR_s_teleprompt_ui_collapse_animate_00557478);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__teleprompt_ui_collapse_animate_s_0055747c,
                          PTR_s__teleprompt_ui_collapse_animate_s_0055747c);
    }
  }
  else {
    iVar2 = func_0x005540f0();
    iVar2 = iVar2 * 0x1c;
    if (param_1 == '\0') {
      iVar3 = iVar2;
      iVar2 = 0;
    }
    else {
      iVar3 = 0;
    }
    *(undefined1 *)(iVar1 + 0x21) = 1;
    FUN_004503d6(&uStack_78);
    uStack_78 = *(undefined4 *)(iVar1 + 0x18);
    uStack_48 = 300;
    puStack_58 = PTR_FUN_00450634_1_00557480;
    puStack_74 = PTR_FUN_00557104_1_00557484;
    puStack_68 = PTR_FUN_0055718c_1_00557488;
    FUN_004506ce(&uStack_78,iVar2,iVar3);
    FUN_00450408(&uStack_78);
  }
  return;
}

