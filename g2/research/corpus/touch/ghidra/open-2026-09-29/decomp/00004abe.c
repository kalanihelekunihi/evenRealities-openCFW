
int touch_application_17be_preflight(int param_1)

{
  int iVar1;
  
  iVar1 = touch_sub_4a92();
  if (iVar1 == 0) {
    touch_terminal_25f8_reset_three(param_1);
    iVar1 = touch_sub_3ec8(param_1);
    if (*(char *)(*(int *)(param_1 + 4) + 7) == '\0') {
      touch_sub_4b04(param_1);
      *(undefined1 *)(*(int *)(param_1 + 4) + 7) = 1;
    }
  }
  return iVar1;
}

