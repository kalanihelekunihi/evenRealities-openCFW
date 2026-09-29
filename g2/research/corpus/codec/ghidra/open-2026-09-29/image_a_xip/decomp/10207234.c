
undefined4 gx8002_audio_input_config(void)

{
  uint uVar1;
  uint *puVar2;
  undefined4 uVar3;
  uint uVar4;
  
  audio_board_init();
  puVar2 = (uint *)audio_board_get();
  uVar4 = *puVar2;
  if ((uVar4 & 1) != 0) {
    gx_audio_in_set_dc_enable(1,*(byte *)((int)puVar2 + 5) >> 2 & 1);
    gx_audio_in_set_evad_threshold(1,puVar2[5],puVar2[6],puVar2[7]);
    gx_audio_in_set_evad_enable(1,puVar2[2],puVar2[3],puVar2[4]);
    gx8002_audio_input_sadc(puVar2[0x17]);
    gx8002_audio_pga_gain((byte)puVar2[1] & 0x3f);
    gx_audio_in_set_rough_gain(1,((ushort)puVar2[1] & 0x1ff) >> 6);
  }
  if ((uVar4 & 2) != 0) {
    gx_audio_in_set_dc_enable(2,*(byte *)((int)puVar2 + 0x21) >> 2 & 1);
    gx_audio_in_set_evad_threshold(2,puVar2[0xc],puVar2[0xd],puVar2[0xe]);
    gx_audio_in_set_evad_enable(2,puVar2[9],puVar2[10],puVar2[0xb]);
    gx_audio_in_set_rough_gain(2,((ushort)puVar2[8] & 0x1ff) >> 6);
    gx8002_audio_input_pdm(puVar2[0x18]);
    gx_audio_in_set_input_channel(2,0,1);
  }
  if ((uVar4 & 4) != 0) {
    gx_audio_in_set_dc_enable(4,*(byte *)((int)puVar2 + 0x3d) >> 2 & 1);
    gx_audio_in_set_evad_threshold(4,puVar2[0x13],puVar2[0x14],puVar2[0x15]);
    gx_audio_in_set_evad_enable(4,puVar2[0x10],puVar2[0x11],puVar2[0x12]);
    gx_audio_in_set_rough_gain(4,((ushort)puVar2[0xf] & 0x1ff) >> 6);
    gx_audio_in_set_i2s_clock(3);
    gx8002_audio_input_i2s
              (puVar2[0x19],puVar2[0x1a],puVar2[0x1b],puVar2[0x1c],puVar2[0x1d],puVar2[0x1e]);
    gx_audio_in_set_input_channel(4,1,0);
    gx_audio_in_set_i2sin_mode(0);
  }
  uVar1 = puVar2[0x16];
  if ((uVar1 & 1) != 0) {
    gx8002_audio_input_output(uVar4,1);
  }
  if ((uVar1 & 2) != 0) {
    gx8002_audio_input_output(uVar4,2);
  }
  if ((uVar1 & 4) != 0) {
    gx8002_audio_input_output(uVar4,4);
  }
  if ((uVar1 & 8) != 0) {
    gx8002_audio_input_output(uVar4,8);
  }
  uVar3 = gx8002_logfbank_frames_per_channel();
  gx_audio_in_set_fftvad_enable(1,0,uVar3);
  return 0;
}

