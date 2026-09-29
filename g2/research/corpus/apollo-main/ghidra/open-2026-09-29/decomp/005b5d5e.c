
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
conversate_ui_action_menu_page_scroll_down(int param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  
  if (param_1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_3 = 0x15;
      FUN_0043d574(2,DAT_005b6950,DAT_005b694c,_DAT_005b6948,0x15,_DAT_005b6944);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,_DAT_005b6954,_DAT_005b6954);
    }
    uVar2 = 5;
  }
  else {
    FUN_0043f66c(param_1);
    iVar1 = FUN_0043fdda(param_1);
    uVar3 = (iVar1 + 0x1b) / 0x1c;
    if (uVar3 < 2) {
      uVar2 = 3;
    }
    else if (uVar3 == 2) {
      uVar2 = 5;
    }
    else if (uVar3 == 3) {
      uVar2 = 7;
    }
    else if (uVar3 == 4) {
      uVar2 = 9;
    }
    else {
      uVar2 = 0xb;
    }
  }
  return CONCAT44(param_3,uVar2);
}

