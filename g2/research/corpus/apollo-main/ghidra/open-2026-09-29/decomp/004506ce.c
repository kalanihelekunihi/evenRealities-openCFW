
void FUN_004506ce(int param_1,undefined4 param_2,undefined4 param_3)

{
  *(undefined4 *)(param_1 + 0x24) = param_2;
  *(undefined4 *)(param_1 + 0x28) = 0x80000000;
  *(undefined4 *)(param_1 + 0x2c) = param_3;
  return;
}

