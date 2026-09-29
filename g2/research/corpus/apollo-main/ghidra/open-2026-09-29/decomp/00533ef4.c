
int dmConnSmExecute(int param_1,int param_2)

{
  byte bVar1;
  int iVar2;
  byte bVar3;
  
  iVar2 = FUN_004c9c50();
  if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_00534540,&DAT_00534130,3), iVar2 != 0)) {
    iVar2 = FUN_004c9c50();
    if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_00534540,DAT_00534550,4), iVar2 != 0)) {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_00534540,DAT_00534540,4), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if (iVar2 == 0) {
          iVar2 = FUN_004c9c50();
          if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_00534134,&DAT_005342d4,3), iVar2 != 0)) {
            WsfTrace(DAT_00534540,DAT_00534544,*(undefined1 *)(param_2 + 2),
                     *(undefined1 *)(param_1 + 0x15));
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(4,&DAT_00534134,DAT_0053454c,DAT_00534548,0x8d,DAT_00534544,
                         *(undefined1 *)(param_2 + 2),*(undefined1 *)(param_1 + 0x15));
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(3,&DAT_00534134,DAT_0053454c,DAT_00534548,0x8d,DAT_00534544,
                       *(undefined1 *)(param_2 + 2),*(undefined1 *)(param_1 + 0x15));
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,&DAT_00534134,DAT_0053454c,DAT_00534548,0x8d,DAT_00534544,
                     *(undefined1 *)(param_2 + 2),*(undefined1 *)(param_1 + 0x15));
      }
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,&DAT_00534134,DAT_0053454c,DAT_00534548,0x8d,DAT_00534544,
                   *(undefined1 *)(param_2 + 2),*(undefined1 *)(param_1 + 0x15));
    }
  }
  bVar3 = *(byte *)(param_2 + 2) & 7;
  bVar1 = *(byte *)((uint)*(byte *)(param_1 + 0x15) * 0x10 + DAT_00534554 + (uint)bVar3 * 2 + 1);
  *(undefined1 *)(param_1 + 0x15) =
       *(undefined1 *)(DAT_00534554 + (uint)*(byte *)(param_1 + 0x15) * 0x10 + (uint)bVar3 * 2);
  iVar2 = FUN_004c9c50();
  if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_00534540,&DAT_00534130,3), iVar2 != 0)) {
    iVar2 = FUN_004c9c50();
    if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_00534540,DAT_00534550,4), iVar2 != 0)) {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_00534540,DAT_00534540,4), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if (iVar2 == 0) {
          iVar2 = FUN_004c9c50();
          if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_00534348,&DAT_005342d4,3), iVar2 != 0)) {
            WsfTrace(DAT_00534540,DAT_00534558,bVar3,bVar1,*(undefined1 *)(param_1 + 0x15));
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(4,&DAT_00534348,DAT_0053454c,DAT_00534548,0x98,DAT_00534558,bVar3,bVar1,
                         *(undefined1 *)(param_1 + 0x15));
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(3,&DAT_00534134,DAT_0053454c,DAT_00534548,0x98,DAT_00534558,bVar3,bVar1,
                       *(undefined1 *)(param_1 + 0x15));
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,&DAT_00534134,DAT_0053454c,DAT_00534548,0x98,DAT_00534558,bVar3,bVar1,
                     *(undefined1 *)(param_1 + 0x15));
      }
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,&DAT_00534134,DAT_0053454c,DAT_00534548,0x98,DAT_00534558,bVar3,bVar1,
                   *(undefined1 *)(param_1 + 0x15));
    }
  }
  iVar2 = FUN_004c9c50();
  if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_00534540,&DAT_0053434c,3), iVar2 != 0)) {
    iVar2 = FUN_004c9c50();
    if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_00534540,DAT_00534550,4), iVar2 != 0)) {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_00534540,DAT_00534540,4), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if (iVar2 == 0) {
          iVar2 = FUN_004c9c50();
          if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_00534348,&DAT_005342d4,3), iVar2 != 0)) {
            WsfTrace(DAT_00534540,DAT_0053455c,bVar1 >> 4);
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(4,&DAT_00534348,DAT_0053454c,DAT_00534548,0x9a,DAT_0053455c,bVar1 >> 4);
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(3,&DAT_00534348,DAT_0053454c,DAT_00534548,0x9a,DAT_0053455c,bVar1 >> 4);
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,&DAT_00534348,DAT_0053454c,DAT_00534548,0x9a,DAT_0053455c,bVar1 >> 4);
      }
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,&DAT_00534348,DAT_0053454c,DAT_00534548,0x9a,DAT_0053455c,bVar1 >> 4);
    }
  }
  iVar2 = FUN_004c9c50();
  if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_00534540,&DAT_0053434c,3), iVar2 != 0)) {
    iVar2 = FUN_004c9c50();
    if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_00534540,DAT_00534550,4), iVar2 != 0)) {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_00534540,DAT_00534540,4), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if (iVar2 == 0) {
          iVar2 = FUN_004c9c50();
          if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_00534534,&DAT_00534538,3), iVar2 != 0)) {
            WsfTrace(DAT_00534540,DAT_00534560,bVar1 & 0xf);
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(4,&DAT_00534534,DAT_0053454c,DAT_00534548,0x9b,DAT_00534560,bVar1 & 0xf);
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(3,&DAT_00534534,DAT_0053454c,DAT_00534548,0x9b,DAT_00534560,bVar1 & 0xf);
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,&DAT_00534348,DAT_0053454c,DAT_00534548,0x9b,DAT_00534560,bVar1 & 0xf);
      }
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,&DAT_00534348,DAT_0053454c,DAT_00534548,0x9b,DAT_00534560,bVar1 & 0xf);
    }
  }
  if (bVar1 >> 4 < 3) {
    iVar2 = *(int *)(DAT_00534568 + ((int)(uint)bVar1 >> 4) * 4);
    if (iVar2 != 0) {
      param_1 = (**(code **)(iVar2 + (bVar1 & 0xf) * 4))(param_1,param_2);
    }
  }
  else {
    iVar2 = FUN_004c9c50();
    if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_0053453c,&DAT_0053453c,3), iVar2 != 0)) {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_0053453c,DAT_00534550,4), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_0053453c,DAT_00534540,4), iVar2 != 0)) {
          iVar2 = FUN_004c9c50();
          if (iVar2 == 0) {
            iVar2 = FUN_004c9c50();
            if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_00534534,&DAT_00534538,3), iVar2 != 0)) {
              WsfTrace(&DAT_0053453c,DAT_00534564,bVar1 >> 4);
            }
          }
          else {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              FUN_0043d574(4,&DAT_00534534,DAT_0053454c,DAT_00534548,0xa0,DAT_00534564,bVar1 >> 4);
            }
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(3,&DAT_00534534,DAT_0053454c,DAT_00534548,0xa0,DAT_00534564,bVar1 >> 4);
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(2,&DAT_00534534,DAT_0053454c,DAT_00534548,0xa0,DAT_00534564,bVar1 >> 4);
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,&DAT_00534534,DAT_0053454c,DAT_00534548,0xa0,DAT_00534564,bVar1 >> 4);
      }
    }
  }
  return param_1;
}

