
undefined4 gx8002_start_i2s(void)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  undefined *puStack_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined1 uStack_24;
  undefined1 uStack_23;
  undefined1 uStack_22;
  undefined1 uStack_21;
  undefined4 uStack_20;
  int iStack_1c;
  int iStack_18;
  int iStack_14;
  
  piVar1 = piRam10209110;
  gx8002_printf(PTR_s__YW_APP___s___d_10209118,PTR_s_start_i2s_10209114,0x115);
  iVar2 = iRam1020911c;
  if (piVar1[5] == 0) {
    piVar1[5] = 1;
    *(undefined1 *)(iVar2 + 4) = 1;
    if (piVar1[1] != -1) {
      gx8002_printf(PTR_s__YW_APP___s___d__handle____d_10209120,PTR_s_start_i2s_10209114,0x122);
      gx8002_audio_out_free(piVar1[1]);
      gx8002_audio_out_exit();
      piVar1[1] = -1;
    }
    gx8002_padmux_set(7,3);
    gx8002_padmux_set(8,3);
    gx8002_padmux_set(9,3);
    gx8002_padmux_set(10,3);
    func_0x10024be0(8,5);
    gx8002_audio_out_init(0);
    uStack_20 = func_0x10025210(0xb);
    iVar2 = gx8002_audio_out_alloc_playback(0);
    puStack_30 = PTR_audio_range_callback_10209124;
    piVar1[1] = iVar2;
    uStack_2c = 0;
    gx8002_audio_out_config_cb(iVar2,&puStack_30);
    gx8002_audio_out_set_db(piVar1[1],0);
    iVar2 = gx8002_mic_buffer_size();
    *piVar1 = iVar2 / 2;
    gx8002_audio_out_set_channel(piVar1[1],0);
    iVar2 = gx8002_mic_buffer_addr();
    piVar1[6] = iVar2;
    iStack_18 = gx8002_mic_buffer_addr();
    iStack_14 = *piVar1;
    iStack_18 = iStack_18 + iStack_14;
    piVar1[7] = iStack_18;
    uStack_24 = 2;
    iStack_1c = piVar1[6];
    gx8002_audio_out_config_buffer(piVar1[1],&iStack_1c);
    uStack_28 = 16000;
    uStack_23 = 0x10;
    uStack_22 = 0;
    uStack_21 = 0;
    gx8002_audio_out_config_pcm(piVar1[1],&uStack_28);
    uVar3 = func_0x10025210(0xb);
    gx8002_printf(PTR_s_MCLK__dHz_10209128,uVar3);
    gx8002_printf(PTR_s_LRCLK__dHz_1020912c,uStack_28);
    gx8002_printf(PTR_s_bits__d_10209130,uStack_23);
    gx8002_printf(PTR_s__s_Init_OK_10209138,PTR_s_I2S_out_Master_10209134);
    uVar3 = 0;
  }
  else {
    uVar3 = 0xffffffff;
  }
  return uVar3;
}

