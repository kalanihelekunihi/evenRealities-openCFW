
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_005e7b2a(byte param_1)

{
  undefined4 uVar1;
  
  uVar1 = _DAT_005e7e64;
  if (param_1 < 0x28) {
    uVar1 = *(undefined4 *)(_DAT_005e7e68 + (uint)param_1 * 4);
  }
  return uVar1;
}

