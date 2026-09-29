
int FUN_1000e314(int param_1,int param_2)

{
  if (param_2 != 0) {
    return *(int *)(param_1 + 0x1c) * 0x48 + *(int *)(param_1 + 0xc) * 10 +
           *(int *)(param_1 + 0x1c) * *(int *)(param_1 + 0x68) * 8 +
           *(int *)(param_1 + 0x10) * 4 + (*(int *)(param_1 + 0x74) * 2 + 1) * 4;
  }
  return 0;
}

