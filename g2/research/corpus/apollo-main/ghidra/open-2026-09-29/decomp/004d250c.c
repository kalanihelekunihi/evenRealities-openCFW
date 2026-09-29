
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void DmSecInit(void)

{
  undefined4 *puVar1;
  
  *(undefined4 *)(_DAT_004d253c + 0x14) = _DAT_004d2538;
  puVar1 = DAT_004d2540;
  *DAT_004d2540 = DAT_004d2530;
  puVar1[1] = *puVar1;
  return;
}

