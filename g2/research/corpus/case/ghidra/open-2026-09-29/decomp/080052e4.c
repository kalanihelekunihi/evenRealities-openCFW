
undefined4 case_configure_clock_path(byte *param_1,uint param_2)

{
  uint *puVar1;
  int *piVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  undefined4 uVar6;
  
  puVar1 = DAT_08005424;
  if (param_1 == (byte *)0x0) {
    return 1;
  }
  if ((*DAT_08005424 & 7) < param_2) {
    *DAT_08005424 = *DAT_08005424 & 0xfffffff8 | param_2;
    iVar3 = case_tick_word2();
    do {
      if ((*puVar1 & 7) == param_2) goto LAB_08005320;
      iVar5 = case_tick_word2();
    } while ((uint)(iVar5 - iVar3) <= DAT_08005428);
  }
  else {
LAB_08005320:
    piVar2 = DAT_0800542c;
    if (*(int *)param_1 << 0x1e < 0) {
      if (*(int *)param_1 << 0x1d < 0) {
        DAT_0800542c[2] = DAT_0800542c[2] | 0x7000;
      }
      piVar2[2] = piVar2[2] & 0xfffff0ffU | *(uint *)(param_1 + 8);
    }
    if ((*param_1 & 1) == 0) {
LAB_080053b0:
      if ((*puVar1 & 7) <= param_2) {
LAB_080053ea:
        if ((int)((uint)*param_1 << 0x1d) < 0) {
          piVar2[2] = piVar2[2] & 0xffff8fffU | *(uint *)(param_1 + 0xc);
        }
        uVar4 = case_derive_clock();
        *DAT_08005434 = uVar4 >> (*(byte *)(DAT_08005430 + ((uint)piVar2[2] >> 6 & 0x3c)) & 0x1f);
        uVar6 = case_initialize_interrupt_path(*DAT_08005438);
        return uVar6;
      }
      *DAT_08005424 = *DAT_08005424 & 0xfffffff8 | param_2;
      iVar3 = case_tick_word2();
      do {
        if ((*DAT_08005424 & 7) == param_2) goto LAB_080053ea;
        iVar5 = case_tick_word2();
      } while ((uint)(iVar5 - iVar3) <= DAT_08005428);
    }
    else {
      uVar4 = *(uint *)(param_1 + 4);
      if (uVar4 == 1) {
        iVar3 = *piVar2 << 0xe;
      }
      else if (uVar4 == 2) {
        iVar3 = *piVar2 << 6;
      }
      else if (uVar4 == 0) {
        iVar3 = *piVar2 << 0x15;
      }
      else {
        if (uVar4 == 3) {
          iVar3 = DAT_0800542c[0x18];
        }
        else {
          iVar3 = DAT_0800542c[0x17];
        }
        iVar3 = iVar3 << 0x1e;
      }
      if (-1 < iVar3) {
        return 1;
      }
      piVar2[2] = piVar2[2] & 0xfffffff8U | uVar4;
      iVar3 = case_tick_word2();
      do {
        if ((piVar2[2] & 0x38U) == *(int *)(param_1 + 4) * 8) goto LAB_080053b0;
        iVar5 = case_tick_word2();
      } while ((uint)(iVar5 - iVar3) <= DAT_08005428);
    }
  }
  return 3;
}

