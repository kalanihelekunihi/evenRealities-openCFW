
void FUN_0041c838(byte param_1)

{
  uint *puVar1;
  
  puVar1 = DAT_0041cbd4;
  *DAT_0041cbd4 = *DAT_0041cbd4 & 0xfffeffff | (param_1 & 1) << 0x10;
  *puVar1 = *puVar1 & 0xfffffffe | param_1 & 1;
  *puVar1 = *puVar1 & 0xffffffdf | (param_1 & 1) << 5;
  return;
}

