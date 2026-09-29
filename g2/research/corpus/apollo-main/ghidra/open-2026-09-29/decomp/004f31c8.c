
undefined8 FUN_004f31c8(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 local_10;
  undefined4 local_c;
  
  local_10 = param_3;
  local_c = param_4;
  if ((((*DAT_004f33c0 == 1) && (*DAT_004f33b4 == 1)) ||
      ((*DAT_004f33c0 == 1 && (*DAT_004f3418 == 1)))) || (*DAT_004f33c0 == 1)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_c = DAT_004f341c;
      local_10 = 0x6a0;
      FUN_0043d574(3,DAT_004f33ec,DAT_004f33e8,DAT_004f3420);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_004f3424,DAT_004f3424);
    }
    puVar1 = DAT_004f3428;
    iVar2 = FUN_0043e2ea(*DAT_004f3428);
    if (iVar2 != 0) {
      FUN_0044d878(*puVar1);
      FUN_004f4670(*puVar1);
    }
  }
  if (*DAT_004f342c == 1) {
    FUN_004efffc();
  }
  return CONCAT44(local_c,local_10);
}

