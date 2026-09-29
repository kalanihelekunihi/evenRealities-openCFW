
void touch_terminal_25f8_reset_three(int param_1)

{
  int iVar1;
  
  *(uint *)(*(int *)(param_1 + 4) + 8) = *(uint *)(*(int *)(param_1 + 4) + 8) & DAT_0000591c;
  iVar1 = 3;
  while (iVar1 != 0) {
    touch_state_2568_reset_object(iVar1 + -1,param_1);
    iVar1 = iVar1 + -1;
  }
  return;
}

