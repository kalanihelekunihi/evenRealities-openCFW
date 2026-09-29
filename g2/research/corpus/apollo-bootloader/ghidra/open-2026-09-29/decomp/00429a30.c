
uint FUN_00429a30(uint param_1,uint param_2,undefined4 param_3)

{
  byte bVar1;
  int iVar2;
  uint uVar3;
  uint *puVar4;
  uint *puVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint local_28;
  
  puVar5 = (uint *)(DAT_0042a084 + param_1 * 4 + 4);
  puVar4 = (uint *)(DAT_0042a084 + 100);
  local_28 = CONCAT13((char)(*puVar4 >> 0x15),
                      CONCAT12((char)(*puVar4 >> 0xe),
                               CONCAT11((char)(*puVar4 >> 7),*(undefined1 *)puVar4))) & 0x7f7f7f7f;
  uVar3 = *puVar5;
  bVar1 = *(byte *)puVar5;
  uVar6 = (uint)*(byte *)((int)&local_28 + (param_2 & 3));
  uVar7 = (uint)*(byte *)((int)&local_28 + (param_1 & 3));
  if (*DAT_0042a088 << 0x1f < 0) {
    uVar8 = 0;
    while ((uVar8 < 0x3c && (-1 < *DAT_0042a1b4 << 1))) {
      delay_us(1);
      uVar8 = uVar8 + 1;
    }
    spotmgr_timer_irq_service_42a04a();
  }
  *DAT_0042a1b8 = param_3;
  *DAT_0042a2a4 = param_1;
  *DAT_0042a2a8 = (*puVar5 & 0x1ffff) >> 7;
  *DAT_0042a2ac = (*puVar5 & 0x1fffff) >> 0x11;
  *DAT_0042a2b0 = (uVar3 & 0xfffffff) >> 0x15;
  *DAT_0042a07c = bVar1 & 0x7f;
  iVar2 = uVar7 - uVar6;
  if (iVar2 < 1) {
    iVar2 = 0;
  }
  else {
    iVar2 = iVar2 * 2;
  }
  if (iVar2 + uVar6 < 0x80) {
    *DAT_0042a080 = *DAT_0042a080 & 0xffffff80 | iVar2 + uVar6 & 0x7f;
  }
  else {
    *DAT_0042a080 = *DAT_0042a080 | 0x7f;
  }
  delay_us(0x32);
  *DAT_0042a080 = *DAT_0042a080 & 0xffffff80 | uVar7 & 0x7f;
  return local_28;
}

