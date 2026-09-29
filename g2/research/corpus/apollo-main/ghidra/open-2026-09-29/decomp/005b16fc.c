
undefined4 FUN_005b16fc(byte param_1)

{
  undefined4 uVar1;
  
  uVar1 = DAT_005b1afc;
  if (param_1 < 0x15) {
    uVar1 = *(undefined4 *)(DAT_005b1b00 + (uint)param_1 * 4);
  }
  return uVar1;
}

