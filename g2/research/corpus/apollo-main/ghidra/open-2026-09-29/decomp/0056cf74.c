
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void SmpScInit(void)

{
  int iVar1;
  byte bVar2;
  
  for (bVar2 = 0; iVar1 = DAT_0056d81c, bVar2 < 3; bVar2 = bVar2 + 1) {
    *(uint *)(DAT_0056d81c + (uint)bVar2 * 0x4c + 0x48) = _DAT_0056d820 + (uint)bVar2 * 0x1c;
  }
  *(undefined4 *)(DAT_0056d81c + 0xf0) = _DAT_0056d824;
  *(undefined4 *)(iVar1 + 0xf4) = _DAT_0056d828;
  *(undefined1 *)(iVar1 + 0xf8) = 1;
  return;
}

