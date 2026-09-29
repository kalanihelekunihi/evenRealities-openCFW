
void FUN_005d3018(int param_1,int *param_2,int *param_3,char *param_4,undefined1 *param_5)

{
  *param_4 = *(char *)(*(int *)(param_1 + 8) + 0xa0);
  *param_5 = *(undefined1 *)(*(int *)(param_1 + 8) + 0xa1);
  if (*param_4 == '\0') {
    *param_2 = 0x400;
    *param_3 = 0x400;
  }
  else {
    *param_2 = (*(int *)(*(int *)(param_1 + 8) + 0xa4) + 0x20) / 0x40;
    *param_3 = (*(int *)(*(int *)(param_1 + 8) + 0xa8) + 0x20) / 0x40;
  }
  return;
}

