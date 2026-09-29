
undefined8 FUN_0050c6e2(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_10;
  undefined4 local_c;
  
  local_10 = param_3;
  local_c = param_4;
  if (((param_1 != 0) && (*(char *)(param_1 + 0x29) != '\0')) && (*(int *)(param_1 + 4) != 0)) {
    iVar1 = FUN_0043e2ea(*(undefined4 *)(param_1 + 4));
    if (iVar1 == 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_c = DAT_0050ca04;
        local_10 = 0x96e;
        FUN_0043d574(2,DAT_0050c9c8,DAT_0050c9c4,DAT_0050ca08);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_0050ca0c,DAT_0050ca0c);
      }
      *(undefined4 *)(param_1 + 4) = 0;
    }
    else {
      FUN_0044ea04(*(undefined4 *)(param_1 + 4),0,0);
      *(undefined1 *)(param_1 + 0x25) = 1;
      *(undefined1 *)(param_1 + 0x26) = 0;
      FUN_0050b5f4(param_1);
    }
  }
  return CONCAT44(local_c,local_10);
}

