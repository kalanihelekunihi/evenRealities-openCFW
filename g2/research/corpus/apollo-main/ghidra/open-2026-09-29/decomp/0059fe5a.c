
undefined4 FUN_0059fe5a(char param_1,char param_2)

{
  uint *puVar1;
  uint *puVar2;
  uint uVar3;
  byte bVar4;
  bool bVar5;
  bool bVar6;
  
  puVar1 = DAT_0059ff98;
  bVar4 = 0;
  uVar3 = *DAT_0059ff98;
  if ((uVar3 & 1) != 0) {
    FUN_0047fe6c(0);
    FUN_004807a0(5);
    *puVar1 = *puVar1 & 0xfffffffe;
  }
  if (param_1 != '\0') {
    if (param_2 == '\0') {
      bVar4 = 1;
    }
    else {
      bVar4 = 2;
    }
  }
  bVar5 = *(char *)(DAT_005a0010 + (uint)bVar4 * 3 + 1) != '\x01';
  bVar6 = *(char *)(DAT_005a0010 + (uint)bVar4 * 3 + 2) != '\x01';
  *DAT_005a0014 = *DAT_005a0014 | 0x80000000;
  puVar2 = DAT_0059ffe8;
  if (bVar5) {
    bVar4 = *DAT_0059fff0;
  }
  else {
    bVar4 = *DAT_0059ffec;
  }
  *DAT_0059ffe8 = *DAT_0059ffe8 & 0xc1ffffff | (bVar4 & 0x1f) << 0x19;
  if (bVar6) {
    bVar4 = *DAT_0059fff0;
  }
  else {
    bVar4 = *DAT_0059ffec;
  }
  *puVar2 = *puVar2 & 0xffff07ff | (bVar4 & 0x1f) << 0xb;
  if (bVar5) {
    bVar4 = *DAT_005a0000;
  }
  else {
    bVar4 = *DAT_0059fff8;
  }
  *DAT_0059fff4 = *DAT_0059fff4 & 0xffffe0ff | (bVar4 & 0x1f) << 8;
  if (bVar6) {
    bVar4 = *DAT_005a0000;
  }
  else {
    bVar4 = *DAT_0059fff8;
  }
  *DAT_0059fffc = *DAT_0059fffc & 0xffc1ffff | (bVar4 & 0x1f) << 0x11;
  puVar2 = DAT_005a0004;
  if (bVar5) {
    bVar4 = *DAT_005a000c;
  }
  else {
    bVar4 = *DAT_005a0008;
  }
  *DAT_005a0004 = *DAT_005a0004 & 0xc1ffffff | (bVar4 & 0x1f) << 0x19;
  if (bVar6) {
    bVar4 = *DAT_005a000c;
  }
  else {
    bVar4 = *DAT_005a0008;
  }
  *puVar2 = *puVar2 & 0xffff07ff | (bVar4 & 0x1f) << 0xb;
  if ((uVar3 & 1) != 0) {
    *puVar1 = *puVar1 | 1;
    FUN_004807a0(5);
    FUN_0047fe6c(1);
  }
  return 0;
}

