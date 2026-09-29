
undefined1 td_record_status_get(int param_1)

{
  undefined1 uVar1;
  uint uVar2;
  uint uVar3;
  
  if (param_1 == -1) {
    uVar1 = *DAT_00597c1c;
  }
  else if ((param_1 == 0) || (*(char *)(DAT_00597c08 + 0xa1d9) == '\0')) {
    uVar1 = 0;
  }
  else {
    uVar3 = *(uint *)(DAT_00597c08 + 0x9568);
    if (10 < uVar3) {
      uVar3 = 10;
    }
    for (uVar2 = 0; uVar2 < uVar3; uVar2 = uVar2 + 1) {
      if (*(int *)(uVar2 * 0x90 + DAT_00597c08 + 0x95fc) == param_1) {
        return *(undefined1 *)(DAT_00597c08 + uVar2 * 0x90 + 0x9682);
      }
    }
    uVar1 = 0;
  }
  return uVar1;
}

