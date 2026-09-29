
void cmdq_adapter_enable_42c420(int param_1)

{
  int *piVar1;
  
  if (*(int *)(param_1 + 0x24) == 0) {
    piVar1 = *(int **)(DAT_0042c6e8 + *(int *)(param_1 + 4) * 0x1000 + 0x22c);
    *piVar1 = DAT_0042c6e8 + *(int *)(param_1 + 4) * 0x1000 + 0x22c;
    piVar1[1] = (int)piVar1;
  }
  cmdq_enable_427878(*(undefined4 *)(param_1 + 0x828));
  return;
}

