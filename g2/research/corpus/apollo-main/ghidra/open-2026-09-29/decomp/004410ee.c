
undefined4 FUN_004410ee(ushort *param_1,byte param_2)

{
  undefined4 unaff_r7;
  
  if (param_2 != 0xff) {
    if (param_2 == 0) {
      FUN_00440f38(param_1,2);
    }
    else {
      *param_1 = *param_1 & 0x7ff |
                 (ushort)(((int)((uint)param_2 * (uint)(*param_1 >> 0xb)) >> 8) << 0xb);
      *param_1 = *param_1 & 0xf81f |
                 (ushort)(((int)((uint)param_2 * ((*param_1 & 0x7ff) >> 5)) >> 8) << 5);
      *param_1 = (ushort)((uint)param_2 * ((byte)*param_1 & 0x1f) >> 8) | *param_1 & 0xffe0;
    }
  }
  return unaff_r7;
}

