
bool gx8002_audio_input_query_vad(void)

{
  int iVar1;
  uint uVar2;
  uint uStack_1c;
  uint uStack_18;
  uint uStack_14;
  ushort uStack_10;
  
  uVar2 = gx8002_distance_noise();
  iVar1 = DAT_102075b4;
  if ((uVar2 < 0x300000) && (*(int *)(DAT_102075b4 + 4) != 4)) {
    gx8002_printf(PTR_s__LVP_AUD_vad_param_4___d__102075b8);
    *(undefined4 *)(iVar1 + 4) = 4;
LAB_1020745c:
    gx_audio_in_set_fftvad_curve_1(0x400,0xf00);
    gx_audio_in_set_fftvad_curve_2(0x4cd,0x600);
    gx_audio_in_set_fftvad_curve_3(0x4cd,0x2000);
    gx_audio_in_set_fftvad_curve_4(0x733,0x333);
    gx_audio_in_set_fftvad_curve_5(0xa00);
    uStack_1c = 0x106028f;
    uStack_18 = 0x210083;
    gx_audio_in_set_fftvad_chipping(0x106028f,0x210083);
  }
  else {
    if ((uVar2 < 0x300000) && (*(int *)(DAT_102075b4 + 4) != 3)) {
      gx8002_printf(PTR_s__LVP_AUD_vad_param_3___d__102075bc);
      *(undefined4 *)(iVar1 + 4) = 3;
      goto LAB_1020745c;
    }
    if (uVar2 < 0xe00001) {
      if (*(int *)(DAT_102075b4 + 4) == 2) goto LAB_102074c6;
      gx8002_printf(PTR_s__LVP_AUD_vad_param_2___d__102075c0);
      *(undefined4 *)(iVar1 + 4) = 2;
      goto LAB_1020745c;
    }
    if ((uVar2 < 0x1400001) || (*(int *)(DAT_102075b4 + 4) == 1)) goto LAB_102074c6;
    gx8002_printf(PTR_s__LVP_AUD_vad_param_1___d__102075c4);
    *(undefined4 *)(iVar1 + 4) = 1;
    gx_audio_in_set_fftvad_curve_1(0x400,0xf00);
    gx_audio_in_set_fftvad_curve_2(0x4cd,0x600);
    gx_audio_in_set_fftvad_curve_3(0x4cd,0x2000);
    gx_audio_in_set_fftvad_curve_4(0x733,0x333);
    gx_audio_in_set_fftvad_curve_5(0xa00);
    uStack_1c = 0x106028f;
    uStack_18 = 0x210083;
    gx_audio_in_set_fftvad_chipping(0x106028f,0x210083);
  }
  gx_audio_in_set_fftvad_w(0x101);
LAB_102074c6:
  gx_audio_in_get_fftvad_state(&uStack_1c);
  uVar2 = (uStack_10 + 0x5e) % 0x5f;
  if (uVar2 < 0x20) {
    uVar2 = 1 << (uVar2 & 0x3f);
  }
  else if (uVar2 < 0x40) {
    uVar2 = 1 << (uVar2 - 0x20 & 0x3f);
    uStack_1c = uStack_18;
  }
  else {
    uVar2 = 1 << (uVar2 - 0x40 & 0x3f);
    uStack_1c = uStack_14;
  }
  return *(int *)(iVar1 + 4) == 1 || (uVar2 & uStack_1c) != 0;
}

