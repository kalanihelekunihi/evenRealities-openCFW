
void Ins_JMPR(int param_1,int *param_2)

{
  if ((*param_2 == 0) && (*(int *)(param_1 + 0x1c) == 0)) {
    *(undefined4 *)(param_1 + 0xc) = 0x84;
  }
  else {
    *(int *)(param_1 + 0x16c) = *param_2 + *(int *)(param_1 + 0x16c);
    if ((*(int *)(param_1 + 0x16c) < 0) ||
       ((0 < *(int *)(param_1 + 0x1b0) &&
        (*(int *)(*(int *)(*(int *)(param_1 + 0x1b8) + *(int *)(param_1 + 0x1b0) * 0x10 + -4) + 8) <
         *(int *)(param_1 + 0x16c))))) {
      *(undefined4 *)(param_1 + 0xc) = 0x84;
    }
    else {
      *(undefined1 *)(param_1 + 0x17c) = 0;
      if ((*param_2 < 0) &&
         (*(int *)(param_1 + 0x274) = *(int *)(param_1 + 0x274) + 1,
         *(uint *)(param_1 + 0x278) < *(uint *)(param_1 + 0x274))) {
        *(undefined4 *)(param_1 + 0xc) = 0x8b;
      }
    }
  }
  return;
}

