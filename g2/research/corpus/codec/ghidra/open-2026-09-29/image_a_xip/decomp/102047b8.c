
undefined4 gx_audio_in_set_interrupt_enable(uint param_1,int param_2)

{
  if (param_2 == 0) {
    uRam00000100 = uRam00000100 & ~param_1;
  }
  else {
    uRam00000100 = param_1 | uRam00000100;
  }
  uRam00000104 = param_1;
  return 0;
}

