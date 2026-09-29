
uint FUN_005da1e8(uint param_1)

{
  uint uVar1;
  
  uVar1 = DAT_005dadf4 * (param_1 ^ param_1 >> 0x10);
  uVar1 = DAT_005dae28 * (uVar1 ^ uVar1 >> 0xd);
  return uVar1 ^ uVar1 >> 0x10;
}

