
int FUN_005d739c(int param_1,int param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = (param_1 + 0x20U & 0xffffffc0) - param_1;
  param_2 = ((param_2 + param_1 + 0x20U & 0xffffffc0) - param_1) - param_2;
  iVar2 = param_2;
  if (param_2 < 0) {
    iVar2 = -param_2;
  }
  iVar3 = iVar1;
  if (iVar1 < 0) {
    iVar3 = -iVar1;
  }
  if (iVar2 < iVar3) {
    iVar1 = param_2;
  }
  return iVar1;
}

