
int FUN_004d445e(int param_1,uint param_2,int param_3,int param_4)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  
  if (param_4 == 1) {
    *(uint *)(param_1 + 8) = param_2;
    FUN_004d4446(param_1 + 0xc,param_3,2);
  }
  else {
    uVar2 = param_2 & 0xfffffffc;
    param_2 = param_2 & 3;
    *(uint *)(param_1 + 8) = uVar2;
    for (iVar1 = param_4; 4 < iVar1 + param_2; iVar1 = iVar1 - iVar3) {
      iVar3 = 4 - param_2;
      FUN_004d4446(param_1 + param_2 * 8 + 0xc,param_3,iVar3 * 2);
      param_3 = param_3 + iVar3 * 8;
      param_2 = 0;
      uVar2 = uVar2 + 4;
      *(uint *)(param_1 + 8) = uVar2;
    }
    FUN_004d4446(param_1 + param_2 * 8 + 0xc,param_3,iVar1 * 2);
  }
  return param_4;
}

