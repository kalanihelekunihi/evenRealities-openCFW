
undefined1 FUN_005456d6(undefined4 param_1)

{
  undefined1 local_3;
  undefined1 local_2;
  
  local_2 = (byte)((uint)param_1 >> 0x10);
  local_3 = (byte)((uint)param_1 >> 8);
  return (char)((ushort)((ushort)local_3 * 0x24 + (ushort)local_2 * 0xdc) >> 8);
}

