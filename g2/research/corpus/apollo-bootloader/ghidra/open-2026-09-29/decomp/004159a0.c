
int FUN_004159a0(undefined4 param_1,undefined4 param_2,char *param_3)

{
  longlong lVar1;
  int iVar2;
  int iVar3;
  longlong lVar4;
  char acStack_39 [29];
  
  iVar2 = 0;
  lVar1 = CONCAT44(param_2,param_1);
  do {
    lVar4 = FUN_00415844((int)lVar1,(int)((ulonglong)lVar1 >> 0x20));
    acStack_39[iVar2 + 1] = (char)lVar1 + (char)lVar4 * -10 + '0';
    iVar2 = iVar2 + 1;
    lVar1 = lVar4;
  } while (lVar4 != 0);
  iVar3 = iVar2;
  if (param_3 != (char *)0x0) {
    while (iVar3 != 0) {
      *param_3 = acStack_39[iVar3];
      param_3 = param_3 + 1;
      iVar3 = iVar3 + -1;
    }
    *param_3 = '\0';
  }
  return iVar2;
}

