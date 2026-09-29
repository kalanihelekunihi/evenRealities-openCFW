
void FUN_0055c13a(int param_1)

{
  int *piVar1;
  
  if (*(int *)(param_1 + 0x24) == 0) {
    piVar1 = *(int **)(DAT_0055c548 + *(int *)(param_1 + 4) * 0x1000 + 0x22c);
    *piVar1 = DAT_0055c548 + *(int *)(param_1 + 4) * 0x1000 + 0x22c;
    piVar1[1] = (int)piVar1;
  }
  FUN_00538e3c(*(undefined4 *)(param_1 + 0x828));
  return;
}

