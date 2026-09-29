
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void platform_bringup_430000(void)

{
  uint uVar1;
  uint uVar2;
  undefined1 *puVar3;
  int iVar4;
  undefined4 extraout_r1;
  undefined4 in_r3;
  byte bVar5;
  uint in_fpscr;
  float fVar6;
  undefined4 uStack_48;
  undefined1 uStack_44;
  undefined1 uStack_43;
  undefined1 uStack_42;
  undefined1 uStack_41;
  undefined1 uStack_40;
  undefined1 uStack_3f;
  undefined1 uStack_3e;
  undefined4 uStack_3c;
  undefined1 auStack_38 [4];
  undefined4 uStack_34;
  undefined1 uStack_30;
  undefined1 uStack_2f;
  undefined1 uStack_2e;
  undefined1 uStack_2d;
  int aiStack_2c [2];
  undefined4 uStack_24;
  undefined4 uStack_20;
  float fStack_1c;
  float fStack_18;
  float fStack_14;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  uStack_3c = 1;
  uStack_c = in_r3;
  FUN_0041d92c(0x10,*_DAT_00430208);
  iVar4 = hw_context_initialize_42e8d0(0,&uStack_48);
  if (iVar4 != 0) {
    FUN_00415fae(_DAT_0043020c);
  }
  fStack_14 = fRam004301f8;
  fStack_18 = fRam004301f8;
  fStack_1c = fRam004301f8;
  uStack_10 = _DAT_00430210;
  hw_config_dispatch_42ec0c(uStack_48,3,&fStack_1c);
  FUN_00415fae(PTR_s_ADC_correction_offset_____6f__ga_00430214,extraout_r1,
               SUB84((double)fStack_1c,0),(int)((ulonglong)(double)fStack_1c >> 0x20),
               (double)fStack_18);
  iVar4 = register_profile_transfer_42f020(uStack_48,0,0);
  if (iVar4 != 0) {
    FUN_00415fae(PTR_s_Error___ADC_power_on_failed__00430218);
  }
  uStack_24 = *(undefined4 *)PTR_DAT_0043021c;
  uStack_20 = *(undefined4 *)(PTR_DAT_0043021c + 4);
  hw_handle_configure_42eb74(uStack_48,&uStack_24);
  uStack_44 = 2;
  uStack_42 = 0;
  uStack_41 = 7;
  uStack_40 = 1;
  uStack_3f = 0;
  uStack_3e = 1;
  uStack_43 = 1;
  iVar4 = hw_profile_apply_42ea68(uStack_48,&uStack_44);
  if (iVar4 != 0) {
    FUN_00415fae(PTR_s_Error___configuring_ADC_failed__00430220);
  }
  auStack_38[0] = 7;
  uStack_34 = 0x20;
  uStack_30 = 0;
  uStack_2f = 3;
  uStack_2e = 0;
  uStack_2d = 1;
  iVar4 = hw_channel_config_42eaf6(uStack_48,0,auStack_38);
  if (iVar4 != 0) {
    FUN_00415fae(PTR_s_Error___configuring_ADC_Slot_fai_00430224);
  }
  iVar4 = hw_handle_activate_42ed60(uStack_48);
  if (iVar4 != 0) {
    FUN_00415fae(PTR_s_Error___enabling_ADC_failed__00430228);
  }
  hw_handle_enable_42ebaa(uStack_48);
  hw_handle_command_42eff4(uStack_48);
  bVar5 = 0;
  do {
    if (2 < bVar5) {
      register_profile_transfer_42f020(uStack_48,2,0);
      hw_handle_reset_42ea32(uStack_48);
      FUN_0041d92c(0x10,*(undefined4 *)PTR_DAT_00430238);
      return;
    }
    do {
    } while ((*_DAT_00430230 & 0xfffffff) >> 0x14 == 0);
    uStack_3c = 1;
    hw_channel_enumerate_42ee70(uStack_48,0,0,&uStack_3c,aiStack_2c);
    if (bVar5 == 2) {
      hw_handle_disable_42ebe2(uStack_48);
      hardware_channel_normalize_42eda0(uStack_48);
      puVar3 = _DAT_0043022c;
      fVar6 = (float)VectorUnsignedToFloat
                               ((uint)(aiStack_2c[0] * 0x4a6) >> 0xc,(byte)(in_fpscr >> 0x16) & 3);
      uVar1 = in_fpscr & 0xfffffff;
      uVar2 = uVar1 | (uint)(fVar6 < fRam004301fc) << 0x1f;
      in_fpscr = uVar2 | (uint)(NAN(fVar6) || NAN(fRam004301fc)) << 0x1c;
      if ((byte)(uVar2 >> 0x1f) == ((byte)(in_fpscr >> 0x1c) & 1)) {
        in_fpscr = uVar1;
        if (fRam00430200 <= fVar6) goto LAB_0043011a;
        *_DAT_0043022c = 1;
        *(undefined2 *)(puVar3 + 2) = 1;
      }
      else {
LAB_0043011a:
        *_DAT_0043022c = 0;
        *(undefined2 *)(puVar3 + 2) = 3;
      }
      *(short *)(_DAT_0043022c + 4) = (short)(int)fVar6;
      FUN_00415fae(PTR_s_HwConfig_ADC_sample_read__d__mea_00430234,aiStack_2c[0],
                   SUB84((double)fVar6,0),(int)((ulonglong)(double)fVar6 >> 0x20));
    }
    bVar5 = bVar5 + 1;
  } while( true );
}

