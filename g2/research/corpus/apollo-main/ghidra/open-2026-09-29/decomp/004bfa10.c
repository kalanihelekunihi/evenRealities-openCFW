
uint FUN_004bfa10(int param_1,uint param_2)

{
  if (*(int *)(param_1 + 0x838) == 1) {
    param_2 = param_2 | 0x40a0;
    *(undefined4 *)(param_1 + 0x838) = 2;
  }
  else if (*(int *)(param_1 + 0x838) == 2) {
    param_2 = 0x4000;
  }
  else {
    param_2 = param_2 | 0x4080;
  }
  return param_2;
}

