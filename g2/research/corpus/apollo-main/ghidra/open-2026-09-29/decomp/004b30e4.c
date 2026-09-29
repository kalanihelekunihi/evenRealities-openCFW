
void dmAdvInit(void)

{
  int iVar1;
  byte bVar2;
  
  for (bVar2 = 0; iVar1 = DAT_004b32d0, bVar2 < 2; bVar2 = bVar2 + 1) {
    dmAdvCbInit(bVar2);
  }
  *(undefined1 *)(DAT_004b32cc + 0xc) = *(undefined1 *)(DAT_004b32d0 + 0xc);
  *(undefined1 *)(iVar1 + 0xe) = 0;
  return;
}

