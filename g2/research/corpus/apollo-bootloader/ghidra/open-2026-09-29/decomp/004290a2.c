
ulonglong FUN_004290a2(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 uVar1;
  int iVar2;
  uint uVar3;
  uint *puVar4;
  uint uVar5;
  uint *puVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  
  puVar6 = (uint *)(DAT_00429624 + param_1 * 4 + 4);
  puVar4 = (uint *)(DAT_00429624 + 100);
  uVar1 = *(undefined1 *)puVar4;
  uVar7 = *puVar4;
  uVar8 = *puVar4;
  uVar5 = *puVar4;
  uVar9 = *(byte *)(DAT_00429624 + param_2 * 4 + 4) & 0x7f;
  uVar3 = *puVar6;
  uVar10 = *(byte *)puVar6 & 0x7f;
  if (*DAT_00429628 << 0x1f < 0) {
    uVar11 = 0;
    while ((uVar11 < 0x3c && (-1 < *DAT_00429700 << 1))) {
      delay_us(1);
      uVar11 = uVar11 + 1;
    }
    spotmgr_timer_irq_service_42a04a();
  }
  *DAT_00429704 = param_3;
  *DAT_00429708 = param_1;
  *DAT_0042970c = (*puVar6 & 0x1ffff) >> 7;
  *DAT_00429710 = (*puVar6 & 0x1fffff) >> 0x11;
  *DAT_00429714 = (uVar3 & 0xfffffff) >> 0x15;
  *DAT_00429520 = uVar10;
  if ((int)(uVar10 - uVar9) < 1) {
    iVar2 = 0;
  }
  else {
    iVar2 = (uVar10 - uVar9) * 2;
  }
  if (iVar2 + uVar9 < 0x80) {
    *DAT_00429da0 = *DAT_00429da0 & 0xffffff80 | iVar2 + uVar9 & 0x7f;
  }
  else {
    *DAT_00429da0 = *DAT_00429da0 | 0x7f;
  }
  puVar4 = DAT_00429a28;
  *DAT_00429a28 = *DAT_00429a28 & 0xffffc3ff | ((*puVar6 & 0x1fffff) >> 0x11) << 10;
  *puVar4 = (*puVar6 & 0x1ffff) >> 7 | *puVar4 & 0xfffffc00;
  delay_us(0x32);
  *DAT_00429da0 = uVar10 | *DAT_00429da0 & 0xffffff80;
  return CONCAT44(param_4,CONCAT13((char)(uVar5 >> 0x15),
                                   CONCAT12((char)(uVar8 >> 0xe),CONCAT11((char)(uVar7 >> 7),uVar1))
                                  )) & 0xffffffff7f7f7f7f;
}

