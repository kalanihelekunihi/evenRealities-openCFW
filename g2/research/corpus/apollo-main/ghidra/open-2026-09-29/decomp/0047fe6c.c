
void FUN_0047fe6c(byte param_1)

{
  uint *puVar1;
  
  puVar1 = DAT_004801d0;
  *DAT_004801d0 = *DAT_004801d0 & 0xfffeffff | (param_1 & 1) << 0x10;
  *puVar1 = *puVar1 & 0xfffffffe | param_1 & 1;
  *puVar1 = *puVar1 & 0xffffffdf | (param_1 & 1) << 5;
  return;
}

