
uint FUN_0048ecae(byte *param_1,int param_2)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  
  uVar1 = 0xffffffff;
  while (iVar2 = param_2 + -1, param_2 != 0) {
    uVar1 = uVar1 ^ *param_1;
    param_1 = param_1 + 1;
    for (iVar3 = 0; param_2 = iVar2, iVar3 < 8; iVar3 = iVar3 + 1) {
      uVar1 = -(uVar1 & 1) & DAT_0048eda8 ^ uVar1 >> 1;
    }
  }
  return ~uVar1;
}

