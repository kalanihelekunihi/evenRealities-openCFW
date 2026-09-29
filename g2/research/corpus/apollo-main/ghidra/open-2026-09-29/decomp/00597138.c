
undefined4 td_find_record_index(int param_1,uint *param_2)

{
  uint uVar1;
  uint uVar2;
  
  if (((param_1 != 0) && (param_2 != (uint *)0x0)) && (*(char *)(DAT_00597c08 + 0xa1d9) != '\0')) {
    uVar2 = *(uint *)(DAT_00597c08 + 0x9568);
    if (10 < uVar2) {
      uVar2 = 10;
    }
    for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1) {
      if (*(int *)(uVar1 * 0x90 + DAT_00597c08 + 0x95fc) == param_1) {
        *param_2 = uVar1;
        return 1;
      }
    }
  }
  return 0;
}

