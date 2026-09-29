
void FUN_004d03f0(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_004cfdb4(param_2);
  if (iVar1 != 0) {
    FUN_004d09b4(DAT_004d097c,DAT_004d06ac,0x2d6);
  }
  iVar1 = FUN_004d01bc(param_2,param_3);
  if (iVar1 != 0) {
    uVar2 = FUN_004d01d4(param_2,param_3);
    FUN_004cfdf6(uVar2);
    uVar2 = FUN_004d033a(param_1,uVar2);
    FUN_004d019a(param_1,uVar2);
  }
  return;
}

