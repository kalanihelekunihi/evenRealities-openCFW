
int FUN_004dcd0a(int param_1,int param_2)

{
  if (*(char *)(param_1 + 0x6c) == '\0') {
    param_2 = param_2 * 0x28;
  }
  else {
    param_2 = param_2 * 0x28 + (*(int *)(param_1 + 100) + *(int *)(param_1 + 0x58) * -0x28) / 2;
  }
  return param_2;
}

