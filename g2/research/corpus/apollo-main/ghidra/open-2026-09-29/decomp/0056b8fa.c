
undefined8 attcDiscProcDescPair(int *param_1,uint param_2,byte *param_3)

{
  int iVar1;
  short sVar2;
  byte *pbVar3;
  byte bVar4;
  int *piVar5;
  uint uVar6;
  
  sVar2 = (ushort)param_3[1] * 0x100 + (ushort)*param_3;
  pbVar3 = param_3 + 2;
  piVar5 = (int *)(*param_1 + (uint)*(byte *)((int)param_1 + 0x12) * 4);
  bVar4 = *(byte *)((int)param_1 + 0x12);
  uVar6 = param_2;
  while( true ) {
    if ((*(byte *)(param_1 + 3) <= bVar4) || (-1 < (int)((uint)*(byte *)(*piVar5 + 4) << 0x1d)))
    goto LAB_0056ba7e;
    if ((*(short *)(param_1[1] + (uint)bVar4 * 2) == 0) &&
       (iVar1 = attcUuidCmp(*piVar5,pbVar3,param_2 & 0xff), iVar1 != 0)) break;
    bVar4 = bVar4 + 1;
    piVar5 = piVar5 + 1;
  }
  *(short *)(param_1[1] + (uint)bVar4 * 2) = sVar2;
  iVar1 = FUN_004c9c50();
  if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0056c1e8,&DAT_0056bc14,3), iVar1 != 0)) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0056c1e8,DAT_0056c34c,4), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0056c1e8,DAT_0056c1e8,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if (iVar1 == 0) {
          iVar1 = FUN_004c9c50();
          if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_0056bc18,&DAT_0056bcfc,3), iVar1 != 0)) {
            WsfTrace(DAT_0056c1e8,DAT_0056c1ec,sVar2);
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            uVar6 = 0xee;
            param_3 = DAT_0056c1ec;
            FUN_0043d574(4,&DAT_0056bc18,DAT_0056c1f4,DAT_0056c1f0,0xee,DAT_0056c1ec,sVar2);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          uVar6 = 0xee;
          param_3 = DAT_0056c1ec;
          FUN_0043d574(3,&DAT_0056bc18,DAT_0056c1f4,DAT_0056c1f0,0xee,DAT_0056c1ec,sVar2);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar6 = 0xee;
        param_3 = DAT_0056c1ec;
        FUN_0043d574(2,&DAT_0056bc18,DAT_0056c1f4,DAT_0056c1f0,0xee,DAT_0056c1ec,sVar2);
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar6 = 0xee;
      param_3 = DAT_0056c1ec;
      FUN_0043d574(1,&DAT_0056bc18,DAT_0056c1f4,DAT_0056c1f0,0xee,DAT_0056c1ec,sVar2);
    }
  }
LAB_0056ba7e:
  return CONCAT44(param_3,uVar6);
}

