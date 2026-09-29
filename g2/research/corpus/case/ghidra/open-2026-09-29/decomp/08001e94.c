
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 gls_frame_validate_dispatch(int param_1)

{
  char cVar1;
  uint *puVar2;
  uint *puVar3;
  byte *pbVar4;
  undefined1 uVar5;
  ushort uVar6;
  uint uVar7;
  char *pcVar8;
  bool bVar9;
  byte bVar10;
  int iVar11;
  byte *pbVar12;
  uint uVar13;
  undefined4 uVar14;
  undefined1 uVar15;
  uint uVar16;
  
  pbVar4 = _DAT_080022bc;
  puVar2 = DAT_080022b8;
  uVar14 = 0xff;
  uVar13 = 0;
  pbVar12 = (byte *)0x0;
  uVar7 = 0;
  uVar16 = 0;
  do {
    if (((*(char *)(DAT_08002254 + uVar7) == 'Z') &&
        (iVar11 = DAT_08002254 + uVar7, *(char *)(iVar11 + 1) == -0x5b)) &&
       (*(char *)(iVar11 + 2) == -1)) {
      pbVar12 = (byte *)(iVar11 + 4);
      uVar16 = (uint)*(byte *)(iVar11 + 3);
      uVar13 = uVar16 - 2 & 0xff;
    }
    uVar7 = uVar7 + 1 & 0xff;
  } while (uVar7 < 4);
  if (pbVar12 == (byte *)0x0) {
    return 0xff;
  }
  for (uVar7 = 0; uVar7 < uVar16; uVar7 = uVar7 + 1 & 0xff) {
    uVar13 = pbVar12[uVar7] + uVar13 & 0xff;
  }
  cVar1 = *_DAT_08002258;
  bVar10 = *pbVar12;
  if (pbVar12[uVar16] != uVar13) {
    if (bVar10 == 0x5a) {
      return 0xff;
    }
    if (cVar1 == '\0') {
      g2_log_printf(s_GLS_RX_error__CRC_wrong__0800225b + 1);
      g2_log_printf(&DAT_08002278);
      if (*_DAT_08002258 == '\0') {
        g2_log_printf(s_CRC_Cal___02x__CRC_Rx___02x__hea_0800227c,uVar13,pbVar12[uVar16],uVar16);
      }
    }
    log_hex_buffer(pbVar12,uVar16);
    return 0xff;
  }
  if (bVar10 == 0x46) {
    if (param_1 == 0) {
      _DAT_080022e8[3] = pbVar12[4] != 0;
    }
    else {
      _DAT_080022e8[2] = pbVar12[4] != 0;
    }
    uVar14 = 0x46;
    goto LAB_08001f5e;
  }
  if (0x46 < bVar10) {
    if (bVar10 == 0x58) {
      if (pbVar12[3] == 0x20) {
        if ((pbVar12[9] == 2) && (0x39 < pbVar12[10])) {
          *(undefined1 *)(DAT_080022b8 + -1) = 2;
          *(byte *)((int)puVar2 + -3) = pbVar12[10];
          uVar7 = FUN_080001fc(pbVar12 + 0xc);
          uVar7 = uVar7 << 0x18 | (uVar7 >> 8 & 0xff) << 0x10 | (uVar7 >> 0x10 & 0xff) << 8 |
                  (uint)pbVar12[0xf];
          *puVar2 = uVar7;
          uVar16 = FUN_080001fc(pbVar12 + 0x10);
          uVar16 = uVar16 << 0x18 | (uVar16 >> 8 & 0xff) << 0x10 | (uVar16 >> 0x10 & 0xff) << 8 |
                   (uint)pbVar12[0x13];
          puVar2[1] = uVar16;
          *(undefined1 *)((int)puVar2 + -7) = 3;
          *(undefined1 *)((int)puVar2 + -6) = 0;
          if (cVar1 != '\0') goto LAB_08001f5e;
          g2_log_printf(DAT_080023b8,2,0x39,pbVar12[9],pbVar12[10],uVar7,uVar16);
        }
        else {
          if (cVar1 != '\0') goto LAB_08001f5e;
          g2_log_printf(s__OTA_BOX___nothing_new__cur_1__d_080023bc,2,0x39,pbVar12[9],pbVar12[10]);
        }
      }
      else {
        if (cVar1 != '\0') goto LAB_08001f5e;
        g2_log_printf(s_ota_check__0x58___len__d_0800239c);
      }
      g2_log_printf(&DAT_08002278);
      goto LAB_08001f5e;
    }
    if (bVar10 == 0x59) {
      if ((pbVar12[3] == 1) && (pbVar12[4] == 0)) {
        uVar14 = 0x59;
      }
      goto LAB_08001f5e;
    }
    if (bVar10 == 0x5a) {
      if ((pbVar12[3] & 7) == 1) {
        bVar10 = 0;
        for (uVar7 = 0; (int)uVar7 < (int)(pbVar12[3] - 1); uVar7 = uVar7 + 1 & 0xff) {
          bVar10 = pbVar12[uVar7 + 4] + bVar10;
        }
        if (pbVar12[uVar7 + 4] == bVar10) {
          FUN_080001b4(DAT_080023f0,pbVar12 + 4);
          DAT_080022b8[2] = DAT_080023f0;
          *(byte *)(puVar2 + 3) = pbVar12[3] - 1;
        }
      }
      goto LAB_08001f5e;
    }
    if (bVar10 == 0x5b) {
      if ((pbVar12[3] == 1) && (pbVar12[4] == 0)) {
        uVar14 = 0x5b;
      }
      goto LAB_08001f5e;
    }
    goto LAB_08001f56;
  }
  if (bVar10 == 8) {
    uVar14 = 8;
    goto LAB_08001f5e;
  }
  if (bVar10 < 9) {
    if (bVar10 == 0) goto LAB_08001f5e;
    if (bVar10 == 7) {
      uVar14 = 7;
      goto LAB_08001f5e;
    }
  }
  else {
    if (bVar10 == 0x13) {
      if (pbVar12[3] == 6) {
        uVar6 = *(ushort *)(pbVar12 + 5) << 8 | *(ushort *)(pbVar12 + 5) >> 8;
        uVar16 = pbVar12[4] & 1;
        uVar7 = (uint)pbVar12[9];
        if (pbVar12[8] != 0) {
          uVar7 = -uVar7;
        }
        if (((pbVar12[4] & 1) == 0) && (0 < (int)uVar7)) {
          bVar9 = false;
        }
        else {
          bVar9 = true;
        }
        uVar5 = (undefined1)uVar16;
        if (param_1 == 0) {
          bVar10 = _DAT_080022bc[1];
          _DAT_080022bc[1] = bVar10 * '\x02';
          if ((bVar9) || (DAT_080022b8[0x11] < 10)) {
            pbVar4[1] = bVar10 * '\x02' + 1;
          }
          puVar2 = DAT_080022b8;
          *(undefined1 *)(DAT_080022b8 + 0xc) = 1;
          uVar15 = (pbVar4[1] & 7) != 0;
          *(undefined1 *)(puVar2 + 0xb) = uVar15;
          if ((*(char *)((int)puVar2 + 0x2d) != '\0') ||
             (*(char *)((int)DAT_080022b8 + -0xd) != '\0')) {
            if (pbVar12[7] < 0x62) {
              uVar5 = 0;
            }
            else {
              uVar5 = 1;
            }
          }
          *(undefined1 *)((int)puVar2 + 0x2d) = uVar5;
          if ((*_DAT_080022e8 != '\0') && (_DAT_080022e8[1] == '\0')) {
            *(undefined1 *)((int)puVar2 + 0x2d) = 0;
          }
          *(undefined1 *)((int)DAT_080022b8 + -0xd) = 0;
          *(byte *)((int)puVar2 + 0x2e) = pbVar12[7];
          *(ushort *)((int)puVar2 + 0x32) = uVar6;
          if (cVar1 != '\0') goto LAB_08002120;
          bVar10 = pbVar12[7];
          pcVar8 = s_R_charging__d__done__d__vol__dmv_08002320;
        }
        else {
          bVar10 = *_DAT_080022bc;
          *_DAT_080022bc = bVar10 * '\x02';
          if ((bVar9) || (DAT_080022b8[10] < 10)) {
            *pbVar4 = bVar10 * '\x02' + 1;
          }
          *(undefined1 *)(puVar2 + 5) = 1;
          *(bool *)(puVar2 + 4) = (*pbVar4 & 7) != 0;
          if (*(char *)((int)puVar2 + 0x11) == '\0') {
            if (*(char *)((int)DAT_080022b8 + -0xe) == '\0') goto LAB_08001ff6;
            *(bool *)((int)puVar2 + 0x11) = 0x61 < pbVar12[7];
            if ((0x61 < pbVar12[7]) && (cVar1 == '\0')) {
              g2_log_printf(s_Disable_charging_since_bat__d__>_080022bf + 1);
              g2_log_printf(&DAT_08002278);
            }
          }
          else {
            if (pbVar12[7] < 0x62) {
              uVar5 = 0;
            }
            else {
              uVar5 = 1;
            }
LAB_08001ff6:
            *(undefined1 *)((int)puVar2 + 0x11) = uVar5;
          }
          if ((*_DAT_080022e8 != '\0') && (_DAT_080022e8[1] == '\0')) {
            *(undefined1 *)((int)puVar2 + 0x11) = 0;
          }
          puVar3 = DAT_080022b8;
          *(undefined1 *)((int)DAT_080022b8 + -0xe) = 0;
          *(byte *)((int)puVar2 + 0x12) = pbVar12[7];
          *(ushort *)((int)puVar3 + 0x16) = uVar6;
          if (*_DAT_08002258 != '\0') goto LAB_08002120;
          bVar10 = pbVar12[7];
          uVar15 = (undefined1)puVar2[4];
          pcVar8 = s_L_charging__d__done__d__vol__dmv_080022eb + 1;
        }
        g2_log_printf(pcVar8,uVar15,uVar16,uVar6,bVar10,uVar7);
LAB_0800211a:
        g2_log_printf(&DAT_08002278);
      }
      else {
        if ((pbVar12[3] != 1) || (pbVar12[4] != 1)) goto LAB_08001f5e;
        if (param_1 == 0) {
          if (cVar1 == '\0') {
            pcVar8 = s_R_charging_1__confirmed_by_GLS_R_08002378;
            goto LAB_08002116;
          }
        }
        else if (cVar1 == '\0') {
          pcVar8 = s_L_charging_1__confirmed_by_GLS_L_08002354;
LAB_08002116:
          g2_log_printf(pcVar8);
          goto LAB_0800211a;
        }
      }
LAB_08002120:
      uVar14 = 0x13;
      goto LAB_08001f5e;
    }
    if (bVar10 == 0x3e) {
      if ((pbVar12[4] == 0) || (pbVar12[4] == 4)) {
        uVar14 = 0x3e;
      }
      goto LAB_08001f5e;
    }
  }
LAB_08001f56:
  FUN_0800680c(pbVar12,uVar16);
LAB_08001f5e:
  FUN_080001e6(DAT_08002254,0x118);
  return uVar14;
}

