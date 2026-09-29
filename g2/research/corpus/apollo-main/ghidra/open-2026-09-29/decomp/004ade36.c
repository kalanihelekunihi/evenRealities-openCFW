
undefined4
als_function_21(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  
  uVar1 = als_function_02();
  if (uVar1 < *DAT_004ae6cc) {
    iVar2 = als_function_20(*DAT_004ae6cc,param_1);
    uVar3 = (*DAT_004ae810 * 0x1e + iVar2 * 0x46) / 100;
    uVar1 = uVar3;
    if (uVar3 < 0x267) {
      uVar1 = 0x266;
    }
    if (uVar1 < 0x59a) {
      if (uVar3 < 0x267) {
        *DAT_004ae810 = 0x266;
      }
      else {
        *DAT_004ae810 = uVar3;
      }
    }
    else {
      *DAT_004ae810 = 0x59a;
    }
    *DAT_004ae818 = *DAT_004ae818 + 1;
    *DAT_004ae814 = iVar2;
    *DAT_004ae94c = 0;
  }
  else {
    *DAT_004ae94c = 1;
    *DAT_004ae814 = 0x400;
  }
  return param_4;
}

