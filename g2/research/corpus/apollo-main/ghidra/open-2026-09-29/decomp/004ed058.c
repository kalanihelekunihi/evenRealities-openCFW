
undefined8 FUN_004ed058(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  if (param_1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_2 = 0x708;
      param_3 = DAT_004ed720;
      FUN_0043d574(1,DAT_004ed6e4,DAT_004ed728,DAT_004ed724,0x708,DAT_004ed720,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004ed72c);
    }
  }
  else {
    iVar1 = FUN_004ecfc8(param_2);
    if (*(int *)(param_1 + 0x4c) != 0) {
      if (iVar1 < 2) {
        FUN_0043ded4(*(undefined4 *)(param_1 + 0x4c),1);
      }
      else {
        FUN_0043dfa4(*(undefined4 *)(param_1 + 0x4c),1);
      }
    }
    if (*(int *)(param_1 + 0x50) != 0) {
      if (iVar1 < 3) {
        FUN_0043ded4(*(undefined4 *)(param_1 + 0x50),1);
      }
      else {
        FUN_0043dfa4(*(undefined4 *)(param_1 + 0x50),1);
      }
    }
  }
  return CONCAT44(param_3,param_2);
}

