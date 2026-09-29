
void gx8002_stop_i2s(void)

{
  undefined4 *puVar1;
  int iVar2;
  
  puVar1 = puRam102091a8;
  gx8002_printf(PTR_s__YW_APP___s___d_102091b0,PTR_s_close_i2s_102091ac,0x133);
  iVar2 = iRam102091b4;
  if (puVar1[5] != 0) {
    puVar1[5] = 0;
    *(undefined1 *)(iVar2 + 4) = 0;
    gx8002_padmux_set(7,1);
    gx8002_padmux_set(8,1);
    gx8002_padmux_set(9,1);
    gx8002_padmux_set(10,1);
    if (puVar1[1] != -1) {
      gx8002_printf(uRam102091b8,PTR_s_close_i2s_102091ac,0x149);
      gx8002_audio_out_free(puVar1[1]);
      gx8002_audio_out_exit();
      puVar1[1] = 0xffffffff;
    }
    puVar1[6] = 0;
    puVar1[7] = 0;
    *puVar1 = 0;
  }
  return;
}

