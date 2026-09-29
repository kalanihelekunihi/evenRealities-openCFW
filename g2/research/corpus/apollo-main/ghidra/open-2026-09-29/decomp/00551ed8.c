
void FUN_00551ed8(int param_1,char param_2)

{
  char cVar1;
  int *piVar2;
  uint *puVar3;
  byte bVar4;
  short sVar5;
  int iVar6;
  int iVar7;
  uint uVar8;
  byte bVar9;
  uint uVar10;
  
  piVar2 = DAT_00552858;
  if (*DAT_00552858 == 0) {
    iVar6 = ui_common_api_fn_00509c1c();
    *piVar2 = iVar6;
    if (*piVar2 == 0) {
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        FUN_0043d574(1,DAT_0055221c,DAT_00552218,DAT_00552860,0x7e9,DAT_0055285c);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_00552864);
      }
    }
  }
  iVar6 = DAT_00552870;
  if (param_1 == 0) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0055221c,DAT_00552218,DAT_00552860,0x7f0,DAT_00552868);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0055286c,DAT_0055286c);
    }
  }
  else if (*(int *)(DAT_00552870 + 0x3c) == 0) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0055221c,DAT_00552218,DAT_00552860,0x7f6,DAT_00552874);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00552878,DAT_00552878);
    }
  }
  else {
    bVar4 = service_ancc_message_count_get();
    if (10 < bVar4) {
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0055221c,DAT_00552218,DAT_00552860,0x800,DAT_0055287c,bVar4,10);
      }
      iVar7 = FUN_0043d0ce();
      if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
        compress_log_output(0x8800000,DAT_00552880,DAT_00552880,bVar4,10);
      }
      bVar4 = 10;
    }
    FUN_0054ff48();
    if (param_2 == '\0') {
      if (bVar4 != 0) {
        *DAT_00552884 = 0;
      }
    }
    else if (param_2 == '\x01') {
      *DAT_00552884 = 0;
    }
    else if (param_2 == '\x02') {
      if (bVar4 == 0) {
        *DAT_00552884 = 0;
      }
      else if ((int)(uint)bVar4 <= (int)*DAT_00552884) {
        *DAT_00552884 = bVar4 - 1;
      }
    }
    puVar3 = DAT_00552884;
    if (bVar4 != 0) {
      if ((int)(uint)bVar4 <= (int)*DAT_00552884) {
        *DAT_00552884 = bVar4 - 1;
      }
      bVar9 = 0;
      for (uVar10 = 0; (uVar10 & 0xff) < 3; uVar10 = uVar10 + 1) {
        if ((int)*puVar3 < (int)(bVar4 - 1)) {
          iVar7 = 1;
        }
        else {
          iVar7 = 2;
        }
        uVar8 = (uVar10 + *puVar3) - iVar7;
        cVar1 = (char)uVar8;
        if ((-1 < cVar1) && ((short)cVar1 < (short)(ushort)bVar4)) {
          FUN_00551abc(iVar6 + (uint)bVar9 * 0x28 + 0x40,uVar8 & 0xff,bVar9);
          bVar9 = bVar9 + 1;
        }
      }
      for (; bVar9 < 3; bVar9 = bVar9 + 1) {
        FUN_0043ded4(*(undefined4 *)(iVar6 + (uint)bVar9 * 0x28 + 0x40),1);
      }
    }
    FUN_00551e5c();
    puVar3 = DAT_00552884;
    if (param_2 == '\0') {
      if ((bVar4 != 0) && (sVar5 = FUN_00550170(*DAT_00552884 & 0xff), -1 < sVar5)) {
        FUN_0044ea04(*(undefined4 *)(iVar6 + 0x3c),sVar5 * 0xd6,0);
      }
    }
    else if (param_2 == '\x01') {
      if ((*DAT_00552884 == 0) && (1 < bVar4)) {
        *DAT_00552884 = *DAT_00552884 + 1;
        sVar5 = FUN_00550170(*puVar3 & 0xff);
        if (-1 < sVar5) {
          FUN_0044ea04(*(undefined4 *)(iVar6 + 0x3c),sVar5 * 0xd6,0);
        }
      }
      FUN_00550968(0);
    }
    else if (param_2 == '\x02') {
      if ((bVar4 != 0) && (sVar5 = FUN_00550170(*DAT_00552884 & 0xff), -1 < sVar5)) {
        FUN_0044ea04(*(undefined4 *)(iVar6 + 0x3c),sVar5 * 0xd6,0);
      }
    }
    else if (((param_2 == '\x03') && (bVar4 != 0)) &&
            (sVar5 = FUN_00550170(*DAT_00552884 & 0xff), -1 < sVar5)) {
      FUN_0044ea04(*(undefined4 *)(iVar6 + 0x3c),sVar5 * 0xd6,0);
    }
  }
  return;
}

