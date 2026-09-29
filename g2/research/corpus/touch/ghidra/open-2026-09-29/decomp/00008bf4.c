
undefined4 ProcessStatusCode(void)

{
  undefined4 uVar1;
  uint uVar2;
  
  uVar2 = *(uint *)(DAT_00008c48 + 8) & 0xf0000000;
  if (uVar2 == 0xa0000000) {
    uVar1 = 0;
  }
  else {
    uVar1 = DAT_00008c4c;
    if ((uVar2 == 0xf0000000) &&
       (uVar2 = *(uint *)(DAT_00008c48 + 8) + DAT_00008c50, uVar1 = DAT_00008c6c, uVar2 < 0x14)) {
                    /* WARNING: Could not recover jumptable at 0x00008c20. Too many branches */
                    /* WARNING: Treating indirect jump as call */
      uVar1 = (**(code **)(DAT_00008c54 + uVar2 * 4))();
      return uVar1;
    }
  }
  return uVar1;
}

