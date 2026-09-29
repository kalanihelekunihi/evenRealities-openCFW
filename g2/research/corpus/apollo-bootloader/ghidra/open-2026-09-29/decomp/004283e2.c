
ulonglong FUN_004283e2(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

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
  
  puVar6 = (uint *)(DAT_00428a78 + param_1 * 4 + 4);
  puVar4 = (uint *)(DAT_00428a78 + 100);
  uVar1 = *(undefined1 *)puVar4;
  uVar7 = *puVar4;
  uVar8 = *puVar4;
  uVar5 = *puVar4;
  uVar9 = *(byte *)(DAT_00428a78 + param_2 * 4 + 4) & 0x7f;
  uVar3 = *puVar6;
  uVar10 = *(byte *)puVar6 & 0x7f;
  if (*DAT_00428a7c << 0x1f < 0) {
    uVar11 = 0;
    while ((uVar11 < 0x3c && (-1 < *DAT_00428a84 << 1))) {
      delay_us(1);
      uVar11 = uVar11 + 1;
    }
    spotmgr_timer_irq_service_42a04a();
  }
  *DAT_00428a88 = param_3;
  *DAT_00428a8c = param_1;
  *DAT_00428c90 = (*puVar6 & 0x1ffff) >> 7;
  *DAT_00428c94 = (*puVar6 & 0x1fffff) >> 0x11;
  *DAT_00428c98 = (uVar3 & 0xfffffff) >> 0x15;
  *DAT_00428a90 = uVar10;
  spotmgr_power_ton_adjust_42a1bc(param_3,param_1);
  if ((int)(uVar10 - uVar9) < 1) {
    iVar2 = 0;
  }
  else {
    iVar2 = (uVar10 - uVar9) * 2;
  }
  if (iVar2 + uVar9 < 0x80) {
    *DAT_00428ba8 = *DAT_00428ba8 & 0xffffff80 | iVar2 + uVar9 & 0x7f;
  }
  else {
    *DAT_00428ba8 = *DAT_00428ba8 | 0x7f;
  }
  delay_us(0x32);
  *DAT_00428ba8 = uVar10 | *DAT_00428ba8 & 0xffffff80;
  return CONCAT44(param_4,CONCAT13((char)(uVar5 >> 0x15),
                                   CONCAT12((char)(uVar8 >> 0xe),CONCAT11((char)(uVar7 >> 7),uVar1))
                                  )) & 0xffffffff7f7f7f7f;
}

