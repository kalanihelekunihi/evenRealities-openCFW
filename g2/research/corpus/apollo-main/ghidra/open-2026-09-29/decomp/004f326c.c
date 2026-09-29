
undefined8 FUN_004f326c(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int *piVar2;
  undefined4 *puVar3;
  int iVar4;
  
  piVar1 = DAT_004f33c0;
  if ((((*DAT_004f33c0 == 1) && (*DAT_004f33b4 == 1)) ||
      ((*DAT_004f33c0 == 1 && (*DAT_004f3418 == 1)))) || (*DAT_004f33c0 == 1)) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      param_2 = 0x6af;
      param_3 = DAT_004f341c;
      FUN_0043d574(3,DAT_004f33ec,DAT_004f33e8,DAT_004f3430);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_004f3424,DAT_004f3424);
    }
    puVar3 = DAT_004f3428;
    iVar4 = FUN_0043e2ea(*DAT_004f3428);
    if (iVar4 != 0) {
      FUN_0044d878(*puVar3);
      FUN_004f4670(*puVar3);
    }
  }
  if (*DAT_004f342c == 1) {
    FUN_004efffc();
  }
  piVar2 = DAT_004f3418;
  if (*piVar1 == 1) {
    if (*DAT_004f3418 == 1) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        param_2 = 0x6bb;
        param_3 = DAT_004f3434;
        FUN_0043d574(3,DAT_004f33ec,DAT_004f33e8,DAT_004f3430,0x6bb,DAT_004f3434,param_4);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_004f3438);
      }
      puVar3 = DAT_004f343c;
      iVar4 = FUN_0043e2ea(*DAT_004f343c);
      if (iVar4 != 0) {
        FUN_0044d878(*puVar3);
        *piVar2 = 0;
        *DAT_004f3384 = 0;
        *DAT_004f3f70 = 0;
      }
    }
  }
  return CONCAT44(param_3,param_2);
}

