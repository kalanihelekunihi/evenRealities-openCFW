
undefined4 FUN_0059fb70(char param_1)

{
  undefined4 unaff_r7;
  
  if (param_1 == '\0') {
    FUN_0047fe6c(0);
    FUN_004807a0(5);
    *DAT_0059ff98 = *DAT_0059ff98 & 0xfffffffe;
  }
  else {
    *DAT_0059ff98 = *DAT_0059ff98 | 1;
    FUN_004807a0(5);
    FUN_0047fe6c(1);
  }
  return unaff_r7;
}

