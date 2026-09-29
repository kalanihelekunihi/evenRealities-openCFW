
undefined1 AttcDiscServiceCmpl(int param_1,int param_2)

{
  undefined1 uVar1;
  int iVar2;
  byte *pbVar3;
  
  if (*(char *)(param_2 + 2) == '\x03') {
    if (*(char *)(param_2 + 3) == '\0') {
      if (*(short *)(param_2 + 8) == 0) {
        uVar1 = 10;
      }
      else {
        pbVar3 = *(byte **)(param_2 + 4);
        *(ushort *)(param_1 + 0xe) = (ushort)pbVar3[1] * 0x100 + (ushort)*pbVar3;
        *(ushort *)(param_1 + 0x10) = (ushort)pbVar3[3] * 0x100 + (ushort)pbVar3[2];
        iVar2 = FUN_004c9c50(pbVar3 + 4);
        if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0056c374,&DAT_0056c1dc,3), iVar2 != 0)) {
          iVar2 = FUN_004c9c50();
          if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0056c374,DAT_0056c34c,4), iVar2 != 0)) {
            iVar2 = FUN_004c9c50();
            if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0056c374,DAT_0056c374,4), iVar2 != 0)) {
              iVar2 = FUN_004c9c50();
              if (iVar2 == 0) {
                iVar2 = FUN_004c9c50();
                if ((iVar2 == 0) ||
                   (iVar2 = FUN_0044b610(&DAT_0056c1e0,&DAT_0056c1e4,3), iVar2 != 0)) {
                  WsfTrace(DAT_0056c374,DAT_0056c378,*(undefined2 *)(param_1 + 0xe),
                           *(undefined2 *)(param_1 + 0x10));
                }
              }
              else {
                iVar2 = FUN_0043d0ce();
                if (iVar2 << 0x1e < 0) {
                  FUN_0043d574(4,&DAT_0056c1e0,DAT_0056c1f4,DAT_0056c370,0x275,DAT_0056c378,
                               *(undefined2 *)(param_1 + 0xe),*(undefined2 *)(param_1 + 0x10));
                }
              }
            }
            else {
              iVar2 = FUN_0043d0ce();
              if (iVar2 << 0x1e < 0) {
                FUN_0043d574(3,&DAT_0056c1e0,DAT_0056c1f4,DAT_0056c370,0x275,DAT_0056c378,
                             *(undefined2 *)(param_1 + 0xe),*(undefined2 *)(param_1 + 0x10));
              }
            }
          }
          else {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              FUN_0043d574(2,&DAT_0056c1e0,DAT_0056c1f4,DAT_0056c370,0x275,DAT_0056c378,
                           *(undefined2 *)(param_1 + 0xe),*(undefined2 *)(param_1 + 0x10));
            }
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(1,&DAT_0056c1e0,DAT_0056c1f4,DAT_0056c370,0x275,DAT_0056c378,
                         *(undefined2 *)(param_1 + 0xe),*(undefined2 *)(param_1 + 0x10));
          }
        }
        uVar1 = 0;
      }
    }
    else {
      uVar1 = *(undefined1 *)(param_2 + 3);
    }
  }
  else {
    iVar2 = FUN_004c9c50();
    if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0056c34c,&DAT_0056c1dc,3), iVar2 != 0)) {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0056c34c,DAT_0056c34c,4), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0056c34c,DAT_0056c374,4), iVar2 != 0)) {
          iVar2 = FUN_004c9c50();
          if (iVar2 == 0) {
            iVar2 = FUN_004c9c50();
            if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_0056c1e0,&DAT_0056c1e4,3), iVar2 != 0)) {
              WsfTrace(DAT_0056c34c,DAT_0056c36c,*(undefined1 *)(param_2 + 2));
            }
          }
          else {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              FUN_0043d574(4,&DAT_0056c1e0,DAT_0056c1f4,DAT_0056c370,0x262,DAT_0056c36c,
                           *(undefined1 *)(param_2 + 2));
            }
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(3,&DAT_0056c1e0,DAT_0056c1f4,DAT_0056c370,0x262,DAT_0056c36c,
                         *(undefined1 *)(param_2 + 2));
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(2,&DAT_0056c1e0,DAT_0056c1f4,DAT_0056c370,0x262,DAT_0056c36c,
                       *(undefined1 *)(param_2 + 2));
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,&DAT_0056c1e0,DAT_0056c1f4,DAT_0056c370,0x262,DAT_0056c36c,
                     *(undefined1 *)(param_2 + 2));
      }
    }
    uVar1 = 0x75;
  }
  return uVar1;
}

