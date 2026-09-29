
int FUN_00415bf6(char *param_1,char *param_2,double *param_3,undefined4 param_4)

{
  char cVar1;
  uint uVar2;
  uint *puVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  char *pcVar7;
  char *pcVar8;
  uint uVar9;
  int iVar10;
  uint uVar11;
  bool bVar12;
  bool bVar13;
  double dVar14;
  char local_38;
  undefined1 local_37;
  int local_34;
  uint local_30;
  uint uStack_2c;
  undefined4 uStack_28;
  
  iVar10 = 0;
  uStack_28 = param_4;
  do {
    while( true ) {
      if (*param_2 == '\0') {
        if (param_1 != (char *)0x0) {
          *param_1 = '\0';
        }
        return iVar10;
      }
      uVar11 = 0xffffffff;
      if (*param_2 == '%') break;
      if (param_1 != (char *)0x0) {
        if ((*param_2 == '\n') && (*DAT_00415fe0 != '\0')) {
          *param_1 = '\r';
          param_1 = param_1 + 1;
          iVar10 = iVar10 + 1;
        }
        *param_1 = *param_2;
        param_1 = param_1 + 1;
      }
      param_2 = param_2 + 1;
      iVar10 = iVar10 + 1;
    }
    pcVar7 = param_2 + 1;
    bVar12 = false;
    local_37 = 0;
    local_38 = ' ';
    if (*pcVar7 == '0') {
      local_38 = '0';
      pcVar7 = param_2 + 2;
    }
    uVar2 = FUN_0041595c(pcVar7,&local_34);
    pcVar7 = pcVar7 + local_34;
    if ((*pcVar7 != 's') && ((int)uVar2 < 0)) {
      uVar2 = -uVar2;
    }
    if (*pcVar7 == '.') {
      pcVar8 = pcVar7 + 1;
      if (*pcVar8 == '*') {
        uVar11 = *(uint *)param_3;
        param_3 = (double *)((int)param_3 + 4);
        pcVar7 = pcVar7 + 2;
      }
      else {
        uVar11 = FUN_0041595c(pcVar8,&local_34);
        pcVar7 = pcVar8 + local_34;
      }
    }
    param_2 = pcVar7;
    if ((*pcVar7 == 'l') && (param_2 = pcVar7 + 1, *param_2 == 'l')) {
      param_2 = pcVar7 + 2;
      bVar12 = true;
    }
    cVar1 = *param_2;
    if (cVar1 == 'F') {
LAB_00415f40:
      if (param_1 != (char *)0x0) {
        param_3 = (double *)((int)param_3 + 7U & 0xfffffff8);
        dVar14 = *param_3;
        param_3 = param_3 + 1;
        param_1[0] = '\x14';
        param_1[1] = '\0';
        param_1[2] = '\0';
        param_1[3] = '\0';
        iVar4 = FUN_00415ab6((float)dVar14,param_1,uVar11);
        if (iVar4 < 0) {
          uVar6 = DAT_00415fe4;
          if ((iVar4 != -1) && (uVar6 = DAT_00415fec, iVar4 == -2)) {
            uVar6 = DAT_00415fe8;
          }
          *(undefined4 *)param_1 = uVar6;
          iVar4 = 3;
        }
        iVar10 = iVar4 + iVar10;
        param_1 = param_1 + iVar4;
      }
    }
    else if (cVar1 == 'X') {
LAB_00415daa:
      if (bVar12) {
        puVar3 = (uint *)((int)param_3 + 7U & 0xfffffff8);
        uVar11 = *puVar3;
        uVar9 = puVar3[1];
        param_3 = (double *)(puVar3 + 2);
      }
      else {
        uVar11 = *(uint *)param_3;
        param_3 = (double *)((int)param_3 + 4);
        uVar9 = 0;
      }
      if (uVar2 != 0) {
        iVar4 = FUN_00415936(uVar11,uVar9);
        iVar5 = FUN_00415a94(param_1,local_38,uVar2 - iVar4);
        iVar4 = iVar5;
        if (param_1 == (char *)0x0) {
          iVar4 = 0;
        }
        param_1 = param_1 + iVar4;
        iVar10 = iVar5 + iVar10;
      }
      iVar4 = FUN_00415a08(uVar11,uVar9,param_1,local_37);
      if (param_1 != (char *)0x0) {
        param_1 = param_1 + iVar4;
      }
      iVar10 = iVar4 + iVar10;
    }
    else if (cVar1 == 'c') {
      uVar11 = *(uint *)param_3;
      param_3 = (double *)((int)param_3 + 4);
      if (param_1 != (char *)0x0) {
        *param_1 = (char)uVar11;
        param_1 = param_1 + 1;
      }
      iVar10 = iVar10 + 1;
    }
    else {
      if (cVar1 != 'd') {
        if (cVar1 == 'f') goto LAB_00415f40;
        if (cVar1 != 'i') {
          if (cVar1 == 's') {
            pcVar7 = *(char **)param_3;
            param_3 = (double *)((int)param_3 + 4);
            uVar9 = FUN_00415a7c(pcVar7);
            if ((-1 < (int)uVar11) && (uVar11 < uVar9)) {
              uVar9 = uVar11;
            }
            if ((0 < (int)uVar2) && (uVar9 < uVar2)) {
              iVar5 = FUN_00415a94(param_1,local_38,uVar2 - uVar9);
              iVar4 = iVar5;
              if (param_1 == (char *)0x0) {
                iVar4 = 0;
              }
              param_1 = param_1 + iVar4;
              iVar10 = iVar5 + iVar10;
              uVar2 = 0;
            }
            for (; (*pcVar7 != '\0' && (uVar9 != 0)); uVar9 = uVar9 - 1) {
              if (param_1 != (char *)0x0) {
                *param_1 = *pcVar7;
                param_1 = param_1 + 1;
              }
              pcVar7 = pcVar7 + 1;
              iVar10 = iVar10 + 1;
            }
            if ((uVar2 != 0) && (uVar9 < -uVar2)) {
              iVar5 = FUN_00415a94(param_1,local_38,-uVar2 - uVar9);
              iVar4 = iVar5;
              if (param_1 == (char *)0x0) {
                iVar4 = 0;
              }
              param_1 = param_1 + iVar4;
              iVar10 = iVar5 + iVar10;
            }
          }
          else if (cVar1 == 'u') {
            if (bVar12) {
              puVar3 = (uint *)((int)param_3 + 7U & 0xfffffff8);
              uVar11 = *puVar3;
              uVar9 = puVar3[1];
              param_3 = (double *)(puVar3 + 2);
            }
            else {
              uVar11 = *(uint *)param_3;
              param_3 = (double *)((int)param_3 + 4);
              uVar9 = 0;
            }
            if (uVar2 != 0) {
              iVar4 = FUN_00415900(uVar11,uVar9);
              iVar5 = FUN_00415a94(param_1,local_38,uVar2 - iVar4);
              iVar4 = iVar5;
              if (param_1 == (char *)0x0) {
                iVar4 = 0;
              }
              param_1 = param_1 + iVar4;
              iVar10 = iVar5 + iVar10;
            }
            iVar4 = FUN_004159a0(uVar11,uVar9,param_1);
            if (param_1 != (char *)0x0) {
              param_1 = param_1 + iVar4;
            }
            iVar10 = iVar4 + iVar10;
          }
          else {
            if (cVar1 == 'x') {
              local_37 = 1;
              goto LAB_00415daa;
            }
            if (param_1 != (char *)0x0) {
              *param_1 = *param_2;
              param_1 = param_1 + 1;
            }
            iVar10 = iVar10 + 1;
          }
          goto LAB_00415f98;
        }
      }
      if (bVar12) {
        puVar3 = (uint *)((int)param_3 + 7U & 0xfffffff8);
        local_30 = *puVar3;
        uStack_2c = puVar3[1];
        param_3 = (double *)(puVar3 + 2);
      }
      else {
        local_30 = *(uint *)param_3;
        param_3 = (double *)((int)param_3 + 4);
        uStack_2c = (int)local_30 >> 0x1f;
      }
      bVar12 = (int)uStack_2c < 0;
      if (bVar12) {
        bVar13 = local_30 != 0;
        local_30 = -local_30;
        uStack_2c = -uStack_2c - (uint)bVar13;
      }
      if (uVar2 == 0) {
        if (bVar12) {
          if (param_1 != (char *)0x0) {
            *param_1 = '-';
            param_1 = param_1 + 1;
          }
          iVar10 = iVar10 + 1;
        }
      }
      else {
        iVar4 = FUN_00415924(local_30,uStack_2c);
        iVar4 = uVar2 - iVar4;
        if ((bVar12) && (iVar4 = iVar4 + -1, local_38 == '0')) {
          if (param_1 != (char *)0x0) {
            *param_1 = '-';
            param_1 = param_1 + 1;
          }
          iVar10 = iVar10 + 1;
        }
        iVar5 = FUN_00415a94(param_1,local_38,iVar4);
        iVar4 = iVar5;
        if (param_1 == (char *)0x0) {
          iVar4 = 0;
        }
        param_1 = param_1 + iVar4;
        iVar10 = iVar5 + iVar10;
        if ((bVar12) && (local_38 == ' ')) {
          if (param_1 != (char *)0x0) {
            *param_1 = '-';
            param_1 = param_1 + 1;
          }
          iVar10 = iVar10 + 1;
        }
      }
      iVar4 = FUN_004159a0(local_30,uStack_2c,param_1);
      if (param_1 != (char *)0x0) {
        param_1 = param_1 + iVar4;
      }
      iVar10 = iVar4 + iVar10;
    }
LAB_00415f98:
    param_2 = param_2 + 1;
  } while( true );
}

