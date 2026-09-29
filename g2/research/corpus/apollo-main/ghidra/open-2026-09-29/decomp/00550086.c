
undefined8 FUN_00550086(byte param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  
  if (param_1 < 10) {
    for (iVar1 = 0; iVar1 < 10; iVar1 = iVar1 + 1) {
      if ((*(char *)(iVar1 * 0xc + DAT_00550948 + 10) != '\0') &&
         (*(byte *)(iVar1 * 0xc + DAT_00550948 + 8) == param_1)) {
        iVar1 = DAT_00550948 + iVar1 * 0xc;
        goto LAB_00550168;
      }
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_2 = 0x1de;
      FUN_0043d574(2,DAT_00550958,DAT_00550954,DAT_00550b04,0x1de,DAT_00550b0c,param_1);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_00550d30,DAT_00550d30,param_1);
    }
    iVar1 = 0;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_4 = (uint)param_1;
      param_2 = 0x1d5;
      param_3 = DAT_00550964;
      FUN_0043d574(2,DAT_00550958,DAT_00550954,DAT_00550b04,0x1d5,DAT_00550964,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_00550b08,DAT_00550b08,param_1,param_2,param_3,param_4);
    }
    iVar1 = 0;
  }
LAB_00550168:
  return CONCAT44(param_2,iVar1);
}

