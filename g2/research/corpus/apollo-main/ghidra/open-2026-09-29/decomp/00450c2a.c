
int FUN_00450c2a(int param_1,int *param_2,int *param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  char cVar3;
  int iVar4;
  int local_30;
  int *local_2c;
  int *local_28;
  int local_24;
  
  local_30 = param_1;
  local_2c = param_2;
  local_28 = param_3;
  local_24 = param_4;
  iVar1 = FUN_00450f00(param_2,param_3);
  if (iVar1 == 0) {
    iVar1 = -1;
  }
  else {
    iVar1 = FUN_00450f28(param_2,param_3,0);
    if (iVar1 == 0) {
      iVar1 = FUN_00451598(param_2);
      iVar2 = FUN_004515a4(param_2);
      cVar3 = 0 < param_3[1] - param_2[1];
      if ((bool)cVar3) {
        local_30 = *param_2;
        local_2c = (int *)param_2[1];
        local_28 = (int *)param_2[2];
        local_24 = (param_3[1] - param_2[1]) + param_2[1] + -1;
        FUN_00439c04(param_1,&local_30,0x10);
      }
      local_24 = param_2[1] + ((iVar2 + -1) - param_3[3]);
      if ((0 < local_24) && (param_3[3] < param_2[3])) {
        local_30 = *param_2;
        local_2c = (int *)(param_3[3] + 1);
        local_28 = (int *)param_2[2];
        local_24 = local_24 + param_3[3];
        FUN_00439c04(cVar3 * 0x10 + param_1,&local_30,0x10);
        cVar3 = cVar3 + '\x01';
      }
      if (param_2[1] < param_3[1]) {
        iVar2 = param_3[1];
      }
      else {
        iVar2 = param_2[1];
      }
      if (param_3[3] < param_2[3]) {
        iVar4 = param_3[3];
      }
      else {
        iVar4 = param_2[3];
      }
      iVar4 = iVar4 - iVar2;
      if ((0 < *param_3 - *param_2) && (0 < iVar4)) {
        local_30 = *param_2;
        local_28 = (int *)((*param_3 - *param_2) + *param_2 + -1);
        local_24 = iVar4 + iVar2;
        local_2c = (int *)iVar2;
        FUN_00439c04(cVar3 * 0x10 + param_1,&local_30,0x10);
        cVar3 = cVar3 + '\x01';
      }
      iVar1 = *param_2 + ((iVar1 + -1) - param_3[2]);
      if (0 < iVar1) {
        local_30 = param_3[2] + 1;
        local_28 = (int *)(iVar1 + param_3[2]);
        local_24 = iVar4 + iVar2;
        local_2c = (int *)iVar2;
        FUN_00439c04(cVar3 * 0x10 + param_1,&local_30,0x10);
        cVar3 = cVar3 + '\x01';
      }
      iVar1 = (int)cVar3;
    }
    else {
      iVar1 = 0;
    }
  }
  return iVar1;
}

