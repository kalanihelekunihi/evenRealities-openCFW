
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void AttsIndInit(void)

{
  int iVar1;
  byte bVar2;
  byte bVar3;
  
  for (bVar2 = 0; bVar2 < 3; bVar2 = bVar2 + 1) {
    for (bVar3 = 0; bVar3 < 3; bVar3 = bVar3 + 1) {
      iVar1 = DAT_00533e98 + (uint)bVar2 * 0xc0 + (uint)bVar3 * 0x40;
      *(undefined1 *)(iVar1 + 0xc) = *(undefined1 *)(DAT_00533eb0 + 0x60);
      *(ushort *)(iVar1 + 8) = bVar2 + 1;
    }
  }
  *(undefined4 *)(DAT_00533e98 + 0x260) = _DAT_00533eb8;
  return;
}

