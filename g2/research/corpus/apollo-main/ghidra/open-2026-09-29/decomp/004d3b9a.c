
undefined4 FUN_004d3b9a(void)

{
  uint *puVar1;
  int iVar2;
  undefined4 unaff_r7;
  
  puVar1 = DAT_004d3ce0;
  *DAT_004d3ce0 = *DAT_004d3ce0 & 0xfffffffe;
  if (*DAT_004d3cd0 << 0x18 < 0) {
    iVar2 = 6;
  }
  else {
    iVar2 = 10;
  }
  *puVar1 = DAT_004d3ce4 & iVar2 << 8 | 0x10;
  *DAT_004d3ce8 = 0xffffffff;
  *DAT_004d3cec = 0xffffffff;
  *DAT_004d3cf0 = *DAT_004d3cf0 | 0x4000;
  *puVar1 = *puVar1 | 2;
  *puVar1 = *puVar1 & 0xfffffffd;
  *puVar1 = *puVar1 | 1;
  do {
  } while (*DAT_004d3cf4 == *DAT_004d3cf4);
  *puVar1 = *puVar1 & 0xfffffffe;
  FUN_004807a0(10);
  return unaff_r7;
}

