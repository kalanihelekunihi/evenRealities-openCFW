
void ft_synthesize_vertical_metrics(int param_1,int param_2)

{
  int iVar1;
  
  iVar1 = *(int *)(param_1 + 4);
  if (*(int *)(param_1 + 0xc) < 0) {
    if (iVar1 < *(int *)(param_1 + 0xc)) {
      iVar1 = *(int *)(param_1 + 0xc);
    }
  }
  else if (0 < *(int *)(param_1 + 0xc)) {
    iVar1 = iVar1 - *(int *)(param_1 + 0xc);
  }
  if (param_2 == 0) {
    param_2 = (iVar1 * 0xc) / 10;
  }
  *(int *)(param_1 + 0x14) = *(int *)(param_1 + 8) - *(int *)(param_1 + 0x10) / 2;
  *(int *)(param_1 + 0x18) = (param_2 - iVar1) / 2;
  *(int *)(param_1 + 0x1c) = param_2;
  return;
}

