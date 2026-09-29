
undefined4 FUN_004d033a(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  int iVar2;
  
  iVar1 = FUN_004cfe44(param_2);
  if (iVar1 == 0) {
    FUN_004d09b4(DAT_004d0970,DAT_004d06ac,0x2ba);
  }
  iVar2 = FUN_004cfdb4(iVar1);
  if (iVar2 != 0) {
    iVar2 = FUN_004cfda0(param_2);
    if (iVar2 != 0) {
      FUN_004d09b4(DAT_004d0974,DAT_004d06ac,0x2be);
    }
    FUN_004d0178(param_1,iVar1);
    param_2 = FUN_004d0294(param_2,iVar1);
  }
  return param_2;
}

