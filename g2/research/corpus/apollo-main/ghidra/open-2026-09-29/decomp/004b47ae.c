
undefined4 error_check(int param_1)

{
  int *piVar1;
  undefined4 unaff_r7;
  
  piVar1 = DAT_004b4d3c;
  if (param_1 != 0) {
    *DAT_004b4d3c = param_1;
    if (*DAT_004b4d40 != 0) {
      (*(code *)*DAT_004b4d40)(*piVar1);
    }
  }
  return unaff_r7;
}

