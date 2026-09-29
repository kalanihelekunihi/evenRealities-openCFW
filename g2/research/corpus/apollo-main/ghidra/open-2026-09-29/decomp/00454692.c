
void FUN_00454692(int param_1)

{
  FUN_0044fdbe(param_1,0x3f,0);
  if (*(int *)(param_1 + 0x2c) == 0) {
    do {
    } while (*(int *)(param_1 + 0x30) != 0);
  }
  else if (*(int *)(param_1 + 0x30) != 0) {
    (**(code **)(param_1 + 0x2c))(param_1);
    *(undefined4 *)(param_1 + 0x30) = 0;
  }
  *(undefined4 *)(param_1 + 0x34) = 0;
  FUN_0044fdbe(param_1,0x40,0);
  return;
}

