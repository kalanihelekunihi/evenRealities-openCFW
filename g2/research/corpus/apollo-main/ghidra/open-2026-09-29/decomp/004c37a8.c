
uint FUN_004c37a8(byte param_1,byte param_2)

{
  return *(uint *)(DAT_004c43dc + (uint)param_1 * 8 + (uint)(param_2 >> 5) * 4) >>
         (uint)(param_2 & 0x1f) & 1;
}

