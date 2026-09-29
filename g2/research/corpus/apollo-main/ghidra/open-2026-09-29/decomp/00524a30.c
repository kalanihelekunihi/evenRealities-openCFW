
undefined4 ft_corner_orientation(int param_1,int param_2,int param_3,int param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  uint local_20;
  uint local_1c;
  uint local_18;
  uint local_14;
  int iStack_10;
  
  iVar2 = param_1;
  if (param_1 < 0) {
    iVar2 = -param_1;
  }
  iVar3 = param_4;
  if (param_4 < 0) {
    iVar3 = -param_4;
  }
  if (iVar3 + iVar2 < 0x20000) {
    iVar2 = param_2;
    if (param_2 < 0) {
      iVar2 = -param_2;
    }
    iVar3 = param_3;
    if (param_3 < 0) {
      iVar3 = -param_3;
    }
    if (iVar3 + iVar2 < 0x20000) {
      if (param_3 * param_2 < param_4 * param_1) {
        return 1;
      }
      if (param_4 * param_1 < param_3 * param_2) {
        return 0xffffffff;
      }
      return 0;
    }
  }
  iStack_10 = param_4;
  ft_multo64(param_1,param_4,&local_18);
  ft_multo64(param_2,param_3,&local_20);
  if (local_1c < local_14) {
    uVar1 = 1;
  }
  else if (local_14 < local_1c) {
    uVar1 = 0xffffffff;
  }
  else if (local_20 < local_18) {
    uVar1 = 1;
  }
  else if (local_18 < local_20) {
    uVar1 = 0xffffffff;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

