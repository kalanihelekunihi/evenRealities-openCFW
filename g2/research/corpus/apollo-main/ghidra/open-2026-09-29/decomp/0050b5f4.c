
undefined8 FUN_0050b5f4(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 local_18;
  undefined4 local_14;
  
  local_18 = param_3;
  local_14 = param_4;
  if ((param_1 != 0) && (*(int *)(param_1 + 4) != 0)) {
    iVar1 = FUN_0043e2ea(*(undefined4 *)(param_1 + 4));
    if (iVar1 == 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_14 = DAT_0050c140;
        local_18 = 0x570;
        FUN_0043d574(2,DAT_0050b740,DAT_0050b73c,DAT_0050c144);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_0050c148,DAT_0050c148);
      }
      *(undefined4 *)(param_1 + 4) = 0;
    }
    else {
      iVar1 = FUN_0044dca2(*(undefined4 *)(param_1 + 4));
      if ((iVar1 == 0) || (iVar1 = FUN_0043e2ea(), iVar1 != 0)) {
        FUN_0043f66c(*(undefined4 *)(param_1 + 4));
        iVar1 = FUN_0044e4aa(*(undefined4 *)(param_1 + 4));
        iVar2 = FUN_0044e4bc(*(undefined4 *)(param_1 + 4));
        iVar3 = FUN_0043fdda(*(undefined4 *)(param_1 + 4));
        *(bool *)(param_1 + 0x24) = iVar3 < iVar2 + iVar1 + iVar3;
        if (*(char *)(param_1 + 0x24) == '\0') {
          FUN_0044e368(*(undefined4 *)(param_1 + 4),0);
          *(undefined1 *)(param_1 + 0x25) = 1;
          *(undefined1 *)(param_1 + 0x26) = 1;
        }
        else {
          iVar1 = FUN_0044e498(*(undefined4 *)(param_1 + 4));
          *(bool *)(param_1 + 0x25) = iVar1 < 3;
          *(bool *)(param_1 + 0x26) = iVar2 < 3;
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          local_14 = DAT_0050c14c;
          local_18 = 0x579;
          FUN_0043d574(2,DAT_0050b740,DAT_0050b73c,DAT_0050c144);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_0050c2f0);
        }
      }
    }
  }
  return CONCAT44(local_14,local_18);
}

