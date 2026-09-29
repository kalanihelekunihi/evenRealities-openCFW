
uint FUN_00543f8c(int param_1,int param_2,int param_3)

{
  uint uVar1;
  int iVar2;
  
  if (*(char *)(param_2 + 1) == '\x01') {
    uVar1 = 0xffffffff;
  }
  else if (*(int *)(param_3 + 0x50) == -1) {
    uVar1 = *(int *)(param_2 + 4) + 0x10;
  }
  else if ((uint)(*(int *)(param_1 + 0xc) + *(int *)(param_2 + 4)) < *(uint *)(param_3 + 0x50)) {
    uVar1 = 0xffffffff;
  }
  else {
    if (*(char *)(param_3 + 1) == '\0') {
      iVar2 = *(int *)(param_3 + 0x50) + 1;
    }
    else {
      iVar2 = *(int *)(param_3 + 8) + *(int *)(param_3 + 0x50);
    }
    uVar1 = FUN_00543ee8(param_1,iVar2,*(int *)(param_1 + 0xc) + *(int *)(param_2 + 4) + -0x10);
    if (((uVar1 == 0xffffffff) || ((uint)(*(int *)(param_1 + 0xc) + *(int *)(param_2 + 4)) < uVar1))
       || (*(int *)(param_3 + 8) == 0)) {
      uVar1 = 0xffffffff;
    }
  }
  return uVar1;
}

