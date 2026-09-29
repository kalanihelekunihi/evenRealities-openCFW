
int FUN_10003458(int param_1,int param_2,int param_3,undefined4 param_4,undefined4 param_5)

{
  int iVar1;
  int iVar2;
  int local_18;
  
  local_18 = 0;
  iVar2 = param_3;
  if (((*(uint *)(param_1 + 0x6c) == 0) ||
      (iVar1 = (*(code *)(*(uint *)(param_1 + 0x6c) & 0xfffffffe))(param_2,param_3,&local_18),
      iVar2 = local_18, iVar1 == 0)) && (local_18 = iVar2, *(uint *)(param_1 + 0x10) != 0)) {
    iVar2 = (*(code *)(*(uint *)(param_1 + 0x10) & 0xfffffffe))(local_18 + param_2,param_4,param_5);
    return iVar2 >> 0x1f;
  }
  return -1;
}

