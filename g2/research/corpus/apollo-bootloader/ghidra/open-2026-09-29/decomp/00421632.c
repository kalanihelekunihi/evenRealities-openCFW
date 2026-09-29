
undefined4 FUN_00421632(byte param_1,byte param_2,char param_3)

{
  byte bVar1;
  undefined4 uVar2;
  
  if ((param_1 < 7) && (param_2 < 0x39)) {
    bVar1 = param_2 >> 5;
    if (param_3 == '\0') {
      *(uint *)(DAT_00422210 + (uint)param_1 * 8 + (uint)bVar1 * 4) =
           *(uint *)(DAT_00422210 + (uint)param_1 * 8 + (uint)bVar1 * 4) &
           ~(1 << (uint)(param_2 & 0x1f));
    }
    else {
      *(uint *)(DAT_00422210 + (uint)param_1 * 8 + (uint)bVar1 * 4) =
           1 << (uint)(param_2 & 0x1f) |
           *(uint *)(DAT_00422210 + (uint)param_1 * 8 + (uint)bVar1 * 4);
    }
    uVar2 = 0;
  }
  else {
    uVar2 = 6;
  }
  return uVar2;
}

