
undefined4 FUN_004b3514(byte param_1,char param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  byte bVar2;
  byte bVar3;
  
  iVar1 = DAT_004b3c8c;
  bVar2 = param_2 << 1;
  bVar3 = param_2 * '\x02' + 1;
  if (*(ushort *)(DAT_004b3c8c + (uint)param_1 * 8 + (uint)bVar2 * 2 + 0x40) <
      *(ushort *)(DAT_004b3c8c + (uint)param_1 * 8 + (uint)bVar2 * 2 + 0x20)) {
    FUN_004b3416(param_1,bVar2);
  }
  if (*(ushort *)(iVar1 + (uint)param_1 * 8 + (uint)bVar3 * 2 + 0x40) <
      *(ushort *)(iVar1 + (uint)param_1 * 8 + (uint)bVar3 * 2 + 0x20)) {
    FUN_004b3416(param_1,bVar3);
  }
  if ((*(ushort *)(iVar1 + (uint)param_1 * 8 + (uint)bVar2 * 2 + 0x20) <=
       *(ushort *)(iVar1 + (uint)param_1 * 8 + (uint)bVar2 * 2 + 0x40)) &&
     (*(ushort *)(iVar1 + (uint)param_1 * 8 + (uint)bVar3 * 2 + 0x20) <=
      *(ushort *)(iVar1 + (uint)param_1 * 8 + (uint)bVar3 * 2 + 0x40))) {
    *(undefined1 *)(iVar1 + (uint)param_1 + 0x55) = 1;
  }
  return param_4;
}

