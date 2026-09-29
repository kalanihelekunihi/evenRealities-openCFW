
void FUN_004b3ca4(ushort *param_1)

{
  char cVar1;
  int iVar2;
  byte bVar3;
  
  iVar2 = 0;
  if ((((((char)param_1[1] != '\"') && ((char)param_1[1] != 'H')) && (*param_1 != 0x20)) &&
      ((*param_1 != 0x79 && (*param_1 != 0)))) && ((*param_1 != 0 && (*param_1 < 4)))) {
    iVar2 = DAT_004b46f0 + (uint)*param_1 * 0x30 + -0x30;
  }
  cVar1 = (char)param_1[1];
  if (cVar1 == ' ') {
    FUN_004b32d4(0x20,iVar2);
    return;
  }
  if (cVar1 != '\"') {
    if (cVar1 == '\'') {
      FUN_004b36fc(param_1);
      return;
    }
    if (cVar1 == '(') {
      FUN_004b3720(param_1);
      return;
    }
    if (cVar1 == ')') {
      return;
    }
    if (cVar1 == '7') {
      FUN_004b3792(param_1);
      return;
    }
    if (cVar1 == '@') {
      FUN_004b38f2(param_1);
      return;
    }
    if (cVar1 == 'A') {
      iVar2 = FUN_004c9c50();
      if ((iVar2 != 0) && (iVar2 = FUN_0044b610(DAT_004b46f8,&DAT_004b423c,3), iVar2 == 0)) {
        iVar2 = FUN_0043d0ce();
        if (-1 < iVar2 << 0x1e) {
          return;
        }
        FUN_0043d574(1,&DAT_004b4234,DAT_004b4704,DAT_004b4700,0x574,DAT_004b4714,
                     *(undefined1 *)((int)param_1 + 3),param_1[5],param_1[3]);
        return;
      }
      iVar2 = FUN_004c9c50();
      if ((iVar2 != 0) && (iVar2 = FUN_0044b610(DAT_004b46f8,DAT_004b4708,4), iVar2 == 0)) {
        iVar2 = FUN_0043d0ce();
        if (-1 < iVar2 << 0x1e) {
          return;
        }
        FUN_0043d574(2,&DAT_004b4234,DAT_004b4704,DAT_004b4700,0x574,DAT_004b4714,
                     *(undefined1 *)((int)param_1 + 3),param_1[5],param_1[3]);
        return;
      }
      iVar2 = FUN_004c9c50();
      if ((iVar2 != 0) && (iVar2 = FUN_0044b610(DAT_004b46f8,DAT_004b46f8,4), iVar2 == 0)) {
        iVar2 = FUN_0043d0ce();
        if (-1 < iVar2 << 0x1e) {
          return;
        }
        FUN_0043d574(3,&DAT_004b4234,DAT_004b4704,DAT_004b4700,0x574,DAT_004b4714,
                     *(undefined1 *)((int)param_1 + 3),param_1[5],param_1[3]);
        return;
      }
      iVar2 = FUN_004c9c50();
      if (iVar2 != 0) {
        iVar2 = FUN_0043d0ce();
        if (-1 < iVar2 << 0x1e) {
          return;
        }
        FUN_0043d574(4,&DAT_004b4234,DAT_004b4704,DAT_004b4700,0x574,DAT_004b4714,
                     *(undefined1 *)((int)param_1 + 3),param_1[5],param_1[3]);
        return;
      }
      iVar2 = FUN_004c9c50();
      if ((iVar2 != 0) && (iVar2 = FUN_0044b610(&DAT_004b4234,&DAT_004b4504,3), iVar2 == 0)) {
        return;
      }
      WsfTrace(DAT_004b46f8,DAT_004b4714,*(undefined1 *)((int)param_1 + 3),param_1[5],param_1[3]);
      return;
    }
    if (cVar1 != 'H') {
      if (cVar1 != 'W') {
        if (cVar1 != 'y') {
          return;
        }
        HciDrvRadioBoot(0);
        DmDevReset();
        return;
      }
      bVar3 = (byte)param_1[4] & 0x20;
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_004b46f8,&DAT_004b3f8c,3), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_004b46f8,DAT_004b4708,4), iVar2 != 0)) {
          iVar2 = FUN_004c9c50();
          if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_004b46f8,DAT_004b46f8,4), iVar2 != 0)) {
            iVar2 = FUN_004c9c50();
            if (iVar2 == 0) {
              iVar2 = FUN_004c9c50();
              if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_004b3f90,&DAT_004b416c,3), iVar2 != 0))
              {
                WsfTrace(DAT_004b46f8,DAT_004b46fc,(char)param_1[4],bVar3);
              }
            }
            else {
              iVar2 = FUN_0043d0ce();
              if (iVar2 << 0x1e < 0) {
                FUN_0043d574(4,&DAT_004b3f90,DAT_004b4704,DAT_004b4700,0x55b,DAT_004b46fc,
                             (char)param_1[4],bVar3);
              }
            }
          }
          else {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              FUN_0043d574(3,&DAT_004b3f90,DAT_004b4704,DAT_004b4700,0x55b,DAT_004b46fc,
                           (char)param_1[4],bVar3);
            }
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(2,&DAT_004b3f90,DAT_004b4704,DAT_004b4700,0x55b,DAT_004b46fc,
                         (char)param_1[4],bVar3);
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(1,&DAT_004b3f90,DAT_004b4704,DAT_004b4700,0x55b,DAT_004b46fc,(char)param_1[4]
                       ,bVar3);
        }
      }
      if (bVar3 == 0x20) {
        iVar2 = FUN_004c9c50();
        if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_004b46f8,&DAT_004b3f8c,3), iVar2 != 0)) {
          iVar2 = FUN_004c9c50();
          if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_004b46f8,DAT_004b4708,4), iVar2 != 0)) {
            iVar2 = FUN_004c9c50();
            if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_004b46f8,DAT_004b46f8,4), iVar2 != 0)) {
              iVar2 = FUN_004c9c50();
              if (iVar2 == 0) {
                iVar2 = FUN_004c9c50();
                if ((iVar2 == 0) ||
                   (iVar2 = FUN_0044b610(&DAT_004b4234,&DAT_004b416c,3), iVar2 != 0)) {
                  WsfTrace(DAT_004b46f8,DAT_004b470c);
                }
              }
              else {
                iVar2 = FUN_0043d0ce();
                if (iVar2 << 0x1e < 0) {
                  FUN_0043d574(4,&DAT_004b3f90,DAT_004b4704,DAT_004b4700,0x55e,DAT_004b470c);
                }
              }
            }
            else {
              iVar2 = FUN_0043d0ce();
              if (iVar2 << 0x1e < 0) {
                FUN_0043d574(3,&DAT_004b3f90,DAT_004b4704,DAT_004b4700,0x55e,DAT_004b470c);
              }
            }
          }
          else {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              FUN_0043d574(2,&DAT_004b3f90,DAT_004b4704,DAT_004b4700,0x55e,DAT_004b470c);
            }
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(1,&DAT_004b3f90,DAT_004b4704,DAT_004b4700,0x55e,DAT_004b470c);
          }
        }
        DmConnSetDataLen((char)*param_1,0xfb,0x848);
        return;
      }
      iVar2 = FUN_004c9c50();
      if ((iVar2 != 0) && (iVar2 = FUN_0044b610(DAT_004b46f8,&DAT_004b423c,3), iVar2 == 0)) {
        iVar2 = FUN_0043d0ce();
        if (-1 < iVar2 << 0x1e) {
          return;
        }
        FUN_0043d574(1,&DAT_004b4234,DAT_004b4704,DAT_004b4700,0x563,DAT_004b4710);
        return;
      }
      iVar2 = FUN_004c9c50();
      if ((iVar2 != 0) && (iVar2 = FUN_0044b610(DAT_004b46f8,DAT_004b4708,4), iVar2 == 0)) {
        iVar2 = FUN_0043d0ce();
        if (-1 < iVar2 << 0x1e) {
          return;
        }
        FUN_0043d574(2,&DAT_004b4234,DAT_004b4704,DAT_004b4700,0x563,DAT_004b4710);
        return;
      }
      iVar2 = FUN_004c9c50();
      if ((iVar2 != 0) && (iVar2 = FUN_0044b610(DAT_004b46f8,DAT_004b46f8,4), iVar2 == 0)) {
        iVar2 = FUN_0043d0ce();
        if (-1 < iVar2 << 0x1e) {
          return;
        }
        FUN_0043d574(3,&DAT_004b4234,DAT_004b4704,DAT_004b4700,0x563,DAT_004b4710);
        return;
      }
      iVar2 = FUN_004c9c50();
      if (iVar2 != 0) {
        iVar2 = FUN_0043d0ce();
        if (-1 < iVar2 << 0x1e) {
          return;
        }
        FUN_0043d574(4,&DAT_004b4234,DAT_004b4704,DAT_004b4700,0x563,DAT_004b4710);
        return;
      }
      iVar2 = FUN_004c9c50();
      if ((iVar2 != 0) && (iVar2 = FUN_0044b610(&DAT_004b4234,&DAT_004b416c,3), iVar2 == 0)) {
        return;
      }
      WsfTrace(DAT_004b46f8,DAT_004b4710);
      return;
    }
  }
  if (*(int *)(DAT_004b46f4 + 0x78) != 0) {
    (**(code **)(DAT_004b46f4 + 0x78))(param_1);
  }
  return;
}

