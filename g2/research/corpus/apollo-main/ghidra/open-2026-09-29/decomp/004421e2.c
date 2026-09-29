
longlong FUN_004421e2(void)

{
  uint *puVar1;
  uint unaff_r7;
  
  puVar1 = DAT_00442224;
  *DAT_00442224 = *DAT_00442224 | 0xff0000;
  *puVar1 = *puVar1 | 0xff000000;
  FUN_0045643e();
  *DAT_00442210 = 0;
  vStartFirstTask();
  FUN_004551b4();
  FUN_0044207c();
  return (ulonglong)unaff_r7 << 0x20;
}

