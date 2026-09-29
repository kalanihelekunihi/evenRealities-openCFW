
void FUN_00454648(int param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  int local_20;
  int local_1c;
  int local_18;
  int local_14;
  undefined4 uStack_10;
  
  local_20 = *(int *)(param_1 + 0x10) + *param_2;
  local_1c = *(int *)(param_1 + 0x14) + param_2[1];
  local_18 = *(int *)(param_1 + 0x10) + param_2[2];
  local_14 = *(int *)(param_1 + 0x14) + param_2[3];
  uStack_10 = param_4;
  FUN_0044fdbe(param_1,0x3d,&local_20);
  (**(code **)(param_1 + 0x28))(param_1,&local_20,param_3);
  FUN_0044fdbe(param_1,0x3e,&local_20);
  return;
}

