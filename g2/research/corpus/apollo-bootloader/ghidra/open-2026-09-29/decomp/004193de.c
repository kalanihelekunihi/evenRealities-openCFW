
void FUN_004193de(int param_1,int param_2,undefined4 param_3)

{
  int iVar1;
  
  while (iVar1 = FUN_00419508(param_1,*(int *)(param_1 + 0x18) + param_2,param_3,param_2),
        iVar1 != 0) {
    param_2 = *(int *)(param_1 + 0x18) + param_2;
    (**(code **)(param_1 + 0x20))(param_1);
  }
  return;
}

