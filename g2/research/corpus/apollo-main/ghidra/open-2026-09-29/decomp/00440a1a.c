
undefined4 FUN_00440a1c(int param_1)

{
  do {
    param_1 = *(int *)(param_1 + 4);
    if (param_1 == 0) {
      return 0;
    }
  } while ((*(int *)(param_1 + 8) == 0) ||
          ((*(ushort *)(*(int *)(param_1 + 8) + 0x32) & 0xfff) >> 10 != 2));
  return 1;
}

