
void td_record_status_set(int param_1,char param_2)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  iVar1 = DAT_00597c08;
  if (param_1 == -1) {
    *DAT_00597c1c = param_2;
  }
  else if ((param_1 != 0) && (*(char *)(DAT_00597c08 + 0xa1d9) != '\0')) {
    uVar3 = *(uint *)(DAT_00597c08 + 0x9568);
    if (10 < uVar3) {
      uVar3 = 10;
    }
    for (uVar2 = 0; uVar2 < uVar3; uVar2 = uVar2 + 1) {
      if (*(int *)(uVar2 * 0x90 + DAT_00597c08 + 0x95fc) == param_1) {
        *(char *)(uVar2 * 0x90 + DAT_00597c08 + 0x9682) = param_2;
        if (param_2 == '\x02') {
          return;
        }
        *(undefined1 *)(iVar1 + uVar2 * 0x90 + 0x9688) = 0;
        return;
      }
    }
  }
  return;
}

