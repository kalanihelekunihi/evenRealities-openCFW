
/* WARNING: Restarted to delay deadcode elimination for space: register */

void FUN_1000691c(char *param_1,undefined4 param_2,int param_3,int param_4,int param_5,int param_6,
                 byte param_7)

{
  bool bVar1;
  byte bVar2;
  longlong lVar3;
  int iVar4;
  uint uVar5;
  char cVar6;
  uint uVar7;
  char *pcVar8;
  int iVar9;
  int iVar10;
  char *pcVar11;
  char *pcVar12;
  byte bVar13;
  uint uVar14;
  int iVar15;
  int iVar16;
  byte *pbVar17;
  uint uVar18;
  char acStack_71 [69];
  
  bVar1 = (param_7 & 0x40) != 0;
  bVar13 = param_7 & 0x10;
  bVar2 = param_7 & 0x20;
  if (bVar13 != 0) {
    param_7 = param_7 & 0xfe;
  }
  cVar6 = '\0';
  lVar3 = CONCAT44(param_3,param_2);
  if ((param_7 & 2) != 0) {
    if (param_3 < 0) {
      param_5 = param_5 + -1;
      cVar6 = '-';
      lVar3 = -CONCAT44(param_3,param_2);
    }
    else if ((param_7 & 4) == 0) {
      cVar6 = '\0';
      lVar3 = CONCAT44(param_3,param_2);
      if ((param_7 & 8) != 0) {
        param_5 = param_5 + -1;
        cVar6 = ' ';
        lVar3 = CONCAT44(param_3,param_2);
      }
    }
    else {
      param_5 = param_5 + -1;
      cVar6 = '+';
      lVar3 = CONCAT44(param_3,param_2);
    }
  }
  pbVar17 = (byte *)(acStack_71 + 1);
  if (bVar1 && param_4 != 10) {
    if (param_4 != 0x10) {
      param_5 = param_5 + -1;
      goto LAB_10006978;
    }
    param_5 = param_5 + -2;
    if (lVar3 != 0) {
      uVar18 = 0xf;
      iVar16 = 4;
LAB_1000699c:
      iVar4 = 0;
      do {
        iVar15 = iVar4;
        uVar14 = (uint)((ulonglong)lVar3 >> 0x20);
        *pbVar17 = PTR_s_0123456789ABCDEF<NULL>_10006b3c[(uint)lVar3 & 0xff & uVar18] | bVar2;
        pbVar17 = pbVar17 + 1;
        uVar7 = uVar14 >> iVar16;
        uVar5 = (uint)lVar3 >> iVar16 | (uVar14 << 1) << (0x1fU - iVar16 & 0x3f);
        if ((iVar16 - 0x20U & 0x80000000) == 0) {
          uVar7 = 0;
          uVar5 = uVar14 >> (iVar16 - 0x20U & 0x3f);
        }
        lVar3 = CONCAT44(uVar7,uVar5);
        iVar4 = iVar15 + 1;
      } while (uVar7 != 0 || uVar5 != 0);
      iVar16 = (uint)(iVar4 < param_6) * param_6 + (uint)(iVar4 >= param_6) * iVar4;
      param_5 = param_5 - iVar16;
      goto joined_r0x10006ab6;
    }
LAB_10006a9e:
    acStack_71[1] = 0x30;
    iVar15 = 0;
    iVar4 = 1;
  }
  else {
LAB_10006978:
    if (lVar3 == 0) goto LAB_10006a9e;
    if (param_4 != 10) {
      iVar16 = 4;
      uVar18 = param_4 - 1;
      if (param_4 == 0x10) {
        uVar18 = 0xf;
      }
      else {
        iVar16 = 3;
      }
      goto LAB_1000699c;
    }
    iVar4 = FUN_10006774(acStack_71 + 1,(int)lVar3,(int)((ulonglong)lVar3 >> 0x20));
    iVar4 = iVar4 - (int)(acStack_71 + 1);
    iVar15 = iVar4 + -1;
  }
  iVar16 = (uint)(iVar4 < param_6) * param_6 + (uint)(iVar4 >= param_6) * iVar4;
  param_5 = param_5 - iVar16;
joined_r0x10006ab6:
  iVar9 = param_5;
  if (((param_7 & 0x11) == 0) && (iVar9 = param_5 + -1, -1 < iVar9)) {
    pcVar12 = param_1 + param_5;
    do {
      *param_1 = ' ';
      param_1 = param_1 + 1;
    } while (pcVar12 != param_1);
    iVar9 = -1;
    param_1 = pcVar12;
  }
  if (cVar6 != '\0') {
    *param_1 = cVar6;
    param_1 = param_1 + 1;
  }
  if (bVar1 && param_4 != 10) {
    *param_1 = '0';
    if (param_4 == 0x10) {
      param_1[1] = bVar2 | 0x58;
      param_1 = param_1 + 2;
    }
    else {
      param_1 = param_1 + 1;
    }
  }
  iVar10 = iVar9;
  if (bVar13 == 0) {
    cVar6 = ' ';
    if ((param_7 & 1) != 0) {
      cVar6 = '0';
    }
    iVar10 = iVar9 + -1;
    if (-1 < iVar10) {
      pcVar12 = param_1 + iVar9;
      do {
        *param_1 = cVar6;
        param_1 = param_1 + 1;
      } while (pcVar12 != param_1);
      iVar10 = -1;
      param_1 = pcVar12;
    }
  }
  pcVar12 = param_1;
  if (iVar4 < iVar16) {
    pcVar12 = param_1 + (iVar16 - iVar4);
    do {
      *param_1 = '0';
      param_1 = param_1 + 1;
    } while (pcVar12 != param_1);
  }
  if (-1 < iVar15) {
    pcVar11 = acStack_71 + iVar15 + 1;
    pcVar8 = pcVar12;
    do {
      cVar6 = *pcVar11;
      pcVar11 = pcVar11 + -1;
      *pcVar8 = cVar6;
      pcVar8 = pcVar8 + 1;
    } while (pcVar11 != acStack_71);
    pcVar12 = pcVar12 + iVar15 + 1;
  }
  if (0 < iVar10) {
    pcVar8 = pcVar12 + iVar10;
    do {
      *pcVar12 = ' ';
      pcVar12 = pcVar12 + 1;
    } while (pcVar8 != pcVar12);
  }
  return;
}

