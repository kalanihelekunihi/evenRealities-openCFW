
undefined8 FUN_00551240(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar1 = FUN_00550086(*DAT_00551ea0 & 0xff);
  if ((iVar1 != 0) && (*(char *)(iVar1 + 10) != '\0')) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_1 = 0x58e;
      param_2 = DAT_00551ea4;
      FUN_0043d574(3,DAT_005514b8,DAT_0055148c,DAT_00551ea8,0x58e,DAT_00551ea4,
                   *(undefined1 *)(iVar1 + 8),param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_00551eac,DAT_00551eac,*(undefined1 *)(iVar1 + 8));
    }
    FUN_005512b0(*(undefined4 *)(iVar1 + 4));
  }
  return CONCAT44(param_2,param_1);
}

