
undefined4 FUN_0052e49a(char param_1)

{
  uint uVar1;
  undefined4 unaff_r7;
  
  uVar1 = *DAT_0052e6a8;
  if (param_1 != '\0') {
    uVar1 = uVar1 & 0xffff1fff | 0x2000;
  }
  FUN_00480f0c(0x75,uVar1);
  return unaff_r7;
}

