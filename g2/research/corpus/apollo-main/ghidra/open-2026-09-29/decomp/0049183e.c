
void FUN_0049183e(int param_1,byte param_2,int param_3)

{
  undefined1 auStack_28 [8];
  undefined4 local_20;
  undefined4 local_18;
  undefined4 local_14;
  
  if (*(int *)(param_3 + 4) != 0) {
    if ((*(int *)(param_3 + 0x10) != 0) || (*(int *)(param_3 + 0x14) != 0)) {
      local_18 = *(undefined4 *)(param_3 + 0x10);
      local_14 = *(undefined4 *)(param_3 + 0x14);
      local_20 = 0;
      (**(code **)(param_3 + 4))(param_1,auStack_28);
    }
    *(undefined4 *)(param_3 + 4) = 0;
    *(undefined4 *)(param_3 + 8) = 0;
    if ((uint)param_2 == *(byte *)(param_1 + 0x7158) - 1) {
      *(char *)(param_1 + 0x7158) = *(char *)(param_1 + 0x7158) + -1;
    }
  }
  return;
}

