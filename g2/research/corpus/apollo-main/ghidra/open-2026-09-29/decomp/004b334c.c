
void FUN_004b334c(byte param_1)

{
  int iVar1;
  byte bVar2;
  byte bVar3;
  bool bVar4;
  bool bVar5;
  
  iVar1 = DAT_004b3c8c;
  bVar3 = *(char *)(DAT_004b3c8c + 0x5d) << 1;
  bVar2 = *(char *)(DAT_004b3c8c + 0x5d) * '\x02' + 1;
  bVar4 = *(short *)(DAT_004b3c8c + (uint)param_1 * 8 + (uint)bVar3 * 2 + 0x40) != 0;
  if (bVar4) {
    *(undefined2 *)(DAT_004b3c8c + (uint)param_1 * 8 + (uint)bVar3 * 2 + 0x40) = 0;
  }
  bVar5 = *(short *)(iVar1 + (uint)param_1 * 8 + (uint)bVar2 * 2 + 0x40) != 0;
  if (bVar5) {
    *(undefined2 *)(iVar1 + (uint)param_1 * 8 + (uint)bVar2 * 2 + 0x40) = 0;
  }
  if (bVar5 || bVar4) {
    *(undefined1 *)((uint)param_1 + iVar1 + 0x55) = 0;
  }
  return;
}

