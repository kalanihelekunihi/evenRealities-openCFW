
undefined4 FUN_0052df12(uint *param_1)

{
  undefined4 uVar1;
  
  if (*param_1 < 9) {
    FUN_004c2e30(*param_1,0);
    FUN_0055c430(param_1[1]);
    if (*(char *)((int)param_1 + 9) != '\0') {
      FUN_0055c7e8(param_1[1],2,1);
    }
    *(undefined1 *)((int)param_1 + 9) = 0;
    FUN_0055c286(param_1[1]);
    *(undefined1 *)(param_1 + 2) = 0;
    uVar1 = 0;
  }
  else {
    uVar1 = 1;
  }
  return uVar1;
}

