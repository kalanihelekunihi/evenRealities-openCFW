
undefined4
CALLBACK_MGR_Init(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  if (param_1 == (undefined4 *)0x0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00510554,DAT_00510550,DAT_00510560,0x2f,DAT_0051055c,param_3,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00510564);
    }
    uVar2 = 0;
  }
  else {
    *param_1 = 0;
    *(undefined1 *)(param_1 + 1) = 0;
    param_1[2] = param_2;
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00510554,DAT_00510550,DAT_00510560,0x37,DAT_00510568,param_1[2]);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__callback_mgr___s__Callback_mana_0051056c,
                          PTR_s__callback_mgr___s__Callback_mana_0051056c,param_1[2]);
    }
    uVar2 = 1;
  }
  return uVar2;
}

