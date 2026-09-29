
void FUN_005d2ee4(int param_1,int param_2)

{
  if (*(char *)(*(int *)(param_1 + 0x1c) + 0x30) == '\0') {
    **(int **)(*(int *)(param_1 + 0x1c) + 0x220) = (int)(short)((uint)(param_2 + 0x8000) >> 0x10);
  }
  return;
}

