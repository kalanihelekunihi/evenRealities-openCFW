
ulonglong FUN_0042984e(uint param_1,uint param_2,undefined4 param_3)

{
  byte bVar1;
  uint *puVar2;
  int iVar3;
  int iVar4;
  uint *puVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  uint local_28;
  
  iVar4 = DAT_0042a084;
  puVar2 = (uint *)(DAT_0042a084 + param_1 * 4 + 4);
  puVar5 = (uint *)(DAT_0042a084 + 100);
  local_28 = CONCAT13((char)(*puVar5 >> 0x15),
                      CONCAT12((char)(*puVar5 >> 0xe),
                               CONCAT11((char)(*puVar5 >> 7),*(undefined1 *)puVar5))) & 0x7f7f7f7f;
  uVar6 = (*(uint *)(DAT_0042a084 + param_2 * 4 + 4) & 0xfffffff) >> 0x15;
  uVar7 = (*puVar2 & 0xfffffff) >> 0x15;
  uVar8 = *(byte *)puVar2 & 0x7f;
  uVar9 = (uint)*(byte *)((int)&local_28 + (param_2 & 3));
  bVar1 = *(byte *)((int)&local_28 + (param_1 & 3));
  if (*DAT_0042a088 << 0x1f < 0) {
    uVar10 = 0;
    while ((uVar10 < 0x3c && (-1 < *DAT_0042a1b4 << 1))) {
      delay_us(1);
      uVar10 = uVar10 + 1;
    }
    spotmgr_timer_irq_service_42a04a();
  }
  *DAT_0042a1b8 = param_3;
  *DAT_0042a2a4 = param_1;
  *DAT_0042a2a8 = (*puVar2 & 0x1ffff) >> 7;
  *DAT_0042a2ac = (*puVar2 & 0x1fffff) >> 0x11;
  *DAT_0042a2b0 = uVar7;
  *DAT_0042a07c = uVar8;
  iVar3 = bVar1 - uVar9;
  if (iVar3 < 1) {
    iVar3 = 0;
  }
  else {
    iVar3 = iVar3 * 2;
  }
  if (iVar3 + uVar9 < 0x80) {
    *DAT_0042a080 = *DAT_0042a080 & 0xffffff80 | iVar3 + uVar9 & 0x7f;
  }
  else {
    *DAT_0042a080 = *DAT_0042a080 | 0x7f;
  }
  iVar4 = ((*(byte *)(iVar4 + 4) & 0x7f) - uVar8) * 2;
  if (iVar4 + uVar8 < 0x80) {
    *DAT_00429a20 = *DAT_00429a20 & 0xffffff80 | iVar4 + uVar8 & 0x7f;
  }
  else {
    *DAT_00429a20 = *DAT_00429a20 | 0x7f;
  }
  if ((int)(uVar7 - uVar6) < 1) {
    iVar4 = 0;
  }
  else {
    iVar4 = (uVar7 - uVar6) * 2;
  }
  if (iVar4 + uVar6 < 0x80) {
    *DAT_00429a2c = *DAT_00429a2c & 0xffffff80 | iVar4 + uVar6 & 0x7f;
  }
  else {
    *DAT_00429a2c = *DAT_00429a2c | 0x7f;
  }
  delay_us(0x32);
  *DAT_00429a2c = uVar7 | *DAT_00429a2c & 0xffffff80;
  puVar5 = DAT_00429a28;
  *DAT_00429a28 = *DAT_00429a28 & 0xffffc3ff | ((*puVar2 & 0x1fffff) >> 0x11) << 10;
  *puVar5 = (*puVar2 & 0x1ffff) >> 7 | *puVar5 & 0xfffffc00;
  delay_us(5);
  *DAT_00429a20 = uVar8 | *DAT_00429a20 & 0xffffff80;
  *DAT_0042a080 = *DAT_0042a080 & 0xffffff80 | bVar1 & 0x7f;
  return (ulonglong)CONCAT14(bVar1,puVar2);
}

