
undefined4 tt_check_trickyness(int param_1)

{
  undefined4 uVar1;
  int iVar2;
  
  if (param_1 == 0) {
    uVar1 = 0;
  }
  else if ((*(int *)(param_1 + 0x14) == 0) ||
          (iVar2 = tt_check_trickyness_family(*(undefined4 *)(param_1 + 0x14)), iVar2 == 0)) {
    iVar2 = tt_check_trickyness_sfnt_ids(param_1);
    if (iVar2 == 0) {
      uVar1 = 0;
    }
    else {
      uVar1 = 1;
    }
  }
  else {
    uVar1 = 1;
  }
  return uVar1;
}

