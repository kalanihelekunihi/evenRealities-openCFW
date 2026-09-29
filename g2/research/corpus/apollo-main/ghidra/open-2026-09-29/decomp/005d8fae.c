
void FUN_005d8fae(uint *param_1,int param_2,int param_3,undefined4 param_4,uint *param_5)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  int *local_28;
  undefined4 local_24;
  
  iVar2 = 0;
  if (param_3 < 0) {
    iVar2 = 1;
    if (param_3 == -0x15) {
      iVar2 = 3;
      param_2 = param_2 + -0x15;
    }
    param_3 = 0;
  }
  if (param_5 != (uint *)0x0) {
    *param_5 = 0xffffffff;
  }
  uVar3 = 0;
  for (local_28 = (int *)param_1[2];
      (uVar3 < *param_1 && ((*local_28 != param_2 || (local_28[1] != param_3))));
      local_28 = local_28 + 3) {
    uVar3 = uVar3 + 1;
  }
  local_24 = param_4;
  if (*param_1 <= uVar3) {
    iVar1 = FUN_005d8b60(param_1,param_4,&local_28);
    if (iVar1 != 0) {
      return;
    }
    *local_28 = param_2;
    local_28[1] = param_3;
    local_28[2] = iVar2;
  }
  iVar2 = FUN_005d8d18(param_1 + 3,param_4,&local_24);
  if (((iVar2 == 0) && (iVar2 = FUN_005d8c3e(local_24,uVar3,param_4), iVar2 == 0)) &&
     (param_5 != (uint *)0x0)) {
    *param_5 = uVar3;
  }
  return;
}

