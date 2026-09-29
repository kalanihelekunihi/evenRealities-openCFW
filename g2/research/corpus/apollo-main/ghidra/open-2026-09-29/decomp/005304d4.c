
undefined4 WsfBufFree(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = *DAT_00530514 + (uint)*DAT_00530518 * 0xc;
  do {
    uVar1 = uVar2;
    if (uVar1 - 0xc < *DAT_00530514) {
      return param_4;
    }
    uVar2 = uVar1 - 0xc;
  } while (param_1 < *(undefined4 **)(uVar1 - 8));
  WsfCsEnter();
  param_1[1] = DAT_00530534;
  *param_1 = *(undefined4 *)(uVar1 - 4);
  *(undefined4 **)(uVar1 - 4) = param_1;
  WsfCsExit();
  return param_4;
}

