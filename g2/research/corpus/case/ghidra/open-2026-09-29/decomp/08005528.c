
undefined4
case_configure_system_clock(byte *param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  uint *puVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  bool bVar8;
  bool bVar9;
  undefined8 uVar10;
  
  bVar8 = param_1 == (byte *)0x0;
LAB_0800552c:
  do {
    puVar1 = DAT_080058ec;
    if (bVar8) {
      return 1;
    }
    if ((*param_1 & 1) == 0) break;
    param_2 = DAT_080058ec[3] & 3;
    if ((DAT_080058ec[2] & 0x38) == 0x10) {
      if (param_2 != 3) goto LAB_08005552;
    }
    else if ((DAT_080058ec[2] & 0x38) != 8) {
LAB_08005552:
      if (*(int *)(param_1 + 4) == 0x10000) {
LAB_0800555c:
        *puVar1 = *puVar1 | 0x10000;
      }
      else {
        if (*(int *)(param_1 + 4) == 0x50000) {
          *DAT_080058ec = *DAT_080058ec | 0x40000;
          goto LAB_0800555c;
        }
        *DAT_080058ec = *DAT_080058ec & 0xfffeffff;
        *puVar1 = *puVar1 & 0xfffbffff;
      }
      if (*(int *)(param_1 + 4) != 0) {
        uVar10 = case_tick_word2();
        goto LAB_080055a8;
      }
      uVar10 = case_tick_word2();
      param_2 = (uint)((ulonglong)uVar10 >> 0x20);
      iVar3 = (int)uVar10;
      while ((int)(*puVar1 << 0xe) < 0) {
        uVar10 = case_tick_word2();
        param_2 = (uint)((ulonglong)uVar10 >> 0x20);
        uVar2 = (int)uVar10 - iVar3;
        bVar9 = 99 < uVar2;
        bVar8 = uVar2 == 100;
        if (100 < uVar2) goto LAB_080055a6;
      }
      break;
    }
  } while (((int)(*DAT_080058ec << 0xe) < 0) && (bVar8 = true, *(int *)(param_1 + 4) == 0));
  while ((int)((uint)*param_1 << 0x1e) < 0) {
    uVar2 = puVar1[2] & 0x38;
    param_2 = 0x3800;
    if (uVar2 == 0x10) {
      if ((puVar1[3] & 3) == 2) goto LAB_0800560c;
    }
    else if (uVar2 == 0) {
LAB_0800560c:
      if (-1 < (int)(*puVar1 << 0x15)) goto LAB_08005618;
      bVar9 = *(int *)(param_1 + 0xc) == 0;
      goto LAB_08005616;
    }
    if (*(int *)(param_1 + 0xc) == 0) {
      *puVar1 = *puVar1 & 0xfffffeff;
      uVar10 = case_tick_word2();
      param_2 = (uint)((ulonglong)uVar10 >> 0x20);
      iVar3 = (int)uVar10;
      do {
        if (-1 < (int)(*puVar1 << 0x15)) goto LAB_080056a2;
        uVar10 = case_tick_word2();
        param_2 = (uint)((ulonglong)uVar10 >> 0x20);
        uVar2 = (int)uVar10 - iVar3;
        bVar9 = 1 < uVar2;
        bVar8 = uVar2 == 2;
      } while (uVar2 < 3);
    }
    else {
      *puVar1 = *puVar1 & 0xffffc7ff | *(uint *)(param_1 + 0x10);
      *puVar1 = *puVar1 | 0x100;
      iVar3 = case_tick_word2();
      do {
        if ((int)(*puVar1 << 0x15) < 0) {
          param_2 = *(int *)(param_1 + 0x14) << 8;
          puVar1[1] = puVar1[1] & 0xffff80ff | param_2;
          goto LAB_080056a2;
        }
        uVar10 = case_tick_word2();
        param_2 = (uint)((ulonglong)uVar10 >> 0x20);
        uVar2 = (int)uVar10 - iVar3;
        bVar9 = 1 < uVar2;
        bVar8 = uVar2 == 2;
      } while (uVar2 < 3);
    }
LAB_080055a6:
    while( true ) {
      uVar10 = CONCAT44(param_2,iVar3);
      if (bVar9 && !bVar8) {
        return 3;
      }
LAB_080055a8:
      param_2 = (uint)((ulonglong)uVar10 >> 0x20);
      iVar3 = (int)uVar10;
      if ((int)(*puVar1 << 0xe) < 0) break;
      uVar10 = case_tick_word2();
      param_2 = (uint)((ulonglong)uVar10 >> 0x20);
      uVar2 = (int)uVar10 - iVar3;
      bVar9 = 99 < uVar2;
      bVar8 = uVar2 == 100;
    }
  }
LAB_080056a2:
  do {
    iVar3 = DAT_080058fc;
    if (-1 < (int)((uint)*param_1 << 0x1c)) goto LAB_08005708;
    if ((puVar1[2] & 0x3f) >> 3 != 3) {
      if (*(int *)(param_1 + 0x18) == 0) {
        *(uint *)(DAT_080058fc + 0x20) = *(uint *)(DAT_080058fc + 0x20) & 0xfffffffe;
        iVar5 = case_tick_word2();
        while (*(int *)(iVar3 + 0x20) << 0x1e < 0) {
          iVar6 = case_tick_word2();
          if (2 < (uint)(iVar6 - iVar5)) {
            return 3;
          }
        }
      }
      else {
        *(uint *)(DAT_080058fc + 0x20) = *(uint *)(DAT_080058fc + 0x20) | 1;
        iVar5 = case_tick_word2();
        while (-1 < *(int *)(iVar3 + 0x20) << 0x1e) {
          iVar6 = case_tick_word2();
          if (2 < (uint)(iVar6 - iVar5)) {
            return 3;
          }
        }
      }
LAB_08005708:
      if (-1 < (int)((uint)*param_1 << 0x1d)) goto LAB_080057e8;
      if ((puVar1[2] & 0x3f) >> 3 == 4) {
        if ((*(int *)(iVar3 + 0x1c) << 0x1e < 0) && (*(int *)(param_1 + 8) == 0)) {
          return 1;
        }
        goto LAB_080057e8;
      }
      bVar8 = -1 < (int)(puVar1[0xf] << 3);
      if (bVar8) {
        puVar1[0xf] = puVar1[0xf] | 0x10000000;
      }
      if (-1 < (int)(*DAT_08005900 << 0x17)) {
        *DAT_08005900 = *DAT_08005900 | (int)DAT_08005900 >> 0x16;
        iVar5 = case_tick_word2();
        while (-1 < (int)(*DAT_08005900 << 0x17)) {
          iVar6 = case_tick_word2();
          if (2 < (uint)(iVar6 - iVar5)) {
            return 3;
          }
        }
      }
      if (*(int *)(param_1 + 8) == 1) {
LAB_08005796:
        *(uint *)(iVar3 + 0x1c) = *(uint *)(iVar3 + 0x1c) | 1;
      }
      else {
        if (*(int *)(param_1 + 8) == 5) {
          *(uint *)(iVar3 + 0x1c) = *(uint *)(iVar3 + 0x1c) | 4;
          goto LAB_08005796;
        }
        *(uint *)(iVar3 + 0x1c) = *(uint *)(iVar3 + 0x1c) & 0xfffffffe;
        *(uint *)(iVar3 + 0x1c) = *(uint *)(iVar3 + 0x1c) & 0xfffffffb;
      }
      if (*(int *)(param_1 + 8) == 0) {
        iVar5 = case_tick_word2();
        while (*(int *)(iVar3 + 0x1c) << 0x1e < 0) {
          iVar6 = case_tick_word2();
          if (DAT_08005904 < (uint)(iVar6 - iVar5)) {
            return 3;
          }
        }
      }
      else {
        iVar5 = case_tick_word2();
        while (-1 < *(int *)(iVar3 + 0x1c) << 0x1e) {
          iVar6 = case_tick_word2();
          if (DAT_08005904 < (uint)(iVar6 - iVar5)) {
            return 3;
          }
        }
      }
      if (bVar8) {
        puVar1[0xf] = puVar1[0xf] & 0xefffffff;
      }
LAB_080057e8:
      iVar3 = *(int *)(param_1 + 0x1c);
      if (iVar3 == 0) {
        return 0;
      }
      if ((puVar1[2] & 0x3f) >> 3 != 2) {
        if (iVar3 == 2) {
          *puVar1 = *puVar1 & 0xfeffffff;
          iVar3 = case_tick_word2();
          do {
            if (-1 < (int)(*puVar1 << 6)) {
              puVar1[3] = *(uint *)(param_1 + 0x20) | *(uint *)(param_1 + 0x24) |
                          *(uint *)(param_1 + 0x2c) | *(int *)(param_1 + 0x28) << 8 |
                          *(uint *)(param_1 + 0x30) | *(uint *)(param_1 + 0x34) |
                          puVar1[3] & DAT_08005908;
              *puVar1 = *puVar1 | 0x1000000;
              puVar1[3] = puVar1[3] | 0x10000000;
              iVar3 = case_tick_word2();
              do {
                if ((int)(*puVar1 << 6) < 0) {
                  return 0;
                }
                iVar5 = case_tick_word2();
              } while ((uint)(iVar5 - iVar3) < 3);
              return 3;
            }
            iVar5 = case_tick_word2();
          } while ((uint)(iVar5 - iVar3) < 3);
        }
        else {
          *puVar1 = *puVar1 & 0xfeffffff;
          iVar3 = case_tick_word2();
          do {
            if (-1 < (int)(*puVar1 << 6)) {
              puVar1[3] = puVar1[3] & DAT_0800590c;
              return 0;
            }
            iVar5 = case_tick_word2();
          } while ((uint)(iVar5 - iVar3) < 3);
        }
        return 3;
      }
      if (iVar3 == 1) {
        return 1;
      }
      uVar2 = puVar1[3];
      if (((((uVar2 & 3) == *(uint *)(param_1 + 0x20)) &&
           ((uVar2 & 0x70) == *(uint *)(param_1 + 0x24))) &&
          ((uVar2 & 0x7f00) == *(int *)(param_1 + 0x28) * 0x100)) &&
         ((((uVar2 & 0x3e0000) == *(uint *)(param_1 + 0x2c) &&
           ((uVar2 & 0xe000000) == *(uint *)(param_1 + 0x30))) &&
          ((uVar2 & 0xe0000000) == *(uint *)(param_1 + 0x34))))) {
        return 0;
      }
      return 1;
    }
    if (-1 < *(int *)(DAT_080058fc + 0x20) << 0x1e) goto LAB_08005708;
    bVar9 = *(int *)(param_1 + 0x18) == 0;
    uVar2 = 0;
    if (!bVar9) goto LAB_08005708;
LAB_08005616:
    bVar8 = true;
    if (bVar9) goto LAB_0800552c;
LAB_08005618:
    iVar3 = *(int *)(param_1 + 0x14);
    uVar7 = puVar1[1] & 0xffff80ff | iVar3 << 8;
    puVar1[1] = uVar7;
    if (uVar2 == 0) {
      *puVar1 = *puVar1 & ~param_2 | *(uint *)(param_1 + 0x10);
      uVar4 = __aeabi_uidiv(DAT_080058f0,1 << ((*puVar1 & 0x3fff) >> 0xb),uVar7,iVar3 << 8,param_4);
      *DAT_080058f4 = uVar4;
    }
    uVar10 = case_initialize_interrupt_path(*DAT_080058f8);
    param_2 = (uint)((ulonglong)uVar10 >> 0x20);
    if ((int)uVar10 != 0) {
      return 1;
    }
  } while( true );
}

