
int FUN_005858a8(int param_1,int param_2)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  iVar1 = 0;
  uVar2 = param_2 - 1U;
  while ((uVar3 = uVar2 - 1, uVar2 != 0 &&
         ((*(byte *)(param_1 + (uVar3 >> 3)) & 0x80U >> (uVar3 & 7)) != 0))) {
    iVar1 = iVar1 + 1;
    uVar2 = uVar3;
  }
  return (param_2 - 1U) - iVar1;
}

