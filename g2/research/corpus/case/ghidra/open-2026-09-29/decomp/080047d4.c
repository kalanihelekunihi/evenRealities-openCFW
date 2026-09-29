
int FUN_080047d4(int *param_1)

{
  int iVar1;
  
  iVar1 = case_status_word2_bit2(*param_1);
  if (iVar1 == 0) {
    if ((char)param_1[0x15] == '\x01') {
      return 2;
    }
    *(undefined1 *)(param_1 + 0x15) = 1;
    iVar1 = case_start_peripheral(param_1);
    if (iVar1 == 0) {
      param_1[0x16] = param_1[0x16] & DAT_08004834 | 0x100;
      param_1[0x17] = 0;
      *(undefined4 *)*param_1 = 0x1c;
      *(undefined1 *)(param_1 + 0x15) = 0;
      *(uint *)(*param_1 + 8) = (*(uint *)(*param_1 + 8) & DAT_08004838) + 4;
    }
    else {
      *(undefined1 *)(param_1 + 0x15) = 0;
    }
  }
  else {
    iVar1 = 2;
  }
  return iVar1;
}

