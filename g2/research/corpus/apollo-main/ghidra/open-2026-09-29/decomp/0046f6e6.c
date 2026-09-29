
int FUN_0046f6e6(uint *param_1)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = 0;
  for (uVar2 = *param_1; uVar2 != 0; uVar2 = uVar2 & uVar2 << 1) {
    iVar1 = iVar1 + 1;
  }
  return iVar1;
}

