
undefined8 DmConnSetIdle(uint param_1,undefined4 param_2,char param_3)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  
  uVar2 = param_1;
  uVar3 = param_2;
  WsfTaskLock();
  iVar1 = DmConnInUse(param_1 & 0xff);
  if (iVar1 != 0) {
    if (param_3 == '\0') {
      *(ushort *)((param_1 & 0xff) * 0x30 + DAT_004b7430 + -0x22) =
           *(ushort *)((param_1 & 0xff) * 0x30 + DAT_004b7430 + -0x22) & ~(ushort)param_2;
    }
    else {
      *(ushort *)((param_1 & 0xff) * 0x30 + DAT_004b7430 + -0x22) =
           (ushort)param_2 | *(ushort *)((param_1 & 0xff) * 0x30 + DAT_004b7430 + -0x22);
    }
  }
  WsfTaskUnlock();
  iVar1 = FUN_004c9c50();
  if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_004b7464,&DAT_004b7428,3), iVar1 != 0)) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_004b7464,DAT_004b7454,4), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_004b7464,DAT_004b7464,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if (iVar1 == 0) {
          iVar1 = FUN_004c9c50();
          if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_004b742c,&DAT_004b7434,3), iVar1 != 0)) {
            WsfTrace(DAT_004b7464,DAT_004b7470,param_1 & 0xff,
                     *(undefined2 *)(DAT_004b7430 + (param_1 & 0xff) * 0x30 + -0x22));
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            uVar2 = 0x6dd;
            uVar3 = DAT_004b7470;
            FUN_0043d574(4,&DAT_004b742c,DAT_004b7460,DAT_004b7474,0x6dd,DAT_004b7470,param_1 & 0xff
                         ,*(undefined2 *)(DAT_004b7430 + (param_1 & 0xff) * 0x30 + -0x22));
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          uVar2 = 0x6dd;
          uVar3 = DAT_004b7470;
          FUN_0043d574(3,&DAT_004b742c,DAT_004b7460,DAT_004b7474,0x6dd,DAT_004b7470,param_1 & 0xff,
                       *(undefined2 *)(DAT_004b7430 + (param_1 & 0xff) * 0x30 + -0x22));
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar2 = 0x6dd;
        uVar3 = DAT_004b7470;
        FUN_0043d574(2,&DAT_004b742c,DAT_004b7460,DAT_004b7474,0x6dd,DAT_004b7470,param_1 & 0xff,
                     *(undefined2 *)(DAT_004b7430 + (param_1 & 0xff) * 0x30 + -0x22));
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar2 = 0x6dd;
      uVar3 = DAT_004b7470;
      FUN_0043d574(1,&DAT_004b742c,DAT_004b7460,DAT_004b7474,0x6dd,DAT_004b7470,param_1 & 0xff,
                   *(undefined2 *)(DAT_004b7430 + (param_1 & 0xff) * 0x30 + -0x22));
    }
  }
  return CONCAT44(uVar3,uVar2);
}

