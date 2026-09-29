
byte FUN_00503d1e(uint param_1,uint param_2,undefined4 param_3,int param_4)

{
  byte bVar1;
  int iVar2;
  int *piVar3;
  
  bVar1 = DmConnOpen(3,param_1 & 0xff,param_2 & 0xff,param_3,param_1,param_2,param_3,param_4);
  if (bVar1 != 0) {
    if (bVar1 == 0) {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_005040d4,&LAB_00503ea4,3), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_005040d4,DAT_005040d4,4), iVar2 != 0)) {
          iVar2 = FUN_004c9c50();
          if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_005040d4,DAT_005040c4,4), iVar2 != 0)) {
            iVar2 = FUN_004c9c50();
            if (iVar2 == 0) {
              iVar2 = FUN_004c9c50();
              if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_00503ff0,&DAT_00503ff8,3), iVar2 != 0))
              {
                WsfTrace(DAT_005040d4,DAT_00504120,0);
              }
            }
            else {
              iVar2 = FUN_0043d0ce();
              if (iVar2 << 0x1e < 0) {
                FUN_0043d574(4,&DAT_00503ff0,DAT_005040d0,DAT_00504124,0x37e,DAT_00504120,0);
              }
            }
          }
          else {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              FUN_0043d574(3,&DAT_00503ff0,DAT_005040d0,DAT_00504124,0x37e,DAT_00504120,0);
            }
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(2,&DAT_00503ff0,DAT_005040d0,DAT_00504124,0x37e,DAT_00504120,0);
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(1,&DAT_00503ff0,DAT_005040d0,DAT_00504124,0x37e,DAT_00504120,0);
        }
      }
      bVar1 = 0;
    }
    else {
      iVar2 = DAT_0050411c + (uint)bVar1 * 0x30;
      piVar3 = (int *)(iVar2 + -0x30);
      *(byte *)(iVar2 + -0x2c) = bVar1;
      if ((param_4 == 0) || (iVar2 = FUN_0047a5d0(param_4), iVar2 == 0)) {
        iVar2 = FUN_0047ad74(param_2 & 0xff,param_3);
        *piVar3 = iVar2;
      }
      else {
        *piVar3 = param_4;
      }
    }
  }
  return bVar1;
}

