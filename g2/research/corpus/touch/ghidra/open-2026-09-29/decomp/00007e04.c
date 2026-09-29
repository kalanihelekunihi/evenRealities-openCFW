
void touch_sub_4b04(int param_1)

{
  int iVar1;
  
  iVar1 = *(int *)(param_1 + 4);
  *(undefined2 *)(iVar1 + 2) = 0;
  *(undefined1 *)(iVar1 + 6) = 0;
  *(undefined2 *)(iVar1 + 0x16) = 0;
  *(undefined1 *)(iVar1 + 0x1c) = 0;
  return;
}

