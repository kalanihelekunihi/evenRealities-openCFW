
void audio_board_init(void)

{
  undefined4 uVar1;
  
  gx8002_printf(PTR_s__AB_dmic___d_Channel__1020a8af_4_10203044,2);
  uVar1 = audio_board_gain((*(ushort *)(DAT_10203048 + 0x20) & 0x1ff) >> 6);
  gx8002_printf(PTR_s__AB_dmic_Ain_gain___d_dB__1020304c,uVar1);
  return;
}

