
void FUN_10002ee8(int param_1,uint param_2)

{
  uint *puVar1;
  
  puVar1 = *(uint **)(param_1 * 0x80 + DAT_10002f1c + 4);
  if (param_2 == 10) {
    do {
    } while ((puVar1[5] & 0x20) == 0);
    *puVar1 = 0xd;
  }
  do {
  } while ((puVar1[5] & 0x20) == 0);
  *puVar1 = param_2 & 0xff;
  return;
}

