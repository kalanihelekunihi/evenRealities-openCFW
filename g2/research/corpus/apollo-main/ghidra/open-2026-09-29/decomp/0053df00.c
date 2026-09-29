
void FUN_0053df00(int param_1,int param_2,int *param_3)

{
  byte bVar1;
  byte bVar2;
  byte bVar3;
  byte bVar4;
  int iVar5;
  undefined4 uVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  byte bVar13;
  byte bVar14;
  int iVar15;
  uint in_fpscr;
  undefined4 uVar16;
  float fVar17;
  float fVar18;
  undefined4 uVar19;
  undefined4 local_60;
  int local_5c;
  int local_58;
  int local_54;
  int local_50;
  int local_4c;
  int local_48;
  int local_44;
  int local_40;
  int local_3c;
  undefined4 local_38;
  undefined1 auStack_34 [16];
  
  if ((((2 < *(byte *)(param_2 + 0x28)) && (*(int *)(param_2 + 0x24) != 0)) &&
      ((*(byte *)(param_2 + 0x29) & 0x1f) != 0)) &&
     (local_4c = param_1, iVar5 = FUN_00450bcc(auStack_34,param_3,param_1 + 0x38), iVar5 != 0)) {
    local_58 = FUN_00451598(param_3);
    local_5c = FUN_004515a4(param_3);
    iVar5 = local_5c;
    if (local_58 < local_5c) {
      iVar5 = local_58;
    }
    iVar5 = iVar5 >> 1;
    iVar12 = *(int *)(param_2 + 0x1c);
    if (iVar5 < *(int *)(param_2 + 0x1c)) {
      iVar12 = iVar5;
    }
    if (*(int *)(param_2 + 0x24) < iVar5) {
      iVar5 = *(int *)(param_2 + 0x24);
    }
    bVar2 = *(byte *)(param_2 + 0x29) >> 1;
    bVar13 = bVar2 & 1;
    bVar1 = *(byte *)(param_2 + 0x29);
    bVar14 = bVar1 & 1;
    bVar3 = *(byte *)(param_2 + 0x29) >> 2;
    bVar4 = *(byte *)(param_2 + 0x29) >> 3;
    if (*(char *)(*(int *)(local_4c + 0x48) + 0x14) == '\x10') {
      local_60 = DAT_0053e724;
    }
    else {
      local_60 = 0x504;
    }
    FUN_00439be4(&local_38,param_2 + 0x20,3);
    uVar6 = FUN_004b06a8(local_38,*(undefined1 *)(param_2 + 0x28));
    FUN_004b0730(*(undefined4 *)(local_4c + 0x4c),local_60);
    FUN_00522a16(uVar6);
    iVar7 = *(int *)(*(int *)(local_4c + 0x48) + 4);
    iVar15 = *(int *)(*(int *)(local_4c + 0x48) + 8);
    if ((bVar3 & 1) != 0) {
      if (iVar12 == 0) {
        iVar8 = *param_3;
        iVar10 = iVar5;
        if ((bVar2 & 1) == 0) {
          iVar10 = 0;
        }
        iVar10 = iVar10 + param_3[1];
        iVar9 = iVar5;
        if ((bVar2 & 1) == 0) {
          iVar9 = 0;
        }
        iVar11 = iVar5;
        if ((bVar1 & 1) == 0) {
          iVar11 = 0;
        }
        iVar11 = (local_5c - iVar9) - iVar11;
        iVar9 = iVar5;
      }
      else {
        iVar8 = *param_3;
        iVar10 = iVar12 + param_3[1];
        iVar9 = iVar12;
        if (iVar5 < iVar12) {
          iVar9 = iVar5;
        }
        iVar11 = local_5c + iVar12 * -2;
      }
      FUN_00522ae0(iVar8 - iVar7,iVar10 - iVar15,iVar9,iVar11);
      if ((iVar12 != 0) && (iVar12 < iVar5)) {
        iVar10 = iVar5;
        if ((bVar2 & 1) == 0) {
          iVar10 = 0;
        }
        iVar8 = iVar5;
        if ((bVar2 & 1) == 0) {
          iVar8 = 0;
        }
        iVar9 = iVar5;
        if ((bVar1 & 1) == 0) {
          iVar9 = 0;
        }
        FUN_00522ae0((iVar12 + *param_3) - iVar7,(iVar10 + param_3[1]) - iVar15,iVar5 - iVar12,
                     (local_5c - iVar8) - iVar9);
      }
    }
    if ((bVar4 & 1) != 0) {
      if (iVar12 == 0) {
        iVar8 = (param_3[2] + 1) - iVar5;
        iVar10 = iVar5;
        if ((bVar2 & 1) == 0) {
          iVar10 = 0;
        }
        iVar10 = iVar10 + param_3[1];
        iVar9 = iVar5;
        if ((bVar2 & 1) == 0) {
          iVar9 = 0;
        }
        iVar11 = iVar5;
        if ((bVar1 & 1) == 0) {
          iVar11 = 0;
        }
        iVar11 = (local_5c - iVar9) - iVar11;
        iVar9 = iVar5;
      }
      else {
        iVar8 = iVar12;
        if (iVar5 < iVar12) {
          iVar8 = iVar5;
        }
        iVar8 = (param_3[2] + 1) - iVar8;
        iVar10 = iVar12 + param_3[1];
        iVar9 = iVar12;
        if (iVar5 < iVar12) {
          iVar9 = iVar5;
        }
        iVar11 = local_5c + iVar12 * -2;
      }
      FUN_00522ae0(iVar8 - iVar7,iVar10 - iVar15,iVar9,iVar11);
      if ((iVar12 != 0) && (iVar12 < iVar5)) {
        iVar10 = iVar5;
        if ((bVar2 & 1) == 0) {
          iVar10 = 0;
        }
        iVar8 = iVar5;
        if ((bVar2 & 1) == 0) {
          iVar8 = 0;
        }
        iVar9 = iVar5;
        if ((bVar1 & 1) == 0) {
          iVar9 = 0;
        }
        FUN_00522ae0(((param_3[2] + 1) - iVar5) - iVar7,(iVar10 + param_3[1]) - iVar15,
                     iVar5 - iVar12,(local_5c - iVar8) - iVar9);
      }
    }
    if ((bVar2 & 1) != 0) {
      if (iVar12 == 0) {
        iVar9 = *param_3;
        iVar11 = param_3[1];
        iVar10 = local_58;
        iVar8 = iVar5;
      }
      else {
        iVar9 = iVar12 + *param_3;
        iVar11 = param_3[1];
        iVar10 = local_58 + iVar12 * -2;
        iVar8 = iVar12;
        if (iVar5 < iVar12) {
          iVar8 = iVar5;
        }
      }
      FUN_00522ae0(iVar9 - iVar7,iVar11 - iVar15,iVar10,iVar8);
      if ((iVar12 != 0) && (iVar12 < iVar5)) {
        iVar10 = iVar12;
        if ((bVar3 & 1) == 0) {
          iVar10 = 0;
        }
        iVar8 = iVar12;
        if ((bVar3 & 1) == 0) {
          iVar8 = 0;
        }
        iVar9 = iVar12;
        if ((bVar4 & 1) == 0) {
          iVar9 = 0;
        }
        FUN_00522ae0((iVar10 + *param_3) - iVar7,(iVar12 + param_3[1]) - iVar15,
                     (local_58 - iVar8) - iVar9,iVar5 - iVar12);
      }
    }
    if ((bVar1 & 1) != 0) {
      if (iVar12 == 0) {
        iVar11 = *param_3;
        iVar8 = (param_3[3] + 1) - iVar5;
        iVar10 = local_58;
        iVar9 = iVar5;
      }
      else {
        iVar11 = iVar12 + *param_3;
        iVar8 = iVar12;
        if (iVar5 < iVar12) {
          iVar8 = iVar5;
        }
        iVar8 = (param_3[3] + 1) - iVar8;
        iVar10 = local_58 + iVar12 * -2;
        iVar9 = iVar12;
        if (iVar5 < iVar12) {
          iVar9 = iVar5;
        }
      }
      FUN_00522ae0(iVar11 - iVar7,iVar8 - iVar15,iVar10,iVar9);
      if ((iVar12 != 0) && (iVar12 < iVar5)) {
        iVar10 = iVar12;
        if ((bVar3 & 1) == 0) {
          iVar10 = 0;
        }
        iVar8 = iVar12;
        if ((bVar3 & 1) == 0) {
          iVar8 = 0;
        }
        iVar9 = iVar12;
        if ((bVar4 & 1) == 0) {
          iVar9 = 0;
        }
        FUN_00522ae0((iVar10 + *param_3) - iVar7,((param_3[3] + 1) - iVar5) - iVar15,
                     (local_58 - iVar8) - iVar9,iVar5 - iVar12);
      }
    }
    if (iVar12 != 0) {
      if ((bVar2 & 1) != 0 || (bVar3 & 1) != 0) {
        local_5c = *param_3;
        local_58 = param_3[1];
        local_54 = iVar12 + local_5c + -1;
        local_50 = iVar12 + local_58 + -1;
        if ((bVar3 & 1 & (bVar13 ^ 1)) == 0) {
          if (bVar13 == 1 && (bVar3 & 1) == 0) {
            iVar10 = iVar12;
            if (iVar5 < iVar12) {
              iVar10 = iVar5;
            }
            local_50 = iVar10 + local_58 + -1;
          }
        }
        else {
          iVar10 = iVar12;
          if (iVar5 < iVar12) {
            iVar10 = iVar5;
          }
          local_54 = iVar10 + local_5c + -1;
        }
        FUN_00450bcc(&local_48,&local_5c,local_4c + 0x38);
        FUN_00450bb2(&local_48,-iVar7,-iVar15);
        FUN_004b1516(local_48,local_44,(local_40 - local_48) + 1,(local_3c - local_44) + 1);
        uVar6 = VectorSignedToFloat((iVar12 + *param_3) - iVar7,(byte)(in_fpscr >> 0x16) & 3);
        uVar16 = VectorSignedToFloat((iVar12 + param_3[1]) - iVar15,(byte)(in_fpscr >> 0x16) & 3);
        iVar10 = iVar12;
        if (iVar5 < iVar12) {
          iVar10 = iVar5;
        }
        fVar17 = (float)VectorSignedToFloat(iVar12,(byte)(in_fpscr >> 0x16) & 3);
        fVar18 = (float)VectorSignedToFloat(iVar10,(byte)(in_fpscr >> 0x16) & 3);
        iVar10 = iVar12;
        if (iVar5 < iVar12) {
          iVar10 = iVar5;
        }
        uVar19 = VectorSignedToFloat(iVar10,(byte)(in_fpscr >> 0x16) & 3);
        FUN_0052330c(uVar6,uVar16,fVar17 + fVar18 * -0.5,uVar19,DAT_0053e714,DAT_0053e710);
        FUN_004b1548();
      }
      if ((bVar1 & 1) != 0 || (bVar3 & 1) != 0) {
        local_5c = *param_3;
        local_50 = param_3[3];
        local_54 = iVar12 + local_5c + -1;
        local_58 = (local_50 - iVar12) + 1;
        if ((bVar3 & 1 & (bVar14 ^ 1)) == 0) {
          if (bVar14 == 1 && (bVar3 & 1) == 0) {
            iVar10 = iVar12;
            if (iVar5 < iVar12) {
              iVar10 = iVar5;
            }
            local_58 = (local_50 - iVar10) + 1;
          }
        }
        else {
          iVar10 = iVar12;
          if (iVar5 < iVar12) {
            iVar10 = iVar5;
          }
          local_54 = iVar10 + local_5c + -1;
        }
        FUN_00450bcc(&local_48,&local_5c,local_4c + 0x38);
        FUN_00450bb2(&local_48,-iVar7,-iVar15);
        FUN_004b1516(local_48,local_44,(local_40 - local_48) + 1,(local_3c - local_44) + 1);
        uVar6 = VectorSignedToFloat((iVar12 + *param_3) - iVar7,(byte)(in_fpscr >> 0x16) & 3);
        uVar16 = VectorSignedToFloat(((param_3[3] - iVar12) + 1) - iVar15,
                                     (byte)(in_fpscr >> 0x16) & 3);
        iVar10 = iVar12;
        if (iVar5 < iVar12) {
          iVar10 = iVar5;
        }
        fVar17 = (float)VectorSignedToFloat(iVar12,(byte)(in_fpscr >> 0x16) & 3);
        fVar18 = (float)VectorSignedToFloat(iVar10,(byte)(in_fpscr >> 0x16) & 3);
        iVar10 = iVar12;
        if (iVar5 < iVar12) {
          iVar10 = iVar5;
        }
        uVar19 = VectorSignedToFloat(iVar10,(byte)(in_fpscr >> 0x16) & 3);
        FUN_0052330c(uVar6,uVar16,fVar17 + fVar18 * -0.5,uVar19,DAT_0053e718,DAT_0053e714);
        FUN_004b1548();
      }
      if ((bVar1 & 1) != 0 || (bVar4 & 1) != 0) {
        local_54 = param_3[2];
        local_50 = param_3[3];
        local_5c = (local_54 - iVar12) + 1;
        local_58 = (local_50 - iVar12) + 1;
        if ((bVar4 & 1 & (bVar14 ^ 1)) == 0) {
          if (bVar14 == 1 && (bVar4 & 1) == 0) {
            iVar10 = iVar12;
            if (iVar5 < iVar12) {
              iVar10 = iVar5;
            }
            local_58 = (local_50 - iVar10) + 1;
          }
        }
        else {
          iVar10 = iVar12;
          if (iVar5 < iVar12) {
            iVar10 = iVar5;
          }
          local_5c = (local_54 - iVar10) + 1;
        }
        FUN_00450bcc(&local_48,&local_5c,local_4c + 0x38);
        FUN_00450bb2(&local_48,-iVar7,-iVar15);
        FUN_004b1516(local_48,local_44,(local_40 - local_48) + 1,(local_3c - local_44) + 1);
        uVar6 = VectorSignedToFloat(((param_3[2] - iVar12) + 1) - iVar7,(byte)(in_fpscr >> 0x16) & 3
                                   );
        uVar16 = VectorSignedToFloat(((param_3[3] - iVar12) + 1) - iVar15,
                                     (byte)(in_fpscr >> 0x16) & 3);
        iVar10 = iVar12;
        if (iVar5 < iVar12) {
          iVar10 = iVar5;
        }
        fVar17 = (float)VectorSignedToFloat(iVar12,(byte)(in_fpscr >> 0x16) & 3);
        fVar18 = (float)VectorSignedToFloat(iVar10,(byte)(in_fpscr >> 0x16) & 3);
        iVar10 = iVar12;
        if (iVar5 < iVar12) {
          iVar10 = iVar5;
        }
        uVar19 = VectorSignedToFloat(iVar10,(byte)(in_fpscr >> 0x16) & 3);
        FUN_0052330c(uVar6,uVar16,fVar17 + fVar18 * -0.5,uVar19,DAT_0053e71c,DAT_0053e718);
        FUN_004b1548();
      }
      if ((bVar2 & 1) != 0 || (bVar4 & 1) != 0) {
        local_54 = param_3[2];
        local_58 = param_3[1];
        local_5c = (local_54 - iVar12) + 1;
        local_50 = iVar12 + local_58 + -1;
        if ((bVar4 & 1 & (bVar13 ^ 1)) == 0) {
          if (bVar13 == 1 && (bVar4 & 1) == 0) {
            iVar10 = iVar12;
            if (iVar5 < iVar12) {
              iVar10 = iVar5;
            }
            local_50 = (local_58 - iVar10) + 1;
          }
        }
        else {
          iVar10 = iVar12;
          if (iVar5 < iVar12) {
            iVar10 = iVar5;
          }
          local_5c = (local_54 - iVar10) + 1;
        }
        FUN_00450bcc(&local_48,&local_5c,local_4c + 0x38);
        FUN_00450bb2(&local_48,-iVar7,-iVar15);
        FUN_004b1516(local_48,local_44,(local_40 - local_48) + 1,(local_3c - local_44) + 1);
        uVar6 = VectorSignedToFloat(((param_3[2] - iVar12) + 1) - iVar7,(byte)(in_fpscr >> 0x16) & 3
                                   );
        uVar16 = VectorSignedToFloat((iVar12 + param_3[1]) - iVar15,(byte)(in_fpscr >> 0x16) & 3);
        iVar7 = iVar12;
        if (iVar5 < iVar12) {
          iVar7 = iVar5;
        }
        fVar17 = (float)VectorSignedToFloat(iVar12,(byte)(in_fpscr >> 0x16) & 3);
        fVar18 = (float)VectorSignedToFloat(iVar7,(byte)(in_fpscr >> 0x16) & 3);
        if (iVar5 < iVar12) {
          iVar12 = iVar5;
        }
        uVar19 = VectorSignedToFloat(iVar12,(byte)(in_fpscr >> 0x16) & 3);
        FUN_0052330c(uVar6,uVar16,fVar17 + fVar18 * -0.5,uVar19,DAT_0053e710,DAT_0053e720);
        FUN_004b1548();
      }
    }
  }
  return;
}

