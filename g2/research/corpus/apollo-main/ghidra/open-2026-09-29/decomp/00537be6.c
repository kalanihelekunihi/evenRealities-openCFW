
undefined4 SmpDmEncryptInd(int param_1)

{
  undefined1 uVar1;
  undefined4 unaff_r7;
  
  if (*(char *)(param_1 + 3) == '\0') {
    uVar1 = 8;
  }
  else {
    uVar1 = 9;
  }
  *(undefined1 *)(param_1 + 2) = uVar1;
  SmpHandler(0);
  return unaff_r7;
}

