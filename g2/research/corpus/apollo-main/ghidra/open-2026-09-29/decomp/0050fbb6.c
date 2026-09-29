
undefined8 FUN_0050fbb6(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char *pcVar1;
  int iVar2;
  int iVar3;
  undefined4 local_18;
  undefined4 local_14;
  
  pcVar1 = DAT_0050fe7c;
  local_18 = param_3;
  local_14 = param_4;
  if (*DAT_0050fe7c != '\0') {
    for (iVar3 = 0; iVar2 = DAT_0050fe9c, iVar3 < 4; iVar3 = iVar3 + 1) {
      if (*(int *)(DAT_0050fe9c + iVar3 * 4) != 0) {
        FUN_00463e1c(*(undefined4 *)(DAT_0050fe9c + iVar3 * 4),0);
        *(undefined4 *)(iVar2 + iVar3 * 4) = 0;
      }
    }
    FUN_0043c0e4(DAT_0050fe94,0x30,0);
    *DAT_0050fe80 = 0;
    *pcVar1 = '\0';
    *DAT_0050feac = 0;
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      local_14 = DAT_0050fecc;
      local_18 = 0xee;
      FUN_0043d574(3,DAT_0050febc,DAT_0050feb8,DAT_0050fed0);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_0050fed4,DAT_0050fed4);
    }
  }
  return CONCAT44(local_14,local_18);
}

