
void FUN_0041c7de(void)

{
  uint *puVar1;
  
  puVar1 = DAT_0041cbd4;
  *DAT_0041cbd4 = *DAT_0041cbd4 | 0x20000;
  *puVar1 = *puVar1 | 0x40000;
  *puVar1 = *puVar1 | 0x80000;
  *puVar1 = *puVar1 | 0x10000;
  *puVar1 = *puVar1 & 0xffffffef;
  *puVar1 = *puVar1 | 0xe;
  *puVar1 = *puVar1 | 1;
  *puVar1 = *puVar1 & 0xfffffdff;
  *puVar1 = *puVar1 | 0x1c0;
  *puVar1 = *puVar1 | 0x20;
  return;
}

