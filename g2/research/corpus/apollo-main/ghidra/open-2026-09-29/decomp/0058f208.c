
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_0058f208(uint param_1)

{
  bool bVar1;
  int iVar2;
  undefined4 uVar3;
  short *psVar4;
  uint uVar5;
  uint uVar6;
  short asStack_468 [2];
  undefined1 auStack_464 [1024];
  undefined1 auStack_64 [60];
  uint uStack_28;
  short sStack_24;
  
  if (param_1 + 0x80000000 < 0x2000000) {
    FUN_0058f1ec(param_1,auStack_64,0x46);
    if (uStack_28 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_product_common_0058f4a8,PTR_s_D__01_workspace_s200_ap510b_iar__0058f4a4
                     ,PTR_s_checkFontCrc16_0058f4a0,0x29,PTR_s_font_crc__invalid_len_0_0058f4b0);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__product_common_font_crc__invali_0058f4b4,
                            PTR_s__product_common_font_crc__invali_0058f4b4);
      }
      uVar3 = 1;
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_product_common_0058f4a8,PTR_s_D__01_workspace_s200_ap510b_iar__0058f4a4
                     ,PTR_s_checkFontCrc16_0058f4a0,0x2d,
                     PTR_s_font_crc__len__u__crc16_0x_04x_0058f4b8,uStack_28,sStack_24);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc800000,PTR_s__product_common_font_crc__len__u_0058f4bc,
                            PTR_s__product_common_font_crc__len__u_0058f4bc,uStack_28,sStack_24);
      }
      if (((char)(CARRY4(param_1,uStack_28) + (0xffffffba < param_1 + uStack_28)) == '\0') &&
         (param_1 + uStack_28 + 0x45 < _DAT_0058f4c0)) {
        iVar2 = 0x45;
        asStack_468[0] = 0;
        bVar1 = true;
        for (uVar5 = uStack_28; uVar5 != 0; uVar5 = uVar5 - uVar6) {
          uVar6 = uVar5;
          if (0x400 < uVar5) {
            uVar6 = 0x400;
          }
          FUN_0058f1ec(iVar2 + param_1,auStack_464,uVar6);
          if (bVar1) {
            psVar4 = (short *)0x0;
          }
          else {
            psVar4 = asStack_468;
          }
          asStack_468[0] = FUN_0049acd4(auStack_464,uVar6,psVar4);
          bVar1 = false;
          iVar2 = uVar6 + iVar2;
        }
        if (asStack_468[0] == sStack_24) {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(3,PTR_s_product_common_0058f4a8,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0058f4a4,
                         PTR_s_checkFontCrc16_0058f4a0,0x45,
                         PTR_s_font_crc__match__calc_0x_04x_exp_0058f4cc,asStack_468[0],sStack_24);
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0xc800000,PTR_s__product_common_font_crc__match__0058f4d0,
                                PTR_s__product_common_font_crc__match__0058f4d0,asStack_468[0],
                                sStack_24);
          }
          uVar3 = 0;
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(1,PTR_s_product_common_0058f4a8,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0058f4a4,
                         PTR_s_checkFontCrc16_0058f4a0,0x49,
                         PTR_s_font_crc__mismatch__calc_0x_04x_e_0058f4d4,asStack_468[0],sStack_24);
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0x4800000,PTR_s__product_common_font_crc__mismat_0058f4d8,
                                PTR_s__product_common_font_crc__mismat_0058f4d8,asStack_468[0],
                                sStack_24);
          }
          uVar3 = 1;
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(1,PTR_s_product_common_0058f4a8,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0058f4a4,PTR_s_checkFontCrc16_0058f4a0
                       ,0x31,PTR_s_font_crc__len_overflow__base_0x__0058f4c4,param_1,uStack_28);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x4800000,PTR_s__product_common_font_crc__len_ov_0058f4c8,
                              PTR_s__product_common_font_crc__len_ov_0058f4c8,param_1,uStack_28);
        }
        uVar3 = 1;
      }
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_product_common_0058f4a8,PTR_s_D__01_workspace_s200_ap510b_iar__0058f4a4,
                   PTR_s_checkFontCrc16_0058f4a0,0x1a,
                   PTR_s_font_crc__invalid_base_addr_0x_0_0058f49c,param_1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,PTR_s__product_common_font_crc__invali_0058f4ac,
                          PTR_s__product_common_font_crc__invali_0058f4ac,param_1);
    }
    uVar3 = 1;
  }
  return uVar3;
}

