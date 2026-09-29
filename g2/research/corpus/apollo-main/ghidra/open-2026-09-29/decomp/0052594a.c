
undefined4 find_unicode_charmap(int param_1)

{
  int *piVar1;
  int *piVar2;
  
  piVar2 = *(int **)(param_1 + 0x28);
  if (piVar2 == (int *)0x0) {
    return 0x26;
  }
  piVar1 = piVar2 + *(int *)(param_1 + 0x24);
  do {
    piVar1 = piVar1 + -1;
    if (piVar1 < piVar2) {
      piVar1 = piVar2 + *(int *)(param_1 + 0x24);
      do {
        piVar1 = piVar1 + -1;
        if (piVar1 < piVar2) {
          return 0x26;
        }
      } while (*(int *)(*piVar1 + 4) != DAT_005262a4);
      *(int *)(param_1 + 0x5c) = *piVar1;
      return 0;
    }
  } while ((*(int *)(*piVar1 + 4) != DAT_005262a4) ||
          (((*(short *)(*piVar1 + 8) != 3 || (*(short *)(*piVar1 + 10) != 10)) &&
           ((*(short *)(*piVar1 + 8) != 0 || (*(short *)(*piVar1 + 10) != 4))))));
  *(int *)(param_1 + 0x5c) = *piVar1;
  return 0;
}

