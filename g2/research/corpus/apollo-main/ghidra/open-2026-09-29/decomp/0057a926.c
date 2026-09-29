
void service_audio_lc3_encoder_setup(int param_1)

{
  undefined4 uVar1;
  
  if (param_1 != 0) {
    uVar1 = FUN_00591374(*(undefined4 *)(param_1 + 4),*(undefined4 *)(param_1 + 8),0,param_1 + 0x1c)
    ;
    *(undefined4 *)(param_1 + 0x18) = uVar1;
  }
  return;
}

