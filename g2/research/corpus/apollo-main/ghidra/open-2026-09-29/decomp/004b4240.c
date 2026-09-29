
undefined4
FUN_004b4240(byte param_1,byte param_2,ushort param_3,undefined4 param_4,undefined2 param_5,
            ushort param_6)

{
  int iVar1;
  
  iVar1 = DAT_004b46f4;
  *(undefined4 *)((uint)param_1 * 0x10 + DAT_004b46f4 + (uint)param_2 * 4) = param_4;
  *(ushort *)(iVar1 + (uint)param_1 * 8 + (uint)param_2 * 2 + 0x20) = param_3;
  *(undefined2 *)(iVar1 + (uint)param_1 * 8 + (uint)param_2 * 2 + 0x30) = param_5;
  *(ushort *)(iVar1 + (uint)param_1 * 2 + 0x50) = param_6;
  *(undefined2 *)(iVar1 + (uint)param_1 * 8 + (uint)param_2 * 2 + 0x40) = 0;
  if ((((*(char *)((uint)param_1 + iVar1 + 0x57) == '\x03') ||
       (param_2 >> 1 != *(byte *)(iVar1 + 0x5d))) || (0xfb < param_3)) || (param_6 < param_3)) {
    *(undefined1 *)((uint)param_1 + iVar1 + 0x55) = 0;
  }
  else {
    FUN_004b3416(param_1,param_2);
  }
  return param_4;
}

