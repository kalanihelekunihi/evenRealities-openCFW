
undefined8 FUN_005e4920(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_10;
  undefined4 local_c;
  
  iVar1 = DAT_005e53b4;
  local_10 = param_3;
  local_c = param_4;
  if ((((*(int *)(DAT_005e53b4 + 0x1cc) != 0) && (*(int *)(DAT_005e53b4 + 0x1d0) != 0)) &&
      (*(int *)(DAT_005e53b4 + 0x1d4) != 0)) && (*(int *)(DAT_005e53b4 + 0x1dc) != 0)) {
    FUN_0043dfa4(*(undefined4 *)(DAT_005e53b4 + 0x1cc),1);
    FUN_005ea30c();
    FUN_005e4878(*(undefined4 *)(iVar1 + 0x1d0));
    FUN_0049942e(*(undefined4 *)(iVar1 + 0x1d4),&LAB_005e4b64);
    FUN_005e4902();
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_c = DAT_005e5474;
      local_10 = 0xae;
      FUN_0043d574(4,DAT_005e5480,DAT_005e547c,DAT_005e5478);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_005e5554,DAT_005e5554);
    }
  }
  return CONCAT44(local_c,local_10);
}

