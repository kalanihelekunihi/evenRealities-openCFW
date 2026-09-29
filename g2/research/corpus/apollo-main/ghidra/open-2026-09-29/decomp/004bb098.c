
undefined8 FUN_004bb098(ushort *param_1,uint param_2,uint param_3)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  
  if ((param_2 & 0xff) == 0) {
    uVar3 = param_2;
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_004bb3a0,&DAT_004bb214,3), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_004bb3a0,DAT_004bb3a0,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_004bb3a0,DAT_004bb3a8,4), iVar1 != 0)) {
          iVar1 = FUN_004c9c50();
          if (iVar1 == 0) {
            iVar1 = FUN_004c9c50();
            if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_004bb218,&DAT_004bb210,3), iVar1 != 0)) {
              WsfTrace(DAT_004bb3a0,DAT_004bb3cc,param_2 & 0xff);
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              uVar3 = 400;
              param_3 = DAT_004bb3cc;
              FUN_0043d574(4,&DAT_004bb218,DAT_004bb3a4,DAT_004bb3d0,400,DAT_004bb3cc,param_2 & 0xff
                          );
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            uVar3 = 400;
            param_3 = DAT_004bb3cc;
            FUN_0043d574(3,&DAT_004bb218,DAT_004bb3a4,DAT_004bb3d0,400,DAT_004bb3cc,param_2 & 0xff);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          uVar3 = 400;
          param_3 = DAT_004bb3cc;
          FUN_0043d574(2,&DAT_004bb218,DAT_004bb3a4,DAT_004bb3d0,400,DAT_004bb3cc,param_2 & 0xff);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar3 = 400;
        param_3 = DAT_004bb3cc;
        FUN_0043d574(1,&DAT_004bb218,DAT_004bb3a4,DAT_004bb3d0,400,DAT_004bb3cc,param_2 & 0xff);
      }
    }
  }
  else {
    uVar2 = *(undefined4 *)(DAT_004bb3ac + (param_2 & 0xff) * 0x30 + -0x30);
    iVar1 = HciLeAdvExtSupported();
    uVar3 = param_2;
    if ((iVar1 != 0) && (iVar1 = FUN_0047ae78(uVar2,4,0), uVar3 = param_2, iVar1 != 0)) {
      uVar2 = DmSecGetLocalIrk();
      param_3 = (uint)*param_1;
      uVar3 = 1;
      DmPrivAddDevToResList(*(undefined1 *)(iVar1 + 0x16),iVar1 + 0x10,iVar1,uVar2);
    }
  }
  return CONCAT44(param_3,uVar3);
}

