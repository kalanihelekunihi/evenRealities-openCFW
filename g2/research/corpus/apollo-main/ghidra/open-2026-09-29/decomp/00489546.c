
void FUN_00489546(int *param_1,int param_2,int param_3,undefined4 param_4,int param_5,
                 undefined4 param_6,uint param_7)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  *param_1 = 0;
  param_1[1] = 0;
  if ((param_2 != 0) && (param_3 != 0)) {
    if ((int)(param_7 << 0x1f) < 0) {
      param_6 = 0x1fffffff;
    }
    uVar1 = *(uint *)(param_3 + 0xc);
    iVar4 = 0;
    while (*(char *)(param_2 + iVar4) != '\0') {
      iVar3 = FUN_004897fc(param_2 + iVar4,0xffffffff,param_3,param_4,param_6,0,param_7 & 0xff);
      if (0x7fffffff < param_5 + param_1[1] + (uVar1 & 0xffff)) {
        FUN_0044d25c(2,DAT_00489ea8,0x70,DAT_00489ea4,DAT_00489ea0);
        return;
      }
      param_1[1] = param_1[1] + (uVar1 & 0xffff);
      param_1[1] = param_5 + param_1[1];
      iVar2 = FUN_00489934(param_2 + iVar4,(iVar3 + iVar4) - iVar4,param_3,param_4);
      if (iVar2 <= *param_1) {
        iVar2 = *param_1;
      }
      *param_1 = iVar2;
      iVar4 = iVar3 + iVar4;
    }
    if ((iVar4 != 0) &&
       ((*(char *)(param_2 + iVar4 + -1) == '\n' || (*(char *)(param_2 + iVar4 + -1) == '\r')))) {
      param_1[1] = param_5 + param_1[1] + (uVar1 & 0xffff);
    }
    if (param_1[1] == 0) {
      param_1[1] = uVar1 & 0xffff;
    }
    else {
      param_1[1] = param_1[1] - param_5;
    }
  }
  return;
}

