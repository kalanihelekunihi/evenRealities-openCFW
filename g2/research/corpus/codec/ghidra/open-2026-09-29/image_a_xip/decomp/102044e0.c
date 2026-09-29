
undefined4 gx_audio_in_set_evad_threshold(int param_1,uint param_2,uint param_3,uint param_4)

{
  uint *puVar1;
  uint *puVar2;
  
  if (param_1 == 1) {
    puVar2 = (uint *)&DAT_a0a00010;
  }
  else {
    puVar2 = (uint *)0x0;
    puVar1 = DAT_10204524;
    if ((param_1 == 2) || (puVar1 = DAT_10204528, param_1 == 4)) {
      puVar2 = puVar1;
      *puVar2 = *puVar2 & 0xefffffff;
    }
  }
  puVar2[2] = param_2;
  puVar2[3] = param_3;
  puVar2[4] = param_4;
  return 0;
}

