
uint FUN_0042863e(int param_1,undefined4 param_2,undefined4 param_3)

{
  byte bVar1;
  uint *puVar2;
  uint *puVar3;
  uint *puVar4;
  uint uVar5;
  uint uVar6;
  bool bVar7;
  uint local_20;
  
  puVar4 = (uint *)(DAT_00428a78 + param_1 * 4 + 4);
  puVar3 = (uint *)(DAT_00428a78 + 100);
  local_20 = CONCAT13((char)(*puVar3 >> 0x15),
                      CONCAT12((char)(*puVar3 >> 0xe),
                               CONCAT11((char)(*puVar3 >> 7),*(undefined1 *)puVar3))) & 0x7f7f7f7f;
  uVar5 = (*puVar4 & 0xfffffff) >> 0x15;
  bVar1 = *(byte *)puVar4;
  if (*DAT_00428a7c << 0x1f < 0) {
    if (param_1 == *DAT_00428a80) {
      spotmgr_power_ton_adjust_42a1bc(param_3,param_1);
      *DAT_00428c84 = uVar5 | *DAT_00428c84 & 0xffffff80;
      FUN_0041ccd6();
      *DAT_00428c88 = 0x1a;
      return local_20;
    }
    if (*DAT_00428a7c << 0x1f < 0) {
      uVar6 = 0;
      while ((uVar6 < 0x3c && (-1 < *DAT_00428a84 << 1))) {
        delay_us(1);
        uVar6 = uVar6 + 1;
      }
      spotmgr_timer_irq_service_42a04a();
    }
  }
  *DAT_00428a88 = param_3;
  *DAT_00428a8c = param_1;
  *DAT_00428c90 = (*puVar4 & 0x1ffff) >> 7;
  *DAT_00428c94 = (*puVar4 & 0x1fffff) >> 0x11;
  *DAT_00428c98 = uVar5;
  *DAT_00428a90 = bVar1 & 0x7f;
  spotmgr_power_ton_adjust_42a1bc(param_3,param_1);
  puVar3 = DAT_004291e0;
  *DAT_004291e0 = *DAT_004291e0 & 0xfffffffc | 1;
  uVar6 = 0;
  while ((puVar2 = DAT_00428c9c, uVar6 < 0x14 && ((*puVar3 & 7) >> 2 == 0))) {
    delay_us(1);
    uVar6 = uVar6 + 1;
  }
  *DAT_00428c9c = *DAT_00428c9c & 0xfffffff7;
  *puVar2 = *puVar2 & 0xffffffbf;
  *puVar2 = *puVar2 | 0x2000000;
  puVar2 = DAT_004291e4;
  bVar7 = -1 < (int)(*DAT_004291e4 << 0x1a);
  if (bVar7) {
    *DAT_004291e4 = *DAT_004291e4 | 0x20;
    delay_us(1);
    delay_status_change(0xf,DAT_004291e8,0x1000000,0x1000000);
  }
  if (*DAT_004291e8 << 7 < 0) {
    *puVar3 = *puVar3 & 0xfffffffc | 2;
    uVar6 = 0;
    while ((uVar6 < 0x14 && ((*puVar3 & 7) >> 2 == 0))) {
      delay_us(1);
      uVar6 = uVar6 + 1;
    }
  }
  if (bVar7) {
    *puVar2 = *puVar2 & 0xffffffdf;
  }
  puVar3 = DAT_00428ca0;
  *DAT_00428ca0 = *DAT_00428ca0 & 0xffffc3ff | ((*puVar4 & 0x1fffff) >> 0x11) << 10;
  *puVar3 = (*puVar4 & 0x1ffff) >> 7 | *puVar3 & 0xfffffc00;
  *DAT_00428c84 = uVar5 | *DAT_00428c84 & 0xffffff80;
  return local_20;
}

