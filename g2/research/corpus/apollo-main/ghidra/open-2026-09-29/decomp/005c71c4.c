
void FUN_005c71c4(undefined4 param_1,int param_2)

{
  *(undefined4 *)(param_2 + 0x2c) = DAT_005c7328;
  *(uint *)(param_2 + 0x30) = *(uint *)(param_2 + 0x30) | 1;
  FUN_0043ded4(param_2,2);
  FUN_0043ded4(param_2,8);
  FUN_0043ded4(param_2,0x400);
  FUN_0043dfa4(param_2,0x10);
  return;
}

