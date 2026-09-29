
void AttsInit(void)

{
  int iVar1;
  byte bVar2;
  byte bVar3;
  int iVar4;
  
  iVar1 = DAT_00535448;
  *(undefined4 *)(DAT_00535448 + 600) = 0;
  *(undefined4 *)(iVar1 + 0x25c) = 0;
  *(undefined4 *)(iVar1 + 0x260) = DAT_0053547c;
  *(undefined4 *)(iVar1 + 0x264) = DAT_00535480;
  for (bVar2 = 0; bVar2 < 3; bVar2 = bVar2 + 1) {
    for (bVar3 = 0; bVar3 < 3; bVar3 = bVar3 + 1) {
      iVar4 = (uint)bVar3 * 0x40 + iVar1 + (uint)bVar2 * 0xc0;
      *(uint *)(iVar4 + 0x10) = DAT_00535464 + (uint)bVar2 * 0x14;
      *(byte *)(iVar4 + 0x24) = bVar2 + 1;
      *(byte *)(iVar4 + 0x25) = bVar3;
    }
  }
  *(undefined4 *)(DAT_00535464 + 0x40) = DAT_00535484;
  return;
}

