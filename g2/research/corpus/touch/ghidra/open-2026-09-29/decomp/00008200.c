
int touch_eeprom_4f00_physical_bytes(ushort *param_1,int param_2)

{
  return ((uint)*(byte *)(param_2 + 4) +
         (1 - (uint)*(byte *)(param_2 + 4)) * (uint)*(byte *)(param_2 + 5) *
         (*(byte *)(param_2 + 6) + 1)) * (uint)*param_1 * (uint)param_1[1];
}

