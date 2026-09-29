
uint FUN_004b15b4(uint param_1)

{
  byte bVar1;
  
  bVar1 = (byte)(param_1 >> 0x18);
  return ((uint)((ulonglong)(uint)((int)(short)(ushort)bVar1 * (int)(short)((ushort)param_1 & 0xff))
                 * (ulonglong)DAT_004b1aac >> 0x20) & 0x7fff) >> 7 |
         (((uint)((ulonglong)
                  (uint)((int)(short)(ushort)bVar1 * (int)(short)(ushort)(byte)(param_1 >> 8)) *
                  (ulonglong)DAT_004b1aac >> 0x20) & 0x7fff) >> 7) << 8 |
         (((uint)((ulonglong)
                  (uint)((int)(short)(ushort)bVar1 * (int)(short)(ushort)(byte)(param_1 >> 0x10)) *
                  (ulonglong)DAT_004b1aac >> 0x20) & 0x7fff) >> 7) << 0x10 | param_1 & 0xff000000;
}

