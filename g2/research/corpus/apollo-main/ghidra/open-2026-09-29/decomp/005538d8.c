
void FUN_005538d8(void)

{
  char cVar1;
  char cVar2;
  bool bVar3;
  bool bVar4;
  byte *pbVar5;
  int *piVar6;
  char cVar7;
  int iVar8;
  int iVar9;
  uint uVar10;
  int iVar11;
  undefined4 uVar12;
  undefined *puVar13;
  undefined4 in_r3;
  char *pcVar14;
  uint uVar15;
  char cVar16;
  char cVar17;
  char cVar18;
  undefined1 local_30;
  byte local_2f;
  undefined1 local_2e;
  undefined1 local_2d;
  undefined1 local_2c;
  undefined1 local_2b;
  undefined1 local_2a;
  undefined1 local_29;
  undefined4 uStack_28;
  
  pbVar5 = DAT_00553fe8;
  if (*DAT_00553d44 != '\0') {
    uStack_28 = in_r3;
    if ((*DAT_00553fe8 == 0) && (*DAT_0055400c == 0)) {
      iVar8 = osKernelGetTickCount();
      iVar11 = DAT_00553d60;
      iVar9 = FUN_00463fa4(*(undefined4 *)(DAT_00553d60 + (uint)*pbVar5 * 4));
      piVar6 = DAT_00554010;
      if (iVar9 == *(int *)(DAT_00553d5c + 0x1c) + -1) {
        if (*DAT_00554010 == 0) {
          *DAT_00554010 = iVar8;
        }
        else if (*(uint *)(DAT_00553d5c + 0x20) <= (uint)(iVar8 - *DAT_00554010)) {
          FUN_00463f5c(*(undefined4 *)(iVar11 + (uint)*pbVar5 * 4),2);
          *piVar6 = 0;
          return;
        }
      }
      else {
        *DAT_00554010 = 0;
      }
    }
    cVar7 = FUN_0045a568();
    if ((cVar7 == '\x02') && (*(int *)(DAT_00553d60 + (uint)*pbVar5 * 4) != 0)) {
      pcVar14 = (char *)(DAT_00553fec + (uint)*pbVar5 * 0x10);
      uVar10 = FUN_00463fa4(*(undefined4 *)(DAT_00553d60 + (uint)*pbVar5 * 4));
      uVar15 = (*(int *)(pcVar14 + 8) + 1) * 6;
      if ((uVar15 <= uVar10) && (*pcVar14 == '\0')) {
        *pcVar14 = '\x01';
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(4,DAT_00554000,DAT_00553ffc,DAT_00554018,0x174,DAT_00554014,uVar10,uVar15);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          compress_log_output(0x10800000,DAT_0055401c,DAT_0055401c,uVar10,uVar15);
        }
      }
      if (*pcVar14 != '\0') {
        return;
      }
    }
    iVar11 = DAT_00553d60;
    if (*(int *)(DAT_00553d60 + (uint)*pbVar5 * 4) != 0) {
      uVar10 = FUN_00463fa4(*(undefined4 *)(DAT_00553d60 + (uint)*pbVar5 * 4));
      cVar17 = *(char *)(*(int *)(iVar11 + (uint)*pbVar5 * 4) + 0x1a);
      cVar16 = *(char *)(*(int *)(iVar11 + (uint)*pbVar5 * 4) + 0x1b);
      cVar2 = *(char *)(*(int *)(iVar11 + (uint)*pbVar5 * 4) + 0x19);
      FUN_00463f34(*(undefined4 *)(iVar11 + (uint)*pbVar5 * 4));
      uVar15 = FUN_00463fa4(*(undefined4 *)(iVar11 + (uint)*pbVar5 * 4));
      cVar1 = *(char *)(*(int *)(iVar11 + (uint)*pbVar5 * 4) + 0x1a);
      cVar18 = *(char *)(*(int *)(iVar11 + (uint)*pbVar5 * 4) + 0x1b);
      if (cVar7 == '\x01') {
        iVar8 = DAT_00553fec + (uint)*pbVar5 * 0x10;
        bVar3 = false;
        bVar4 = false;
        if (cVar2 == '\0') {
          if (uVar15 < uVar10) {
            *(undefined4 *)(iVar8 + 4) = 0;
            bVar3 = true;
            bVar4 = true;
            iVar11 = FUN_0043d0ce();
            if (iVar11 << 0x1e < 0) {
              FUN_0043d574(4,DAT_00554000,DAT_00553ffc,DAT_00554018,0x199,DAT_00554020,uVar10,uVar15
                          );
            }
            iVar11 = FUN_0043d0ce();
            if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
              compress_log_output(0x10800000,DAT_00554024,DAT_00554024,uVar10,uVar15);
            }
          }
        }
        else if (cVar2 == '\x01') {
          if ((cVar16 == '\0') && (cVar18 != '\0')) {
            bVar3 = true;
            bVar4 = true;
            *(undefined1 *)(iVar8 + 0xd) = 1;
            iVar11 = FUN_0043d0ce();
            if (iVar11 << 0x1e < 0) {
              FUN_0043d574(4,DAT_00554000,DAT_00553ffc,DAT_00554018,0x1a2,DAT_00554028,uVar15);
            }
            iVar11 = FUN_0043d0ce();
            if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
              compress_log_output(0x10400000,DAT_0055402c,DAT_0055402c,uVar15);
            }
          }
        }
        else if ((cVar2 == '\x02') && (cVar17 != cVar1)) {
          if (cVar1 == '\0') {
            *(uint *)(iVar8 + 4) = (*(int *)(*(int *)(iVar11 + (uint)*pbVar5 * 4) + 8) - 1U) / 6;
          }
          else {
            *(undefined4 *)(iVar8 + 4) = 0;
          }
          bVar3 = true;
          bVar4 = true;
          *(char *)(iVar8 + 0xc) = cVar1;
          iVar11 = FUN_0043d0ce();
          if (iVar11 << 0x1e < 0) {
            uVar12 = DAT_00554034;
            if (cVar1 != '\0') {
              uVar12 = DAT_00554030;
            }
            FUN_0043d574(4,DAT_00554000,DAT_00553ffc,DAT_00554018,0x1b4,DAT_00554038,uVar12,uVar15);
          }
          iVar11 = FUN_0043d0ce();
          if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
            uVar12 = DAT_00554034;
            if (cVar1 != '\0') {
              uVar12 = DAT_00554030;
            }
            compress_log_output(0x10800000,DAT_0055403c,DAT_0055403c,uVar12,uVar15);
          }
        }
        if (((((!bVar4) && (uVar15 != uVar10)) && (uVar10 = uVar15 / 6, uVar15 != 0)) &&
            (uVar15 % 6 == 0)) &&
           ((*(uint *)(iVar8 + 4) < uVar10 || (uVar10 < *(uint *)(iVar8 + 4))))) {
          bVar3 = true;
          *(uint *)(iVar8 + 4) = uVar10;
        }
        if (bVar3) {
          local_30 = 6;
          local_2f = *pbVar5;
          local_2e = (undefined1)uVar15;
          local_2d = (undefined1)(uVar15 >> 8);
          local_2c = (undefined1)(uVar15 >> 0x10);
          local_2b = (undefined1)(uVar15 >> 0x18);
          local_2a = cVar1 != '\0';
          local_29 = cVar18 != '\0';
          FUN_00464bb2(7,&local_30,8,0);
          if (!bVar4) {
            iVar11 = FUN_0043d0ce();
            if (iVar11 << 0x1e < 0) {
              if (cVar1 == '\0') {
                puVar13 = &DAT_00553d40;
              }
              else {
                puVar13 = &DAT_00553d3c;
              }
              FUN_0043d574(4,DAT_00554000,DAT_00553ffc,DAT_00554018,0x1d7,DAT_00554040,*pbVar5,
                           uVar15,*(undefined4 *)(iVar8 + 4),puVar13);
            }
            iVar11 = FUN_0043d0ce();
            if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
              if (cVar1 == '\0') {
                puVar13 = &DAT_00553d40;
              }
              else {
                puVar13 = &DAT_00553d3c;
              }
              compress_log_output(0x11000000,DAT_00554044,DAT_00554044,*pbVar5,uVar15,
                                  *(undefined4 *)(iVar8 + 4),puVar13);
            }
          }
        }
      }
    }
    *DAT_0055400c = *pbVar5;
  }
  return;
}

