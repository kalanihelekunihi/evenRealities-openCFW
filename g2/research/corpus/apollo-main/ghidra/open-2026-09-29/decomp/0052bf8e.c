
undefined8 attsCccReadValue(undefined1 param_1,short param_2,undefined1 *param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  short *psVar3;
  byte bVar4;
  
  bVar4 = 0;
  for (psVar3 = *(short **)(DAT_0052c674 + 0xc);
      (bVar4 < *(byte *)(DAT_0052c674 + 0x14) && (*psVar3 != param_2)); psVar3 = psVar3 + 3) {
    bVar4 = bVar4 + 1;
  }
  if (bVar4 == *(byte *)(DAT_0052c674 + 0x14)) {
    uVar1 = 10;
  }
  else {
    iVar2 = attsCccGetTbl(param_1);
    if (iVar2 == 0) {
      uVar1 = 0x11;
    }
    else {
      *param_3 = (char)*(undefined2 *)(iVar2 + (uint)bVar4 * 2);
      param_3[1] = (char)((ushort)*(undefined2 *)(iVar2 + (uint)bVar4 * 2) >> 8);
      uVar1 = 0;
    }
  }
  return CONCAT44(param_4,uVar1);
}

