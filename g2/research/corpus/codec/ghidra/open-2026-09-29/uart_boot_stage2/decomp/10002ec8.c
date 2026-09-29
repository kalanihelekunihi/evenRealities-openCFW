
uint FUN_10002ec8(int param_1)

{
  uint *puVar1;
  
  puVar1 = *(uint **)(param_1 * 0x80 + DAT_10002ee4 + 4);
  do {
  } while ((puVar1[5] & 1) == 0);
  return *puVar1 & 0xff;
}

