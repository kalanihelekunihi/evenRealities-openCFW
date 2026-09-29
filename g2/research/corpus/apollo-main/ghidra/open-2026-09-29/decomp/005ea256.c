
uint FUN_005ea256(uint param_1)

{
  uint uVar1;
  
  uVar1 = DAT_005eadac * (param_1 ^ param_1 >> 0x10);
  uVar1 = DAT_005eadb0 * (uVar1 ^ uVar1 >> 0xf);
  return uVar1 ^ uVar1 >> 0x10;
}

