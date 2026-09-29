
undefined8 FUN_0050f30e(int param_1,int *param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int local_28;
  int *piStack_24;
  int local_20;
  undefined4 uStack_1c;
  
  local_28 = param_1;
  piStack_24 = param_2;
  local_20 = param_3;
  uStack_1c = param_4;
  iVar1 = FUN_0050e9cc(param_1,0);
  iVar2 = FUN_0050e9cc(param_1,0x40000);
  iVar1 = *(int *)(iVar1 + 0xc);
  iVar2 = *(int *)(iVar2 + 0xc);
  iVar3 = FUN_0050e9e0(param_1,0);
  iVar3 = iVar3 + (iVar1 + iVar2) / 2;
  iVar1 = FUN_0043fdda(param_1);
  param_2[1] = (iVar1 / 2 + *(int *)(param_1 + 0x18)) - iVar3 / 2;
  param_2[3] = iVar3 + param_2[1];
  FUN_0043fc2a(param_1,&local_28);
  *param_2 = local_28;
  param_2[2] = local_20;
  return CONCAT44(piStack_24,local_28);
}

