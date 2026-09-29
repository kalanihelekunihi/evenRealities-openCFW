
int FUN_0046da92(int *param_1)

{
  int iVar1;
  uint uVar2;
  
  if (((param_1 == (int *)0x0) || (*param_1 == 0)) || (param_1[1] == 0)) {
    iVar1 = 0;
  }
  else {
    uVar2 = param_1[3];
    if (uVar2 < (uint)param_1[2]) {
      iVar1 = -uVar2;
    }
    else {
      iVar1 = param_1[1] - uVar2;
    }
    iVar1 = param_1[2] + iVar1 + -1;
  }
  return iVar1;
}

