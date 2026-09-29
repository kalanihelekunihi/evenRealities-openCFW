
void Ins_CINDEX(int param_1,int *param_2)

{
  int iVar1;
  
  iVar1 = *param_2;
  if ((iVar1 < 1) || (*(int *)(param_1 + 0x1c) < iVar1)) {
    if (*(char *)(param_1 + 0x235) != '\0') {
      *(undefined4 *)(param_1 + 0xc) = 0x86;
    }
    *param_2 = 0;
  }
  else {
    *param_2 = *(int *)(*(int *)(param_1 + 0x18) + (*(int *)(param_1 + 0x1c) - iVar1) * 4);
  }
  return;
}

