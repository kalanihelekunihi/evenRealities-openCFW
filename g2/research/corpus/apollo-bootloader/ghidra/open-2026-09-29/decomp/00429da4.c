
void spotmgr_load_factory_trims_429da4(void)

{
  int iVar1;
  uint *puVar2;
  int *piVar3;
  
  piVar3 = DAT_0042a868;
  puVar2 = DAT_0042a548;
  iVar1 = DAT_0042a084;
  *DAT_0042a548 =
       *DAT_0042a548 & 0xffffc3ff |
       (*(uint *)(DAT_0042a084 + *DAT_0042a868 * 4 + 4) >> 0x11 & 0xf) << 10;
  *puVar2 = *puVar2 & 0xfffffc00 | *(uint *)(iVar1 + *piVar3 * 4 + 4) >> 7 & 0x3ff;
  *DAT_0042a86c = *DAT_0042a86c & 0xffffff80 | *(uint *)(iVar1 + *piVar3 * 4 + 4) >> 0x15 & 0x7f;
  *DAT_0042a54c = 0;
  return;
}

