
undefined4 FUN_0042f4b2(char param_1,char param_2)

{
  uint *puVar1;
  uint *puVar2;
  uint uVar3;
  byte bVar4;
  bool bVar5;
  bool bVar6;
  
  puVar1 = DAT_0042f5f0;
  bVar4 = 0;
  uVar3 = *DAT_0042f5f0;
  if ((uVar3 & 1) != 0) {
    FUN_0041c838(0);
    delay_us(5);
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
  bVar5 = *(char *)(DAT_0042f668 + (uint)bVar4 * 3 + 1) != '\x01';
  bVar6 = *(char *)(DAT_0042f668 + (uint)bVar4 * 3 + 2) != '\x01';
  *DAT_0042f66c = *DAT_0042f66c | 0x80000000;
  puVar2 = DAT_0042f640;
  if (bVar5) {
    bVar4 = *DAT_0042f648;
  }
  else {
    bVar4 = *DAT_0042f644;
  }
  *DAT_0042f640 = *DAT_0042f640 & 0xc1ffffff | (bVar4 & 0x1f) << 0x19;
  if (bVar6) {
    bVar4 = *DAT_0042f648;
  }
  else {
    bVar4 = *DAT_0042f644;
  }
  *puVar2 = *puVar2 & 0xffff07ff | (bVar4 & 0x1f) << 0xb;
  if (bVar5) {
    bVar4 = *DAT_0042f658;
  }
  else {
    bVar4 = *DAT_0042f650;
  }
  *DAT_0042f64c = *DAT_0042f64c & 0xffffe0ff | (bVar4 & 0x1f) << 8;
  if (bVar6) {
    bVar4 = *DAT_0042f658;
  }
  else {
    bVar4 = *DAT_0042f650;
  }
  *DAT_0042f654 = *DAT_0042f654 & 0xffc1ffff | (bVar4 & 0x1f) << 0x11;
  puVar2 = DAT_0042f65c;
  if (bVar5) {
    bVar4 = *DAT_0042f664;
  }
  else {
    bVar4 = *DAT_0042f660;
  }
  *DAT_0042f65c = *DAT_0042f65c & 0xc1ffffff | (bVar4 & 0x1f) << 0x19;
  if (bVar6) {
    bVar4 = *DAT_0042f664;
  }
  else {
    bVar4 = *DAT_0042f660;
  }
  *puVar2 = *puVar2 & 0xffff07ff | (bVar4 & 0x1f) << 0xb;
  if ((uVar3 & 1) != 0) {
    *puVar1 = *puVar1 | 1;
    delay_us(5);
    FUN_0041c838(1);
  }
  return 0;
}

