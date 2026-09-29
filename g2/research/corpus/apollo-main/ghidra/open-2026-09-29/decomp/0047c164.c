
undefined8 FUN_0047c164(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_1 = 0x82b;
    param_2 = DAT_0047cae8;
    FUN_0043d574(4,DAT_0047c548,DAT_0047c544,DAT_0047caec,0x82b,DAT_0047cae8,param_3,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_0047caf0);
  }
  piVar1 = DAT_0047c558;
  *DAT_0047c558 = 0;
  iVar2 = DAT_0047caf4;
  for (iVar4 = 0; iVar4 < 10; iVar4 = iVar4 + 1) {
    if ((*(char *)(iVar2 + 0x2f) != '\0') && (*(char *)(iVar2 + 0x30) != '\0')) {
      *piVar1 = *piVar1 + 1;
      *(int *)(iVar2 + 0xc4) = *piVar1;
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        param_1 = 0x835;
        param_2 = DAT_0047caf8;
        FUN_0043d574(4,DAT_0047c548,DAT_0047c544,DAT_0047caec,0x835,DAT_0047caf8,iVar4,
                     *(undefined4 *)(iVar2 + 0xc4));
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        param_1 = *(undefined4 *)(iVar2 + 0xc4);
        compress_log_output(0x10800000,DAT_0047cafc,DAT_0047cafc,iVar4);
      }
      FUN_00479b74(iVar2);
    }
    iVar2 = iVar2 + 200;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_1 = 0x83e;
    param_2 = DAT_0047cb00;
    FUN_0043d574(4,DAT_0047c548,DAT_0047c544,DAT_0047caec);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_0047cb04,DAT_0047cb04);
  }
  return CONCAT44(param_2,param_1);
}

