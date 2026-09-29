
void dmConn2ActDataLenChange(int param_1)

{
  uint local_18;
  
  local_18 = (uint)CONCAT12(0x41,(ushort)*(byte *)(param_1 + 0x10));
  (**(code **)(DAT_004b7430 + 0x9c))(&local_18);
  return;
}

