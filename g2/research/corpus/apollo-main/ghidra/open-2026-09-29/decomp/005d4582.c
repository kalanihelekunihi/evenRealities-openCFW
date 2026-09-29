
int FUN_005d4582(int *param_1,int param_2,int param_3,int param_4,int param_5,int *param_6,
                int *param_7)

{
  int iVar1;
  int iVar2;
  
  iVar2 = param_4 - param_2;
  param_5 = param_5 - param_3;
  if (*(char *)(*param_1 + 0xec) != '\0') {
    iVar2 = -iVar2;
    param_5 = -param_5;
  }
  *param_7 = 0;
  *param_6 = *param_7;
  if (*(char *)((int)param_1 + 0x2d92) != '\0') {
    iVar1 = FUN_005d352e(param_2);
    *(int *)(param_1[1] + 0x10) = iVar1 + *(int *)(param_1[1] + 0x10);
    if (iVar2 < 0) {
      if (param_5 < 0) {
        if (param_5 * -2 + iVar2 < 0 == SCARRY4(param_5 * -2,iVar2)) {
          if (iVar2 * -2 + param_5 < 0 == SCARRY4(iVar2 * -2,param_5)) {
            iVar2 = FT_MulFix(DAT_005d474c,param_1[0xb6a]);
            *param_6 = iVar2;
            iVar2 = FT_MulFix(DAT_005d4750,param_1[0xb6b]);
            *param_7 = iVar2;
          }
          else {
            *param_6 = -param_1[0xb6a];
            *param_7 = param_1[0xb6b];
          }
        }
        else {
          *param_6 = 0;
          *param_7 = param_1[0xb6b] << 1;
        }
      }
      else if (param_5 * 2 + iVar2 < 0 == SCARRY4(param_5 * 2,iVar2)) {
        if (iVar2 * -2 < param_5) {
          *param_6 = param_1[0xb6a];
          *param_7 = param_1[0xb6b];
        }
        else {
          iVar2 = FT_MulFix(0xb333,param_1[0xb6a]);
          *param_6 = iVar2;
          iVar2 = FT_MulFix(DAT_005d4750,param_1[0xb6b]);
          *param_7 = iVar2;
        }
      }
      else {
        *param_6 = 0;
        *param_7 = param_1[0xb6b] << 1;
      }
    }
    else if (param_5 < 0) {
      if (param_5 * -2 < iVar2) {
        *param_6 = 0;
        *param_7 = 0;
      }
      else if (iVar2 * 2 + param_5 < 0 == SCARRY4(iVar2 * 2,param_5)) {
        iVar2 = FT_MulFix(DAT_005d474c,param_1[0xb6a]);
        *param_6 = iVar2;
        iVar2 = FT_MulFix(0x4ccd,param_1[0xb6b]);
        *param_7 = iVar2;
      }
      else {
        *param_6 = -param_1[0xb6a];
        *param_7 = param_1[0xb6b];
      }
    }
    else if (param_5 * 2 < iVar2) {
      *param_6 = 0;
      *param_7 = 0;
    }
    else if (iVar2 * 2 < param_5) {
      *param_6 = param_1[0xb6a];
      *param_7 = param_1[0xb6b];
    }
    else {
      iVar2 = FT_MulFix(0xb333,param_1[0xb6a]);
      *param_6 = iVar2;
      iVar2 = FT_MulFix(0x4ccd,param_1[0xb6b]);
      *param_7 = iVar2;
    }
  }
  return param_4;
}

