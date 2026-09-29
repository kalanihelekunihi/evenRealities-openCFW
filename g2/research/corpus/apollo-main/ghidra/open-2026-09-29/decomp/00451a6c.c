
char FUN_00451a6c(int *param_1)

{
  char cVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = FUN_00452ef8();
  if (iVar2 != 0) {
    if ((*(byte *)(param_1 + 6) & 3) >> 1 != 0) {
      return '\x01';
    }
    if ((int)((uint)*(byte *)(param_1 + 6) << 0x1f) < 0) {
      return '\0';
    }
  }
  if (*(int *)(*param_1 + 8) == 0) {
    iVar2 = 0;
  }
  else {
    iVar2 = *(int *)(*param_1 + 8) + 8;
  }
  cVar1 = FUN_0044ffe6(iVar2,param_1,1);
  if (((((cVar1 == '\x01') && ((*(byte *)(param_1 + 6) & 3) >> 1 == 0)) &&
       (cVar1 = FUN_004516f8(0,param_1), cVar1 == '\x01')) &&
      (((*(byte *)(param_1 + 6) & 3) >> 1 == 0 &&
       (cVar1 = FUN_0044ffe6(iVar2,param_1,0), cVar1 == '\x01')))) &&
     (((*(byte *)(param_1 + 6) & 3) >> 1 == 0 &&
      ((iVar2 = FUN_0044dca2(*param_1), iVar2 != 0 && (iVar3 = FUN_00451b34(param_1), iVar3 != 0))))
     )) {
    *param_1 = iVar2;
    cVar1 = FUN_00451a6c(param_1);
  }
  return cVar1;
}

