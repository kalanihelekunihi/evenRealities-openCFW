
undefined4 gx8002_audio_irq(void)

{
  int iVar1;
  uint uVar2;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  undefined4 uStack_14;
  
  iVar1 = iRam100260cc;
  uVar2 = 0;
  if (((uRam00000100 >> 0x12 & 1) != 0) && (uVar2 = 0, (uRam00000104 >> 0x12 & 1) != 0)) {
    uRam00000104 = 0x40000;
    uVar2 = 1;
  }
  if (((uRam00000100 >> 0x13 & 1) != 0) && ((uRam00000104 >> 0x13 & 1) != 0)) {
    uVar2 = uVar2 | 2;
    uRam00000104 = 0x80000;
  }
  if (((uRam00000100 >> 0x14 & 1) == 0) || ((uRam00000104 >> 0x14 & 1) == 0)) {
    if (uVar2 != 0) goto LAB_10025ee4;
  }
  else {
    uVar2 = uVar2 | 4;
    uRam00000104 = 0x100000;
LAB_10025ee4:
    if (*(uint *)(iRam100260cc + 0x14) != 0) {
      (*(code *)(*(uint *)(iRam100260cc + 0x14) & 0xfffffffe))(uVar2);
    }
  }
  func_0x102099cc(&uStack_1c,0,0xc);
  uVar2 = 0;
  if ((uRam00000100 & 1) != 0) {
    uVar2 = uRam00000104 & 1;
  }
  uStack_1c = uRam00000124;
  if (((uRam00000100 >> 1 & 1) != 0) && ((uRam00000104 >> 1 & 1) != 0)) {
    uVar2 = uVar2 | 2;
  }
  uStack_18 = uRam00000148;
  if (((uRam00000100 >> 2 & 1) != 0) && ((uRam00000104 >> 2 & 1) != 0)) {
    uVar2 = uVar2 | 4;
  }
  uStack_14 = uRam00000168;
  if (uVar2 != 0) {
    if (*(uint *)(iVar1 + 0xc) != 0) {
      (*(code *)(*(uint *)(iVar1 + 0xc) & 0xfffffffe))(uVar2,&uStack_1c);
    }
    if ((uVar2 & 1) != 0) {
      uRam00000104 = 1;
    }
    if ((uVar2 & 2) != 0) {
      uRam00000104 = 2;
    }
    if ((uVar2 & 4) != 0) {
      uRam00000104 = 4;
    }
  }
  func_0x102099cc(&uStack_1c,0,0xc);
  uVar2 = 0;
  if (((uRam00000100 >> 3 & 1) != 0) && (uVar2 = 0, (uRam00000104 >> 3 & 1) != 0)) {
    uStack_1c = uRam00000128;
    uVar2 = 1;
  }
  if (((uRam00000100 >> 4 & 1) != 0) && ((uRam00000104 >> 4 & 1) != 0)) {
    uVar2 = uVar2 | 2;
    uStack_18 = uRam0000014c;
  }
  if (((uRam00000100 >> 5 & 1) == 0) || ((uRam00000104 >> 5 & 1) == 0)) {
    if (uVar2 == 0) goto LAB_10026060;
  }
  else {
    uVar2 = uVar2 | 4;
    uStack_14 = uRam0000016c;
  }
  if (*(uint *)(iVar1 + 0x10) != 0) {
    (*(code *)(*(uint *)(iVar1 + 0x10) & 0xfffffffe))(uVar2,&uStack_1c);
  }
  if ((uVar2 & 1) != 0) {
    uRam00000104 = 8;
  }
  if ((uVar2 & 2) != 0) {
    uRam00000104 = 0x10;
  }
LAB_10026060:
  if ((uVar2 & 4) != 0) {
    uRam00000104 = 0x20;
  }
  uVar2 = 0;
  if (((uRam00000100 >> 0x10 & 1) != 0) && (uVar2 = 0, (uRam00000104 >> 0x10 & 1) != 0)) {
    uRam00000104 = 0x10000;
    uVar2 = 1;
  }
  if (((uRam00000100 >> 0x11 & 1) != 0) && ((uRam00000104 >> 0x11 & 1) != 0)) {
    uVar2 = uVar2 | 2;
    uRam00000104 = 0x20000;
  }
  if (*(uint *)(iVar1 + 0x18) != 0) {
    (*(code *)(*(uint *)(iVar1 + 0x18) & 0xfffffffe))(uVar2);
  }
  return 0;
}

