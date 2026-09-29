
undefined4 FUN_005ecc1a(short param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  char cVar2;
  int iVar3;
  int iVar4;
  
  iVar1 = DAT_005ed744;
  cVar2 = '\0';
  if (param_1 != *(short *)(DAT_005ed744 + 0x27a)) {
    iVar3 = FUN_005ecb52((int)*(short *)(DAT_005ed744 + 0x27a));
    iVar4 = FUN_005ecb52((int)param_1);
    if ((iVar3 != 0) || (iVar4 != 0)) {
      cVar2 = FUN_005896fc(iVar3,iVar4,200);
    }
    if (cVar2 == '\0') {
      FUN_005ecb88((int)param_1);
    }
    else {
      *(short *)(iVar1 + 0x27a) = param_1;
    }
    FUN_005ecbea((int)param_1);
  }
  return param_4;
}

