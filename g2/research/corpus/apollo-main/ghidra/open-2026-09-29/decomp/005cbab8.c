
void FUN_005cbab8(int param_1,int *param_2,int param_3,char param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  
  if (param_4 == '\0') {
    param_2[1] = param_2[1] - (param_3 >> 1);
    param_2[3] = param_3 + param_2[1] + -1;
    *param_2 = *(int *)(param_1 + 0x14);
    param_2[2] = *(int *)(param_1 + 0x1c);
  }
  else {
    *param_2 = *param_2 - (param_3 >> 1);
    param_2[2] = param_3 + *param_2 + -1;
    param_2[1] = *(int *)(param_1 + 0x18);
    param_2[3] = *(int *)(param_1 + 0x20);
  }
  iVar1 = FUN_005cb462(param_1,0x30000);
  iVar2 = FUN_005cb46c(param_1,0x30000);
  iVar3 = FUN_005cb44e(param_1,0x30000);
  iVar4 = FUN_005cb458(param_1,0x30000);
  iVar5 = FUN_005cb43a(param_1,0x30000);
  iVar6 = FUN_005cb444(param_1,0x30000);
  *param_2 = (*param_2 - iVar1) - iVar5;
  param_2[2] = iVar5 + iVar2 + param_2[2];
  param_2[1] = (param_2[1] - iVar3) - iVar6;
  param_2[3] = iVar6 + iVar4 + param_2[3];
  return;
}

