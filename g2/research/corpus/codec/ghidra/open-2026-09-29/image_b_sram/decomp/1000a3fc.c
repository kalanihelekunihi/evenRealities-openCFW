
undefined4 FUN_1000a3fc(int param_1)

{
  undefined4 uVar1;
  
  if (DAT_1000a414[1] < param_1 + *DAT_1000a414) {
    uVar1 = 0xffffffff;
  }
  else {
    *DAT_1000a414 = param_1 + *DAT_1000a414;
    uVar1 = 0;
  }
  return uVar1;
}

