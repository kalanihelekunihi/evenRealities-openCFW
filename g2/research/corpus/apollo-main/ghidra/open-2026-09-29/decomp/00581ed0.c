
undefined4 FUN_00581ed0(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  char *pcVar1;
  undefined1 *puVar2;
  undefined1 *puVar3;
  char *pcVar4;
  uint *puVar5;
  undefined2 *puVar6;
  char cVar7;
  undefined2 uVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  uint uVar14;
  undefined4 uVar15;
  uint uVar16;
  uint uVar17;
  ushort uVar18;
  int local_28;
  uint local_24;
  uint local_20;
  int local_1c;
  
  local_1c = 0;
  local_28 = 0;
  local_20 = 0;
  local_24 = 0;
  iVar9 = FUN_005848fc(param_3,1,&local_1c);
  iVar10 = FUN_005848fc(param_3,2,&local_28);
  iVar11 = FUN_005848fc(param_3,3,&local_20);
  iVar12 = FUN_005848fc(param_3,4,&local_24);
  if ((iVar9 == 0) || (local_1c < 1)) {
    FUN_004733ee(DAT_00582804);
  }
  else {
    iVar13 = FUN_0044b610(iVar9,&DAT_00582220,3);
    pcVar1 = DAT_00582808;
    if (iVar13 == 0) {
      FUN_0043c0e4(DAT_00582808,0x48c,0);
      if ((iVar10 != 0) && (0 < local_28)) {
        cVar7 = thunk_FUN_0048d86c(iVar10);
        *pcVar1 = cVar7;
      }
      if ((iVar11 == 0) || ((int)local_20 < 1)) {
        FUN_0044b728(pcVar1 + 4,0x80,DAT_0058280c);
        uVar8 = FUN_0044a43c(pcVar1 + 4);
        *(undefined2 *)(pcVar1 + 2) = uVar8;
      }
      else {
        uVar14 = local_20;
        if (0x7f < local_20) {
          uVar14 = 0x7f;
        }
        FUN_0044b5a0(pcVar1 + 4,iVar11,uVar14);
        pcVar1[uVar14 + 4] = '\0';
        *(short *)(pcVar1 + 2) = (short)uVar14;
      }
      if ((iVar12 == 0) || ((int)local_24 < 1)) {
        if (*pcVar1 == '\x01') {
          FUN_0044b728(pcVar1 + 0x86,0x400,DAT_00582810);
          uVar8 = FUN_0044a43c(pcVar1 + 0x86);
          *(undefined2 *)(pcVar1 + 0x84) = uVar8;
        }
        else {
          FUN_0044b728(pcVar1 + 0x86,0x400,DAT_00582814);
          uVar8 = FUN_0044a43c(pcVar1 + 0x86);
          *(undefined2 *)(pcVar1 + 0x84) = uVar8;
        }
      }
      else {
        uVar14 = local_24;
        if (0x3ff < local_24) {
          uVar14 = 0x3ff;
        }
        FUN_0044b5a0(pcVar1 + 0x86,iVar12,uVar14);
        pcVar1[uVar14 + 0x86] = '\0';
        *(short *)(pcVar1 + 0x84) = (short)uVar14;
      }
      puVar2 = DAT_00582818;
      FUN_0043c0e4(DAT_00582818,0xfac,0);
      *puVar2 = 5;
      pcVar4 = DAT_0058281c;
      *DAT_0058281c = *DAT_0058281c + '\x01';
      puVar2[1] = *pcVar4;
      *(undefined2 *)(puVar2 + 2) = 7;
      FUN_00439c04(puVar2 + 4,pcVar1,0x48c);
      FUN_00581de0(puVar2);
    }
    else {
      iVar11 = FUN_0044b610(iVar9,DAT_00582820,5);
      puVar2 = DAT_00582824;
      if (iVar11 == 0) {
        FUN_0043c0e4(DAT_00582824,0x94,0);
        *puVar2 = 1;
        puVar2[1] = 1;
        puVar2[3] = 1;
        puVar2[4] = 1;
        puVar2[5] = 0;
        puVar2[2] = 1;
        puVar2[6] = 0;
        puVar2[7] = 0;
        pcVar1 = DAT_00582828;
        *DAT_00582828 = '\0';
        if ((iVar10 != 0) && (0 < local_28)) {
          puVar2[7] = 1;
          *(undefined4 *)(puVar2 + 0x8c) = 2;
          uVar14 = FUN_0044b728(puVar2 + 10,0x80,DAT_0058282c);
          if (0x7f < uVar14) {
            uVar14 = 0x7f;
          }
          *(short *)(puVar2 + 8) = (short)uVar14;
          *pcVar1 = '\x01';
        }
        puVar3 = DAT_00582818;
        FUN_0043c0e4(DAT_00582818,0xfac,0);
        *puVar3 = 1;
        pcVar1 = DAT_0058281c;
        *DAT_0058281c = *DAT_0058281c + '\x01';
        puVar3[1] = *pcVar1;
        *(undefined2 *)(puVar3 + 2) = 3;
        FUN_00439c04(puVar3 + 4,puVar2,0x94);
        FUN_00581de0(puVar3);
      }
      else {
        iVar11 = FUN_0044b610(iVar9,DAT_00582830,6);
        if (iVar11 == 0) {
          if (*DAT_00582828 == '\0') {
            FUN_004733ee(DAT_00582834);
          }
          else if ((iVar10 == 0) || (local_28 < 1)) {
            FUN_004733ee(DAT_00582838);
          }
          else {
            uVar14 = thunk_FUN_0048d86c(iVar10);
            puVar5 = DAT_00582840;
            if (uVar14 < 2) {
              FUN_0043c0e4(DAT_00582840,0xfa8,0);
              *puVar5 = uVar14;
              uVar15 = FUN_00581e6a(uVar14,(int)puVar5 + 6,4000);
              *(short *)(puVar5 + 1) = (short)uVar15;
              puVar2 = DAT_00582818;
              FUN_0043c0e4(DAT_00582818,0xfac,0);
              *puVar2 = 7;
              pcVar1 = DAT_0058281c;
              *DAT_0058281c = *DAT_0058281c + '\x01';
              puVar2[1] = *pcVar1;
              *(undefined2 *)(puVar2 + 2) = 0xd;
              FUN_00439c04(puVar2 + 4,puVar5,0xfa8);
              FUN_00581de0(puVar2);
              FUN_004733ee(DAT_00582844,uVar14,uVar15);
            }
            else {
              FUN_004733ee(DAT_0058283c,uVar14);
            }
          }
        }
        else {
          iVar11 = FUN_0044b610(iVar9,DAT_00582848,8);
          if (iVar11 == 0) {
            uVar14 = 3;
            if (((iVar10 != 0) && (0 < local_28)) &&
               (uVar16 = thunk_FUN_0048d86c(iVar10), 0 < (int)uVar16)) {
              uVar14 = uVar16;
            }
            puVar6 = DAT_0058284c;
            if (0x14 < uVar14) {
              uVar14 = 0x14;
            }
            FUN_0043c0e4(DAT_0058284c,0xaa8,0);
            *puVar6 = (short)uVar14;
            *(undefined4 *)(puVar6 + 0x552) = 1;
            for (uVar16 = 0; puVar2 = DAT_00582818, uVar16 < uVar14; uVar16 = uVar16 + 1) {
              *(uint *)(puVar6 + uVar16 * 0x44 + 2) = uVar16 + 1;
              uVar17 = FUN_0044b728(puVar6 + uVar16 * 0x44 + 5,0x80,DAT_00582850,uVar16 + 1);
              if (0x7f < uVar17) {
                uVar17 = 0x7f;
              }
              puVar6[uVar16 * 0x44 + 4] = (short)uVar17;
            }
            FUN_0043c0e4(DAT_00582818,0xfac,0);
            *puVar2 = 3;
            pcVar1 = DAT_0058281c;
            *DAT_0058281c = *DAT_0058281c + '\x01';
            puVar2[1] = *pcVar1;
            *(undefined2 *)(puVar2 + 2) = 5;
            FUN_00439c04(puVar2 + 4,puVar6,0xaa8);
            FUN_00581de0(puVar2);
            FUN_004733ee(DAT_00582854,uVar14);
          }
          else {
            iVar9 = FUN_0044b610(iVar9,DAT_00582858,5);
            if (iVar9 == 0) {
              FUN_004733ee(DAT_0058285c);
              for (uVar18 = 0; uVar14 = FUN_0059674e(), uVar18 < uVar14; uVar18 = uVar18 + 1) {
                iVar9 = FUN_005964e2(uVar18);
                FUN_004733ee(DAT_00582860,*(undefined4 *)(iVar9 + 4),*(undefined4 *)(iVar9 + 8));
              }
            }
          }
        }
      }
    }
  }
  return 0;
}

