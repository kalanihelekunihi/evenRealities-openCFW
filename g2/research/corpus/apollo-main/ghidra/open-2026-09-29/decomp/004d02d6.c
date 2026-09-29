
undefined4 FUN_004d02d6(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  int iVar2;
  
  iVar1 = FUN_004cfddc(param_2);
  if (iVar1 != 0) {
    iVar1 = FUN_004cfe1e(param_2);
    if (iVar1 == 0) {
      FUN_004d09b4(DAT_004d0968,DAT_004d06ac,0x2ad);
    }
    iVar2 = FUN_004cfdb4(iVar1);
    if (iVar2 == 0) {
      FUN_004d09b4(DAT_004d096c,DAT_004d06ac,0x2ae);
    }
    FUN_004d0178(param_1,iVar1);
    param_2 = FUN_004d0294(iVar1,param_2);
  }
  return param_2;
}

