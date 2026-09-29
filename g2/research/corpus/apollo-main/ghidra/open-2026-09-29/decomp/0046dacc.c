
int FUN_0046dacc(int *param_1)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  if (((param_1 == (int *)0x0) || (*param_1 == 0)) || (param_1[1] == 0)) {
    iVar1 = 0;
  }
  else {
    uVar2 = param_1[3];
    uVar3 = param_1[2];
    if (uVar2 < uVar3) {
      iVar1 = uVar2 + (param_1[1] - uVar3);
    }
    else {
      iVar1 = uVar2 - uVar3;
    }
  }
  return iVar1;
}

