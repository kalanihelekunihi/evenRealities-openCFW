
void smpSmExecute(int param_1,int param_2)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  char *pcVar5;
  int *piVar6;
  
  iVar1 = DAT_0056f154;
  if (((*(char *)(DAT_0056f154 + 0xf8) == '\0') || (*(int *)(param_1 + 0x48) == 0)) ||
     (**(char **)(param_1 + 0x48) == '\0')) {
    iVar2 = FUN_004c9c50();
    if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0056f168,&DAT_0056f144,3), iVar2 != 0)) {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0056f168,PTR_DAT_0056f158,4), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0056f168,DAT_0056f168,4), iVar2 != 0)) {
          iVar2 = FUN_004c9c50();
          if (iVar2 == 0) {
            iVar2 = FUN_004c9c50();
            if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_0056f148,&DAT_0056f14c,3), iVar2 != 0)) {
              WsfTrace(DAT_0056f168,DAT_0056f174,*(undefined1 *)(param_2 + 2),
                       *(undefined1 *)(param_1 + 0x3e));
            }
          }
          else {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              FUN_0043d574(4,&DAT_0056f148,DAT_0056f164,DAT_0056f170,0x357,DAT_0056f174,
                           *(undefined1 *)(param_2 + 2),*(undefined1 *)(param_1 + 0x3e));
            }
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(3,&DAT_0056f148,DAT_0056f164,DAT_0056f170,0x357,DAT_0056f174,
                         *(undefined1 *)(param_2 + 2),*(undefined1 *)(param_1 + 0x3e));
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(2,&DAT_0056f148,DAT_0056f164,DAT_0056f170,0x357,DAT_0056f174,
                       *(undefined1 *)(param_2 + 2),*(undefined1 *)(param_1 + 0x3e));
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,&DAT_0056f148,DAT_0056f164,DAT_0056f170,0x357,DAT_0056f174,
                     *(undefined1 *)(param_2 + 2),*(undefined1 *)(param_1 + 0x3e));
      }
    }
  }
  else {
    iVar2 = FUN_004c9c50();
    if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0056f168,&DAT_0056f144,3), iVar2 != 0)) {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0056f168,PTR_DAT_0056f158,4), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0056f168,DAT_0056f168,4), iVar2 != 0)) {
          iVar2 = FUN_004c9c50();
          if (iVar2 == 0) {
            iVar2 = FUN_004c9c50();
            if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_0056f148,&DAT_0056f14c,3), iVar2 != 0)) {
              uVar3 = smpStateStr(*(undefined1 *)(param_1 + 0x3e));
              uVar4 = smpEventStr(*(undefined1 *)(param_2 + 2));
              WsfTrace(DAT_0056f168,DAT_0056f16c,uVar4,uVar3);
            }
          }
          else {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              uVar3 = smpStateStr(*(undefined1 *)(param_1 + 0x3e));
              uVar4 = smpEventStr(*(undefined1 *)(param_2 + 2));
              FUN_0043d574(4,&DAT_0056f148,DAT_0056f164,DAT_0056f170,0x354,DAT_0056f16c,uVar4,uVar3)
              ;
            }
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            uVar3 = smpStateStr(*(undefined1 *)(param_1 + 0x3e));
            uVar4 = smpEventStr(*(undefined1 *)(param_2 + 2));
            FUN_0043d574(3,&DAT_0056f148,DAT_0056f164,DAT_0056f170,0x354,DAT_0056f16c,uVar4,uVar3);
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          uVar3 = smpStateStr(*(undefined1 *)(param_1 + 0x3e));
          uVar4 = smpEventStr(*(undefined1 *)(param_2 + 2));
          FUN_0043d574(2,&DAT_0056f148,DAT_0056f164,DAT_0056f170,0x354,DAT_0056f16c,uVar4,uVar3);
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        uVar3 = smpStateStr(*(undefined1 *)(param_1 + 0x3e));
        uVar4 = smpEventStr(*(undefined1 *)(param_2 + 2));
        FUN_0043d574(1,&DAT_0056f148,DAT_0056f164,DAT_0056f170,0x354,DAT_0056f16c,uVar4,uVar3);
      }
    }
  }
  iVar2 = DmConnRole(*(undefined1 *)(param_1 + 0x3d));
  if (iVar2 == 1) {
    piVar6 = *(int **)(iVar1 + 0xe4);
  }
  else {
    piVar6 = *(int **)(iVar1 + 0xe8);
  }
  pcVar5 = *(char **)(*piVar6 + (uint)*(byte *)(param_1 + 0x3e) * 4);
  while( true ) {
    do {
      if (*pcVar5 == *(char *)(param_2 + 2)) {
        *(char *)(param_1 + 0x3e) = pcVar5[1];
        (**(code **)(piVar6[1] + (uint)(byte)pcVar5[2] * 4))(param_1,param_2);
        return;
      }
      pcVar5 = pcVar5 + 3;
    } while (*pcVar5 != '\0');
    if (pcVar5 == (char *)(piVar6[2] + 0xc)) break;
    pcVar5 = (char *)piVar6[2];
  }
  return;
}

