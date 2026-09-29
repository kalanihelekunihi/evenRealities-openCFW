
longlong FUN_0041b4f6(void)

{
  uint *puVar1;
  uint unaff_r7;
  
  puVar1 = DAT_0041b538;
  *DAT_0041b538 = *DAT_0041b538 | 0xff0000;
  *puVar1 = *puVar1 | 0xff000000;
  FUN_0041b6fa();
  *DAT_0041b524 = 0;
  FUN_0041b2e0();
  FUN_00418570();
  FUN_0041b390();
  return (ulonglong)unaff_r7 << 0x20;
}

