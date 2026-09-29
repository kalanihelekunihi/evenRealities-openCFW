
undefined4 service_audio_pcm_sample_bytes(byte param_1)

{
  undefined4 uVar1;
  
  if (param_1 == 0) {
    uVar1 = 2;
  }
  else if (param_1 == 2) {
    uVar1 = 3;
  }
  else if (param_1 < 2) {
    uVar1 = 4;
  }
  else if (param_1 == 3) {
    uVar1 = 4;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

