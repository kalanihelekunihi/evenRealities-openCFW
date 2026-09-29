
void FUN_005e1686(int param_1,undefined4 param_2,int param_3,int param_4,int param_5,int param_6)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  undefined4 local_34;
  undefined4 local_30;
  
  iVar6 = param_3 >> 8;
  iVar1 = param_5 >> 8;
  if (param_4 == param_6) {
    FUN_005e1618(param_1,iVar1,param_2);
  }
  else {
    iVar2 = param_3 + iVar6 * -0x100;
    if (iVar6 != iVar1) {
      param_3 = param_5 - param_3;
      local_34 = param_6 - param_4;
      if (param_3 < 1) {
        local_30 = 0;
        iVar4 = -1;
        param_3 = -param_3;
        iVar5 = iVar2;
      }
      else {
        local_30 = 0x100;
        iVar4 = 1;
        iVar5 = 0x100 - iVar2;
      }
      iVar5 = local_34 * iVar5;
      iVar3 = iVar5 / param_3;
      iVar5 = iVar5 - param_3 * (iVar5 / param_3);
      if (iVar5 < 0) {
        iVar3 = iVar3 + -1;
        iVar5 = param_3 + iVar5;
      }
      *(int *)(param_1 + 0x98) = iVar3 * (local_30 + iVar2) + *(int *)(param_1 + 0x98);
      *(int *)(param_1 + 0x9c) = iVar3 + *(int *)(param_1 + 0x9c);
      param_4 = iVar3 + param_4;
      iVar6 = iVar4 + iVar6;
      FUN_005e1618(param_1,iVar6,param_2);
      if (iVar6 != iVar1) {
        local_34 = local_34 * 0x100;
        iVar2 = local_34 / param_3;
        local_34 = local_34 - param_3 * (local_34 / param_3);
        if (local_34 < 0) {
          iVar2 = iVar2 + -1;
          local_34 = param_3 + local_34;
        }
        do {
          iVar5 = local_34 + iVar5;
          iVar3 = iVar2;
          if (param_3 <= iVar5) {
            iVar5 = iVar5 - param_3;
            iVar3 = iVar2 + 1;
          }
          *(int *)(param_1 + 0x98) = *(int *)(param_1 + 0x98) + iVar3 * 0x100;
          *(int *)(param_1 + 0x9c) = iVar3 + *(int *)(param_1 + 0x9c);
          param_4 = iVar3 + param_4;
          iVar6 = iVar4 + iVar6;
          FUN_005e1618(param_1,iVar6,param_2);
        } while (iVar6 != iVar1);
      }
      iVar2 = 0x100 - local_30;
    }
    *(int *)(param_1 + 0x98) =
         (param_6 - param_4) * (param_5 + iVar1 * -0x100 + iVar2) + *(int *)(param_1 + 0x98);
    *(int *)(param_1 + 0x9c) = (param_6 - param_4) + *(int *)(param_1 + 0x9c);
  }
  return;
}

