
ushort FUN_00491730(ushort param_1,byte param_2)

{
  return *(ushort *)(DAT_00491ef0 + (((uint)param_1 ^ (uint)param_2) & 0xff) * 2) ^ param_1 >> 8;
}

