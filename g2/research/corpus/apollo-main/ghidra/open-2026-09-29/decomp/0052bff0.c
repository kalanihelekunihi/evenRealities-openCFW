
undefined8 attsCccWriteValue(undefined1 param_1,short param_2,byte *param_3,undefined4 param_4)

{
  ushort uVar1;
  short *psVar2;
  undefined4 uVar3;
  int iVar4;
  byte bVar5;
  ushort uVar6;
  
  bVar5 = 0;
  for (psVar2 = *(short **)(DAT_0052c674 + 0xc);
      (bVar5 < *(byte *)(DAT_0052c674 + 0x14) && (*psVar2 != param_2)); psVar2 = psVar2 + 3) {
    bVar5 = bVar5 + 1;
  }
  if (bVar5 == *(byte *)(DAT_0052c674 + 0x14)) {
    uVar3 = 10;
  }
  else {
    uVar6 = (ushort)param_3[1] * 0x100 + (ushort)*param_3;
    if ((((uVar6 == 0) || (uVar6 == 1)) || (uVar6 == 2)) &&
       ((uVar6 == 0 || ((uVar6 & psVar2[1]) != 0)))) {
      iVar4 = attsCccGetTbl(param_1);
      if (iVar4 == 0) {
        uVar3 = 0x11;
      }
      else {
        uVar1 = *(ushort *)(iVar4 + (uint)bVar5 * 2);
        *(ushort *)(iVar4 + (uint)bVar5 * 2) = uVar6;
        if (uVar1 != uVar6) {
          attsCccCback(param_1,bVar5,param_2,uVar6);
        }
        uVar3 = 0;
      }
    }
    else {
      uVar3 = 0x80;
    }
  }
  return CONCAT44(param_4,uVar3);
}

