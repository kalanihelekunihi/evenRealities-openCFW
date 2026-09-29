
uint FUN_00483960(code *param_1,int param_2,uint param_3,char *param_4,uint *param_5)

{
  char cVar1;
  int iVar2;
  int *piVar3;
  undefined4 *puVar4;
  undefined8 *puVar5;
  int iVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  undefined4 uVar13;
  char *pcVar14;
  bool bVar15;
  bool bVar16;
  char *local_28;
  
  uVar9 = 0;
  local_28 = param_4;
  if (param_2 == 0) {
    param_1 = DAT_0048400c;
  }
LAB_0048398e:
  while( true ) {
    while( true ) {
      if (*local_28 == '\0') {
        uVar11 = uVar9;
        if (param_3 <= uVar9) {
          uVar11 = param_3 - 1;
        }
        (*param_1)(0,param_2,uVar11,param_3);
        return uVar9;
      }
      if (*local_28 == '%') break;
      (*param_1)(*local_28,param_2,uVar9,param_3);
      uVar9 = uVar9 + 1;
      local_28 = local_28 + 1;
    }
    local_28 = local_28 + 1;
    uVar11 = 0;
    do {
      cVar1 = *local_28;
      if (cVar1 == ' ') {
        uVar11 = uVar11 | 8;
        local_28 = local_28 + 1;
        bVar15 = true;
      }
      else if (cVar1 == '#') {
        uVar11 = uVar11 | 0x10;
        local_28 = local_28 + 1;
        bVar15 = true;
      }
      else if (cVar1 == '+') {
        uVar11 = uVar11 | 4;
        local_28 = local_28 + 1;
        bVar15 = true;
      }
      else if (cVar1 == '-') {
        uVar11 = uVar11 | 2;
        local_28 = local_28 + 1;
        bVar15 = true;
      }
      else if (cVar1 == '0') {
        uVar11 = uVar11 | 1;
        local_28 = local_28 + 1;
        bVar15 = true;
      }
      else {
        bVar15 = false;
      }
    } while (bVar15);
    uVar10 = 0;
    iVar2 = FUN_00483032(*local_28);
    if (iVar2 == 0) {
      if (*local_28 == '*') {
        uVar10 = *param_5;
        param_5 = param_5 + 1;
        if ((int)uVar10 < 0) {
          uVar11 = uVar11 | 2;
          uVar10 = -uVar10;
        }
        local_28 = local_28 + 1;
      }
    }
    else {
      uVar10 = FUN_00483044(&local_28);
    }
    uVar7 = 0;
    if (*local_28 == '.') {
      uVar11 = uVar11 | 0x400;
      local_28 = local_28 + 1;
      iVar2 = FUN_00483032(*local_28);
      if (iVar2 == 0) {
        if (*local_28 == '*') {
          uVar7 = *param_5;
          param_5 = param_5 + 1;
          if ((int)uVar7 < 1) {
            uVar7 = 0;
          }
          local_28 = local_28 + 1;
        }
      }
      else {
        uVar7 = FUN_00483044(&local_28);
      }
    }
    cVar1 = *local_28;
    if (cVar1 == 'h') {
      uVar12 = uVar11 | 0x80;
      pcVar14 = local_28 + 1;
      if (local_28[1] == 'h') {
        uVar12 = uVar11 | 0xc0;
        pcVar14 = local_28 + 2;
      }
    }
    else if (cVar1 == 'j') {
      uVar12 = uVar11 | 0x200;
      pcVar14 = local_28 + 1;
    }
    else if (cVar1 == 'l') {
      uVar12 = uVar11 | 0x100;
      pcVar14 = local_28 + 1;
      if (local_28[1] == 'l') {
        uVar12 = uVar11 | 0x300;
        pcVar14 = local_28 + 2;
      }
    }
    else if (cVar1 == 't') {
      uVar12 = uVar11 | 0x100;
      pcVar14 = local_28 + 1;
    }
    else {
      uVar12 = uVar11;
      pcVar14 = local_28;
      if (cVar1 == 'z') {
        uVar12 = uVar11 | 0x100;
        pcVar14 = local_28 + 1;
      }
    }
    local_28 = pcVar14;
    cVar1 = *local_28;
    if (cVar1 != '%') break;
    (*param_1)(0x25,param_2,uVar9,param_3);
    uVar9 = uVar9 + 1;
    local_28 = local_28 + 1;
  }
  if (cVar1 != 'E') {
    if (cVar1 == 'F') {
LAB_00483e08:
      if (*local_28 == 'F') {
        uVar12 = uVar12 | 0x20;
      }
      puVar5 = (undefined8 *)((int)param_5 + 7U & 0xfffffff8);
      param_5 = (uint *)(puVar5 + 1);
      uVar9 = FUN_00483350((int)*puVar5,param_1,param_2,uVar9,param_3,uVar7,uVar10,uVar12);
      local_28 = local_28 + 1;
      goto LAB_0048398e;
    }
    if (cVar1 == 'G') goto LAB_00483e42;
    if (((cVar1 != 'P') && (cVar1 != 'X')) && (cVar1 != 'b')) {
      if (cVar1 == 'c') {
        uVar11 = 1;
        uVar7 = uVar11;
        if (-1 < (int)(uVar12 << 0x1e)) {
          while (uVar11 = uVar7 + 1, uVar7 < uVar10) {
            (*param_1)(0x20,param_2,uVar9,param_3);
            uVar9 = uVar9 + 1;
            uVar7 = uVar11;
          }
        }
        uVar7 = *param_5;
        param_5 = param_5 + 1;
        (*param_1)(uVar7 & 0xff,param_2,uVar9,param_3);
        uVar9 = uVar9 + 1;
        if ((int)(uVar12 << 0x1e) < 0) {
          while (uVar11 < uVar10) {
            (*param_1)(0x20,param_2,uVar9,param_3);
            uVar9 = uVar9 + 1;
            uVar11 = uVar11 + 1;
          }
        }
        local_28 = local_28 + 1;
        goto LAB_0048398e;
      }
      if (cVar1 == 'd') goto LAB_00483b68;
      if (cVar1 == 'e') goto LAB_00483e42;
      if (cVar1 == 'f') goto LAB_00483e08;
      if (cVar1 == 'g') goto LAB_00483e42;
      if (((cVar1 != 'i') && (cVar1 != 'o')) && (cVar1 != 'p')) {
        if (cVar1 == 's') {
          pcVar14 = (char *)*param_5;
          param_5 = param_5 + 1;
          uVar11 = uVar7;
          if (uVar7 == 0) {
            uVar11 = 0xffffffff;
          }
          uVar11 = FUN_00454770(pcVar14,uVar11);
          if (((int)(uVar12 << 0x15) < 0) && (uVar7 <= uVar11)) {
            uVar11 = uVar7;
          }
          uVar8 = uVar11;
          if (-1 < (int)(uVar12 << 0x1e)) {
            while (uVar11 = uVar8 + 1, uVar8 < uVar10) {
              (*param_1)(0x20,param_2,uVar9,param_3);
              uVar9 = uVar9 + 1;
              uVar8 = uVar11;
            }
          }
          while ((*pcVar14 != '\0' &&
                 ((uVar8 = uVar7, -1 < (int)(uVar12 << 0x15) || (uVar8 = uVar7 - 1, uVar7 != 0)))))
          {
            (*param_1)(*pcVar14,param_2,uVar9,param_3);
            pcVar14 = pcVar14 + 1;
            uVar7 = uVar8;
            uVar9 = uVar9 + 1;
          }
          if ((int)(uVar12 << 0x1e) < 0) {
            while (uVar11 < uVar10) {
              (*param_1)(0x20,param_2,uVar9,param_3);
              uVar9 = uVar9 + 1;
              uVar11 = uVar11 + 1;
            }
          }
          local_28 = local_28 + 1;
        }
        else {
          if ((cVar1 == 'u') || (cVar1 == 'x')) goto LAB_00483b68;
          (*param_1)(*local_28,param_2,uVar9,param_3);
          uVar9 = uVar9 + 1;
          local_28 = local_28 + 1;
        }
        goto LAB_0048398e;
      }
    }
LAB_00483b68:
    if ((*local_28 == 'x') || (*local_28 == 'X')) {
      uVar13 = 0x10;
    }
    else if ((*local_28 == 'p') || (*local_28 == 'P')) {
      uVar13 = 0x10;
      uVar12 = uVar12 | 0x110;
      if (local_28[1] == 'V') {
        local_28 = local_28 + 1;
      }
    }
    else if (*local_28 == 'o') {
      uVar13 = 8;
    }
    else if (*local_28 == 'b') {
      uVar13 = 2;
    }
    else {
      uVar13 = 10;
      uVar12 = uVar12 & 0xffffffef;
    }
    if ((*local_28 == 'X') || (*local_28 == 'P')) {
      uVar12 = uVar12 | 0x20;
    }
    if ((*local_28 != 'i') && (*local_28 != 'd')) {
      uVar12 = uVar12 & 0xfffffff3;
    }
    if ((int)(uVar12 << 0x15) < 0) {
      uVar12 = uVar12 & 0xfffffffe;
    }
    if ((*local_28 == 'i') || (*local_28 == 'd')) {
      if ((int)(uVar12 << 0x16) < 0) {
        piVar3 = (int *)((int)param_5 + 7U & 0xfffffff8);
        iVar2 = *piVar3;
        iVar6 = piVar3[1];
        param_5 = (uint *)(piVar3 + 2);
        bVar15 = iVar6 < 0;
        if ((iVar6 < 0) || ((iVar6 < 1 && (iVar2 == 0)))) {
          bVar16 = iVar2 != 0;
          iVar2 = -iVar2;
          iVar6 = -iVar6 - (uint)bVar16;
        }
        uVar9 = FUN_0048329c(param_1,param_2,uVar9,param_3,iVar2,iVar6,bVar15);
      }
      else if ((int)(uVar12 << 0x17) < 0) {
        uVar11 = *param_5;
        param_5 = param_5 + 1;
        bVar15 = (int)uVar11 < 0;
        if ((int)uVar11 < 1) {
          uVar11 = -uVar11;
        }
        uVar9 = FUN_0048320a(param_1,param_2,uVar9,param_3,uVar11,bVar15,uVar13,uVar7,uVar10,uVar12)
        ;
      }
      else {
        if ((int)(uVar12 << 0x19) < 0) {
          uVar11 = *param_5 & 0xff;
        }
        else if ((int)(uVar12 << 0x18) < 0) {
          uVar11 = (uint)(short)*param_5;
        }
        else {
          uVar11 = *param_5;
        }
        param_5 = param_5 + 1;
        bVar15 = (int)uVar11 < 0;
        if ((int)uVar11 < 1) {
          uVar11 = -uVar11;
        }
        uVar9 = FUN_0048320a(param_1,param_2,uVar9,param_3,uVar11,bVar15,uVar13,uVar7,uVar10,uVar12)
        ;
      }
    }
    else if (*local_28 == 'V') {
      puVar4 = (undefined4 *)*param_5;
      param_5 = param_5 + 1;
      iVar2 = FUN_00483960(param_1,param_2 + uVar9,param_3 - uVar9,*puVar4,*(undefined4 *)puVar4[1])
      ;
      uVar9 = iVar2 + uVar9;
    }
    else if ((int)(uVar12 << 0x16) < 0) {
      puVar4 = (undefined4 *)((int)param_5 + 7U & 0xfffffff8);
      param_5 = puVar4 + 2;
      uVar9 = FUN_0048329c(param_1,param_2,uVar9,param_3,*puVar4,puVar4[1],0);
    }
    else if ((int)(uVar12 << 0x17) < 0) {
      uVar11 = *param_5;
      param_5 = param_5 + 1;
      uVar9 = FUN_0048320a(param_1,param_2,uVar9,param_3,uVar11,0,uVar13,uVar7,uVar10,uVar12);
    }
    else {
      if ((int)(uVar12 << 0x19) < 0) {
        uVar11 = *param_5 & 0xff;
      }
      else if ((int)(uVar12 << 0x18) < 0) {
        uVar11 = *param_5 & 0xffff;
      }
      else {
        uVar11 = *param_5;
      }
      param_5 = param_5 + 1;
      uVar9 = FUN_0048320a(param_1,param_2,uVar9,param_3,uVar11,0,uVar13,uVar7,uVar10,uVar12);
    }
    local_28 = local_28 + 1;
    goto LAB_0048398e;
  }
LAB_00483e42:
  if ((*local_28 == 'g') || (*local_28 == 'G')) {
    uVar12 = uVar12 | 0x800;
  }
  if ((*local_28 == 'E') || (*local_28 == 'G')) {
    uVar12 = uVar12 | 0x20;
  }
  puVar5 = (undefined8 *)((int)param_5 + 7U & 0xfffffff8);
  param_5 = (uint *)(puVar5 + 1);
  uVar9 = FUN_0048364c((int)*puVar5,param_1,param_2,uVar9,param_3,uVar7,uVar10,uVar12);
  local_28 = local_28 + 1;
  goto LAB_0048398e;
}

