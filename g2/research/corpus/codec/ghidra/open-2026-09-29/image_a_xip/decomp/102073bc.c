
void gx8002_audio_input_init(undefined4 param_1)

{
  gx8002_memset(DAT_102073e4,0,0x14);
  gx8002_audio_initialize(DAT_102073f0,PTR_gx8002_audio_input_config_102073e8,PTR_LAB_102073ec,0,0);
  *DAT_102073f4 = param_1;
  return;
}

