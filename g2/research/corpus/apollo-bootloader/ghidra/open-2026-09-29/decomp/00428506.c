
uint FUN_00428506(int param_1,undefined4 param_2,undefined4 param_3)

{
  byte bVar1;
  uint *puVar2;
  uint *puVar3;
  uint uVar4;
  uint uVar5;
  undefined4 local_20;
  
  puVar3 = (uint *)(DAT_00428a78 + param_1 * 4 + 4);
  puVar2 = (uint *)(DAT_00428a78 + 100);
  local_20 = CONCAT13((char)(*puVar2 >> 0x15),
                      CONCAT12((char)(*puVar2 >> 0xe),
                               CONCAT11((char)(*puVar2 >> 7),*(undefined1 *)puVar2))) & 0x7f7f7f7f;
  uVar4 = (*puVar3 & 0xfffffff) >> 0x15;
  bVar1 = *(byte *)puVar3;
  if (*DAT_00428a7c << 0x1f < 0) {
    uVar5 = 0;
    while ((uVar5 < 0x3c && (-1 < *DAT_00428a84 << 1))) {
      delay_us(1);
      uVar5 = uVar5 + 1;
    }
    spotmgr_timer_irq_service_42a04a();
  }
  *DAT_00428a88 = param_3;
  *DAT_00428a8c = param_1;
  *DAT_00428c90 = (*puVar3 & 0x1ffff) >> 7;
  *DAT_00428c94 = (*puVar3 & 0x1fffff) >> 0x11;
  *DAT_00428c98 = uVar4;
  *DAT_00428a90 = bVar1 & 0x7f;
  puVar2 = DAT_00428ca0;
  *DAT_00428ca0 = *DAT_00428ca0 & 0xffffc3ff | ((*puVar3 & 0x1fffff) >> 0x11) << 10;
  *puVar2 = (*puVar3 & 0x1ffff) >> 7 | *puVar2 & 0xfffffc00;
  *DAT_00428c84 = uVar4 | *DAT_00428c84 & 0xffffff80;
  *DAT_00428ba8 = bVar1 & 0x7f | *DAT_00428ba8 & 0xffffff80;
  spotmgr_power_ton_adjust_42a1bc(param_3,param_1);
  puVar2 = DAT_00428c9c;
  *DAT_00428c9c = *DAT_00428c9c & 0xfffffff7;
  *puVar2 = *puVar2 & 0xffffffbf;
  *puVar2 = *puVar2 & 0xfffeffff;
  return local_20;
}

