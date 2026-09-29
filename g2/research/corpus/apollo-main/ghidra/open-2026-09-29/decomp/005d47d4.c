
void FUN_005d47d4(int param_1,int param_2,int param_3)

{
  bool bVar1;
  int iVar2;
  int local_3c;
  int local_38;
  int local_34;
  int local_30;
  int local_2c;
  int local_28;
  
  iVar2 = FUN_005d4b18(*(undefined4 *)(param_1 + 0x2d9c));
  if ((iVar2 == 0) || (*(char *)(param_1 + 0x2d91) != '\0')) {
    bVar1 = false;
  }
  else {
    bVar1 = true;
  }
  if (((*(int *)(param_1 + 0x2dc8) != param_2) || (*(int *)(param_1 + 0x2dcc) != param_3)) ||
     (bVar1)) {
    FUN_005d4582(param_1,*(undefined4 *)(param_1 + 0x2dc8),*(undefined4 *)(param_1 + 0x2dcc),param_2
                 ,param_3,&local_38,&local_3c);
    local_2c = local_38 + *(int *)(param_1 + 0x2dc8);
    local_28 = local_3c + *(int *)(param_1 + 0x2dcc);
    local_34 = local_38 + param_2;
    local_30 = local_3c + param_3;
    if (*(char *)(param_1 + 0x2d93) != '\0') {
      FUN_005d4510(param_1,local_2c,local_28);
      *(undefined1 *)(param_1 + 0x2d93) = 0;
      *(undefined1 *)(param_1 + 0x2d90) = 1;
      *(int *)(param_1 + 0x2dc0) = local_34;
      *(int *)(param_1 + 0x2dc4) = local_30;
    }
    if (*(char *)(param_1 + 0x2de0) != '\0') {
      FUN_005d431e(param_1,param_1 + 8,&local_2c,local_34,local_30,0);
    }
    *(undefined1 *)(param_1 + 0x2de0) = 1;
    *(undefined4 *)(param_1 + 0x2de4) = 2;
    *(int *)(param_1 + 0x2de8) = local_2c;
    *(int *)(param_1 + 0x2dec) = local_28;
    *(int *)(param_1 + 0x2df0) = local_34;
    *(int *)(param_1 + 0x2df4) = local_30;
    if (bVar1) {
      FUN_005d3c0a(param_1 + 8,*(undefined4 *)(param_1 + 0x2d94),*(undefined4 *)(param_1 + 0x2d98),
                   *(undefined4 *)(param_1 + 0x2d9c),*(undefined4 *)(param_1 + 0x2da0),0);
    }
    *(int *)(param_1 + 0x2dc8) = param_2;
    *(int *)(param_1 + 0x2dcc) = param_3;
  }
  return;
}

