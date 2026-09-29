
undefined4 SkipCode(int param_1)

{
  *(int *)(param_1 + 0x16c) = *(int *)(param_1 + 0x178) + *(int *)(param_1 + 0x16c);
  if (*(int *)(param_1 + 0x16c) < *(int *)(param_1 + 0x170)) {
    *(undefined1 *)(param_1 + 0x174) =
         *(undefined1 *)(*(int *)(param_1 + 0x168) + *(int *)(param_1 + 0x16c));
    *(int *)(param_1 + 0x178) = (int)*(char *)(DAT_005f5b7c + (uint)*(byte *)(param_1 + 0x174));
    if (*(int *)(param_1 + 0x178) < 0) {
      if (*(int *)(param_1 + 0x170) <= *(int *)(param_1 + 0x16c) + 1) goto LAB_005f52c6;
      *(uint *)(param_1 + 0x178) =
           2 - (uint)*(byte *)(*(int *)(param_1 + 0x168) + *(int *)(param_1 + 0x16c) + 1) *
               *(int *)(param_1 + 0x178);
    }
    if (*(int *)(param_1 + 0x178) + *(int *)(param_1 + 0x16c) <= *(int *)(param_1 + 0x170)) {
      return 0;
    }
  }
LAB_005f52c6:
  *(undefined4 *)(param_1 + 0xc) = 0x83;
  return 1;
}

