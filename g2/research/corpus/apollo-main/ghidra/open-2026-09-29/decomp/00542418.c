
undefined8 SmpDbSetFailureCount(uint param_1,uint param_2)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  
  uVar3 = param_1;
  uVar4 = param_2;
  iVar1 = smpDbGetRecord(param_1 & 0xff);
  iVar2 = FUN_004c9c50();
  if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_005429f8,&DAT_00542570,3), iVar2 != 0)) {
    iVar2 = FUN_004c9c50();
    if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_005429f8,DAT_0054295c,4), iVar2 != 0)) {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_005429f8,DAT_005429f8,4), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if (iVar2 == 0) {
          iVar2 = FUN_004c9c50();
          if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_00542574,&LAB_00542578,3), iVar2 != 0)) {
            WsfTrace(DAT_005429f8,DAT_00542a20,param_1 & 0xff,param_2 & 0xff);
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            uVar3 = 0xf7;
            uVar4 = DAT_00542a20;
            FUN_0043d574(4,&DAT_00542574,DAT_00542958,DAT_00542a24,0xf7,DAT_00542a20,param_1 & 0xff,
                         param_2 & 0xff);
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          uVar3 = 0xf7;
          uVar4 = DAT_00542a20;
          FUN_0043d574(3,&DAT_00542574,DAT_00542958,DAT_00542a24,0xf7,DAT_00542a20,param_1 & 0xff,
                       param_2 & 0xff);
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        uVar3 = 0xf7;
        uVar4 = DAT_00542a20;
        FUN_0043d574(2,&DAT_00542574,DAT_00542958,DAT_00542a24,0xf7,DAT_00542a20,param_1 & 0xff,
                     param_2 & 0xff);
      }
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uVar3 = 0xf7;
      uVar4 = DAT_00542a20;
      FUN_0043d574(1,&DAT_00542574,DAT_00542958,DAT_00542a24,0xf7,DAT_00542a20,param_1 & 0xff,
                   param_2 & 0xff);
    }
  }
  *(char *)(iVar1 + 7) = (char)param_2;
  if ((param_2 & 0xff) != 0) {
    *(undefined4 *)(iVar1 + 0x14) = *(undefined4 *)(*DAT_00542a28 + 0xc);
  }
  return CONCAT44(uVar4,uVar3);
}

