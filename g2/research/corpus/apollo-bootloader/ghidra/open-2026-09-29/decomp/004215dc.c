
uint FUN_004215dc(byte param_1,byte param_2)

{
  return *(uint *)(DAT_00422210 + (uint)param_1 * 8 + (uint)(param_2 >> 5) * 4) >>
         (uint)(param_2 & 0x1f) & 1;
}

