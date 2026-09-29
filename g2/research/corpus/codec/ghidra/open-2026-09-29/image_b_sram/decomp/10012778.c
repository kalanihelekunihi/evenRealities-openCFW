
int FUN_10012778(uint *param_1,uint *param_2)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar2 = *param_1;
  if ((uVar2 < 2) || (uVar4 = *param_2, uVar4 < 2)) {
    return 1;
  }
  if (uVar2 == 4) {
    if (uVar4 == 4) {
      return param_2[1] - param_1[1];
    }
LAB_100127ce:
    iVar1 = -1;
    if (param_1[1] == 0) {
      iVar1 = 1;
    }
    return iVar1;
  }
  if (uVar4 != 4) {
    if (uVar2 != 2) {
      if (uVar4 == 2) goto LAB_100127ce;
      uVar2 = param_1[1];
      if (uVar2 != param_2[1]) {
LAB_100127a6:
        iVar1 = -1;
        if (uVar2 == 0) {
          iVar1 = 1;
        }
        return iVar1;
      }
      if ((int)param_2[2] < (int)param_1[2]) goto LAB_100127a6;
      if ((int)param_1[2] < (int)param_2[2]) {
        if (uVar2 != 0) {
          return 1;
        }
        return -1;
      }
      uVar3 = param_1[4];
      uVar4 = param_2[4];
      if ((uVar4 < uVar3) || ((uVar3 == uVar4 && (param_2[3] < param_1[3])))) {
        if (uVar2 == 0) {
          return 1;
        }
        return -1;
      }
      if (uVar4 <= uVar3) {
        if (uVar4 != uVar3) {
          return 0;
        }
        if (param_2[3] <= param_1[3]) {
          return 0;
        }
      }
      goto LAB_100127ba;
    }
    if (uVar4 == 2) {
      return 0;
    }
  }
  uVar2 = param_2[1];
LAB_100127ba:
  iVar1 = 1;
  if (uVar2 == 0) {
    iVar1 = -1;
  }
  return iVar1;
}

