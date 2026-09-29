
undefined8 AttsCccInitTable(undefined1 param_1,short *param_2,undefined4 param_3)

{
  int iVar1;
  short *psVar2;
  byte bVar3;
  short *psVar4;
  
  psVar4 = param_2;
  iVar1 = FUN_004c9c50();
  if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052c688,&DAT_0052c3c8,3), iVar1 != 0)) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052c688,DAT_0052c678,4), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052c688,DAT_0052c688,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if (iVar1 == 0) {
          iVar1 = FUN_004c9c50();
          if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&LAB_0052c3cc,&DAT_0052c3c4,3), iVar1 != 0)) {
            WsfTrace(DAT_0052c688,DAT_0052c6ac,param_1);
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            psVar4 = (short *)0x160;
            param_3 = DAT_0052c6ac;
            FUN_0043d574(4,&LAB_0052c3cc,DAT_0052c684,DAT_0052c6b0,0x160,DAT_0052c6ac,param_1);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          psVar4 = (short *)0x160;
          param_3 = DAT_0052c6ac;
          FUN_0043d574(3,&LAB_0052c3cc,DAT_0052c684,DAT_0052c6b0,0x160,DAT_0052c6ac,param_1);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        psVar4 = (short *)0x160;
        param_3 = DAT_0052c6ac;
        FUN_0043d574(2,&LAB_0052c3cc,DAT_0052c684,DAT_0052c6b0,0x160,DAT_0052c6ac,param_1);
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      psVar4 = (short *)0x160;
      param_3 = DAT_0052c6ac;
      FUN_0043d574(1,&LAB_0052c3cc,DAT_0052c684,DAT_0052c6b0,0x160,DAT_0052c6ac,param_1);
    }
  }
  psVar2 = (short *)attsCccAllocTbl(param_1);
  if (psVar2 != (short *)0x0) {
    if (param_2 == (short *)0x0) {
      FUN_0043c0e4(psVar2,(uint)*(byte *)(DAT_0052c674 + 0x14) << 1,0);
    }
    else {
      for (bVar3 = 0; bVar3 < *(byte *)(DAT_0052c674 + 0x14); bVar3 = bVar3 + 1) {
        *psVar2 = *param_2;
        if (*param_2 != 0) {
          attsCccCback(param_1,bVar3,0,*param_2);
        }
        param_2 = param_2 + 1;
        psVar2 = psVar2 + 1;
      }
    }
  }
  return CONCAT44(param_3,psVar4);
}

