
int FUN_005d3544(int *param_1,undefined4 param_2,int param_3,int param_4,int param_5,int param_6,
                char param_7)

{
  char *pcVar1;
  int iVar2;
  
  FUN_0043c0e4(param_1,0x14,0);
  pcVar1 = (char *)FUN_005d23ba(param_2,param_3);
  iVar2 = *(int *)(pcVar1 + 8) - *(int *)(pcVar1 + 4);
  if (iVar2 == -0x150000) {
    if (param_7 == '\0') {
      *param_1 = 0;
    }
    else {
      param_1[2] = *(int *)(pcVar1 + 8);
      *param_1 = 1;
    }
  }
  else if (iVar2 == -0x140000) {
    if (param_7 == '\0') {
      param_1[2] = *(int *)(pcVar1 + 4);
      *param_1 = 2;
    }
    else {
      *param_1 = 0;
    }
  }
  else if (iVar2 < 0) {
    if (param_7 == '\0') {
      param_1[2] = *(int *)(pcVar1 + 4);
      *param_1 = 8;
    }
    else {
      param_1[2] = *(int *)(pcVar1 + 8);
      *param_1 = 4;
    }
  }
  else if (param_7 == '\0') {
    param_1[2] = *(int *)(pcVar1 + 8);
    *param_1 = 8;
  }
  else {
    param_1[2] = *(int *)(pcVar1 + 4);
    *param_1 = 4;
  }
  iVar2 = FUN_005d3672(param_1);
  if (iVar2 != 0) {
    param_1[2] = param_1[2] + *(int *)(param_4 + 0xe8) * 2;
  }
  param_1[2] = param_5 + param_1[2];
  param_1[4] = param_6;
  param_1[1] = param_3;
  if ((*param_1 == 0) || (*pcVar1 == '\0')) {
    iVar2 = FT_MulFix(param_1[2]);
    param_1[3] = iVar2;
  }
  else {
    iVar2 = FUN_005d3672(param_1);
    if (iVar2 == 0) {
      param_1[3] = *(int *)(pcVar1 + 0xc);
    }
    else {
      param_1[3] = *(int *)(pcVar1 + 0x10);
    }
    FUN_005d36ae(param_1);
  }
  return param_4;
}

