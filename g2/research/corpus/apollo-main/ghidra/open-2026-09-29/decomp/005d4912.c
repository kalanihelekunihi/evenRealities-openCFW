
void FUN_005d4912(int param_1,int param_2,int param_3,int param_4,int param_5,int param_6,
                 int param_7)

{
  int iVar1;
  int local_5c;
  int local_58;
  int local_54;
  int local_50;
  int local_4c;
  int local_48;
  int local_44;
  int local_40;
  int local_3c;
  int local_38;
  int local_34;
  int local_30;
  int iStack_2c;
  int local_28;
  
  iStack_2c = param_1;
  local_28 = param_2;
  FUN_005d4582(param_1,*(undefined4 *)(param_1 + 0x2dc8),*(undefined4 *)(param_1 + 0x2dcc),param_2,
               param_3,&local_50,&local_54);
  FUN_005d4582(param_1,param_4,param_5,param_6,param_7,&local_58,&local_5c);
  iVar1 = FUN_005d352e(local_28,param_3,param_4,param_5);
  *(int *)(*(int *)(param_1 + 4) + 0x10) = iVar1 + *(int *)(*(int *)(param_1 + 4) + 0x10);
  local_44 = local_50 + *(int *)(param_1 + 0x2dc8);
  local_40 = local_54 + *(int *)(param_1 + 0x2dcc);
  local_4c = local_50 + local_28;
  local_48 = local_54 + param_3;
  local_34 = local_58 + param_4;
  local_30 = local_5c + param_5;
  local_3c = local_58 + param_6;
  local_38 = local_5c + param_7;
  if (*(char *)(param_1 + 0x2d93) != '\0') {
    FUN_005d4510(param_1,local_44,local_40);
    *(undefined1 *)(param_1 + 0x2d93) = 0;
    *(undefined1 *)(param_1 + 0x2d90) = 1;
    *(int *)(param_1 + 0x2dc0) = local_4c;
    *(int *)(param_1 + 0x2dc4) = local_48;
  }
  if (*(char *)(param_1 + 0x2de0) != '\0') {
    FUN_005d431e(param_1,param_1 + 8,&local_44,local_4c,local_48,0);
  }
  *(undefined1 *)(param_1 + 0x2de0) = 1;
  *(undefined4 *)(param_1 + 0x2de4) = 4;
  *(int *)(param_1 + 0x2de8) = local_44;
  *(int *)(param_1 + 0x2dec) = local_40;
  *(int *)(param_1 + 0x2df0) = local_4c;
  *(int *)(param_1 + 0x2df4) = local_48;
  *(int *)(param_1 + 0x2df8) = local_34;
  *(int *)(param_1 + 0x2dfc) = local_30;
  *(int *)(param_1 + 0x2e00) = local_3c;
  *(int *)(param_1 + 0x2e04) = local_38;
  iVar1 = FUN_005d4b18(*(undefined4 *)(param_1 + 0x2d9c));
  if (iVar1 != 0) {
    FUN_005d3c0a(param_1 + 8,*(undefined4 *)(param_1 + 0x2d94),*(undefined4 *)(param_1 + 0x2d98),
                 *(undefined4 *)(param_1 + 0x2d9c),*(undefined4 *)(param_1 + 0x2da0),0);
  }
  *(int *)(param_1 + 0x2dc8) = param_6;
  *(int *)(param_1 + 0x2dcc) = param_7;
  return;
}

