
void FUN_004d0580(undefined4 param_1,code *param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int iVar4;
  
  if (param_2 == (code *)0x0) {
    param_2 = DAT_004d0994;
  }
  iVar1 = FUN_004cfe1a(param_1,-*DAT_004d0964);
  while ((iVar1 != 0 && (iVar4 = FUN_004cfda0(iVar1), iVar4 == 0))) {
    iVar4 = FUN_004cfdb4(iVar1);
    uVar2 = FUN_004cfd70(iVar1);
    uVar3 = FUN_004cfe10(iVar1);
    (*param_2)(uVar3,uVar2,iVar4 == 0,param_3);
    iVar1 = FUN_004cfe44(iVar1);
  }
  return;
}

