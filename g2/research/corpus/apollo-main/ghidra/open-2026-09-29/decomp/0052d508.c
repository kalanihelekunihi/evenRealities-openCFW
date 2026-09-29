
undefined4 AttsCsfWriteFeatures(byte param_1,undefined4 param_2,ushort param_3,byte *param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  byte *pbVar5;
  
  iVar1 = DAT_0052da1c;
  if (param_1 == 0) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052da20,&DAT_0052d7b8,3), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052da20,DAT_0052da20,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052da20,DAT_0052da30,4), iVar1 != 0)) {
          iVar1 = FUN_004c9c50();
          if (iVar1 == 0) {
            iVar1 = FUN_004c9c50();
            if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_0052d7bc,&DAT_0052d7c0,3), iVar1 != 0)) {
              WsfTrace(DAT_0052da20,DAT_0052da3c,0);
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              FUN_0043d574(4,&DAT_0052d7bc,DAT_0052da2c,DAT_0052da40,0x172,DAT_0052da3c,0);
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(3,&DAT_0052d7bc,DAT_0052da2c,DAT_0052da40,0x172,DAT_0052da3c,0);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(2,&DAT_0052d7bc,DAT_0052da2c,DAT_0052da40,0x172,DAT_0052da3c,0);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,&DAT_0052d7bc,DAT_0052da2c,DAT_0052da40,0x172,DAT_0052da3c,0,param_4);
      }
    }
    uVar2 = 0xe;
  }
  else {
    iVar3 = DAT_0052da1c + (uint)param_1 * 2;
    pbVar5 = (byte *)(iVar3 + -2);
    if (param_3 < 2) {
      if ((*pbVar5 == 0) || ((*param_4 & 7) != 0)) {
        *pbVar5 = *param_4 & 7 | *pbVar5;
        iVar4 = FUN_004c9c50();
        if ((iVar4 == 0) || (iVar4 = FUN_0044b610(DAT_0052da30,&DAT_0052d7b8,3), iVar4 != 0)) {
          iVar4 = FUN_004c9c50();
          if ((iVar4 == 0) || (iVar4 = FUN_0044b610(DAT_0052da30,DAT_0052da20,4), iVar4 != 0)) {
            iVar4 = FUN_004c9c50();
            if ((iVar4 == 0) || (iVar4 = FUN_0044b610(DAT_0052da30,DAT_0052da30,4), iVar4 != 0)) {
              iVar4 = FUN_004c9c50();
              if (iVar4 == 0) {
                iVar4 = FUN_004c9c50();
                if ((iVar4 == 0) ||
                   (iVar4 = FUN_0044b610(&DAT_0052d7bc,&DAT_0052d7c0,3), iVar4 != 0)) {
                  WsfTrace(DAT_0052da30,DAT_0052da44,param_1,*pbVar5);
                }
              }
              else {
                iVar4 = FUN_0043d0ce();
                if (iVar4 << 0x1e < 0) {
                  FUN_0043d574(4,&DAT_0052d7bc,DAT_0052da2c,DAT_0052da40,0x18c,DAT_0052da44,param_1,
                               *pbVar5);
                }
              }
            }
            else {
              iVar4 = FUN_0043d0ce();
              if (iVar4 << 0x1e < 0) {
                FUN_0043d574(3,&DAT_0052d7bc,DAT_0052da2c,DAT_0052da40,0x18c,DAT_0052da44,param_1,
                             *pbVar5);
              }
            }
          }
          else {
            iVar4 = FUN_0043d0ce();
            if (iVar4 << 0x1e < 0) {
              FUN_0043d574(2,&DAT_0052d7bc,DAT_0052da2c,DAT_0052da40,0x18c,DAT_0052da44,param_1,
                           *pbVar5);
            }
          }
        }
        else {
          iVar4 = FUN_0043d0ce();
          if (iVar4 << 0x1e < 0) {
            FUN_0043d574(1,&DAT_0052d7bc,DAT_0052da2c,DAT_0052da40,0x18c,DAT_0052da44,param_1,
                         *pbVar5);
          }
        }
        if (*(int *)(iVar1 + 8) != 0) {
          (**(code **)(iVar1 + 8))(param_1,*(undefined1 *)(iVar3 + -1),pbVar5);
        }
        uVar2 = 0;
      }
      else {
        uVar2 = 0x13;
      }
    }
    else {
      uVar2 = 0xd;
    }
  }
  return uVar2;
}

