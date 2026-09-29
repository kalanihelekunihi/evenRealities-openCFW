
int FUN_0044d77a(int param_1)

{
  char cVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = 0;
  iVar2 = FUN_00452edc(0);
  while ((iVar3 = iVar4, iVar2 != 0 && (cVar1 = FUN_00452f00(iVar2), iVar3 = iVar2, cVar1 != '\x01')
         )) {
    iVar3 = FUN_00452f18(iVar2);
    if (iVar3 == param_1) {
      iVar4 = iVar2;
    }
    iVar2 = FUN_00452edc(iVar2);
  }
  return iVar3;
}

