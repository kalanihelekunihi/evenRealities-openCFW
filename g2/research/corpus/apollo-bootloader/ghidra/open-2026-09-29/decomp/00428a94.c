
undefined4 spotmgr_transition_sequence_7b_428a94(void)

{
  uint *puVar1;
  uint *puVar2;
  undefined4 in_r3;
  uint uVar3;
  bool bVar4;
  
  *DAT_00428c84 = *DAT_00428c84 & 0xffffff80 | *DAT_00428c98 & 0x7f;
  puVar2 = DAT_00428ca0;
  *DAT_00428ca0 = *DAT_00428ca0 & 0xffffc3ff | (*DAT_00428c94 & 0xf) << 10;
  *puVar2 = *puVar2 & 0xfffffc00 | *DAT_00428c90 & 0x3ff;
  delay_us(5);
  *DAT_00428ba8 = *DAT_00428ba8 & 0xffffff80 | *DAT_00429520 & 0x7f;
  puVar2 = DAT_004291e0;
  if ((*DAT_004291e0 & 3) == 2) {
    *DAT_004291e0 = *DAT_004291e0 & 0xfffffffc | 1;
    uVar3 = 0;
    while ((uVar3 < 0x14 && ((*puVar2 & 7) >> 2 == 0))) {
      delay_us(1);
      uVar3 = uVar3 + 1;
    }
    bVar4 = true;
  }
  else {
    bVar4 = false;
  }
  puVar1 = DAT_00428c9c;
  *DAT_00428c9c = *DAT_00428c9c | 0x40;
  *puVar1 = *puVar1 | 8;
  *puVar1 = *puVar1 & 0xfdffffff;
  puVar1 = DAT_004291e4;
  if (bVar4) {
    bVar4 = -1 < (int)(*DAT_004291e4 << 0x1a);
    if (bVar4) {
      *DAT_004291e4 = *DAT_004291e4 | 0x20;
      delay_us(1);
      delay_status_change(0xf,DAT_004291e8,0x1000000,0x1000000);
    }
    if (*DAT_004291e8 << 7 < 0) {
      *puVar2 = *puVar2 & 0xfffffffc | 2;
      uVar3 = 0;
      while ((uVar3 < 0x14 && ((*puVar2 & 7) >> 2 == 0))) {
        delay_us(1);
        uVar3 = uVar3 + 1;
      }
    }
    if (bVar4) {
      *puVar1 = *puVar1 & 0xffffffdf;
    }
  }
  *DAT_00428c88 = 0x1a;
  return in_r3;
}

