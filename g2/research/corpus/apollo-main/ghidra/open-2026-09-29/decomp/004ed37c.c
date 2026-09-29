
undefined8 FUN_004ed37c(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  undefined4 local_18;
  undefined4 local_14;
  
  piVar1 = DAT_004ed748;
  local_18 = param_3;
  local_14 = param_4;
  if (*DAT_004ed748 == 0) {
    *DAT_004ed730 = 0;
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      local_14 = DAT_004ed758;
      local_18 = 0x780;
      FUN_0043d574(4,DAT_004ed6e4,DAT_004ed728,DAT_004ed75c);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004ed760);
    }
  }
  else {
    *DAT_004ed730 = 1;
    for (iVar3 = 0; iVar2 = DAT_004ed754, iVar3 < *piVar1; iVar3 = iVar3 + 1) {
      if (*(int *)(DAT_004ed754 + iVar3 * 4) != 0) {
        iVar4 = FUN_004ebf20();
        if (iVar3 == iVar4) {
          uVar5 = FUN_0044104c(0xffffff);
          FUN_0044127e(*(undefined4 *)(iVar2 + iVar3 * 4),uVar5,0);
          FUN_0044129e(*(undefined4 *)(iVar2 + iVar3 * 4),0xff,0);
        }
        else {
          uVar5 = FUN_0044104c(DAT_004ed6c0);
          FUN_0044127e(*(undefined4 *)(iVar2 + iVar3 * 4),uVar5,0);
          FUN_0044129e(*(undefined4 *)(iVar2 + iVar3 * 4),0x96,0);
        }
      }
    }
  }
  return CONCAT44(local_14,local_18);
}

