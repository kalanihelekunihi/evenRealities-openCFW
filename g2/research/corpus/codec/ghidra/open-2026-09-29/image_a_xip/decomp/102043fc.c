
void gx_audio_in_set_evad_enable(int param_1,uint param_2,int param_3,int param_4)

{
  uint *puVar1;
  uint *puVar2;
  
  puVar1 = DAT_102044dc;
  puVar2 = DAT_102044d8;
  if (param_1 == 1) {
    uRam00000100 = uRam00000100 & 0xfffbffff | (param_2 & 1) << 0x12;
    puVar2 = (uint *)&DAT_a0a00010;
  }
  else if (param_1 == 2) {
    *DAT_102044d8 = *DAT_102044d8 & 0xefffffff;
    uRam00000100 = uRam00000100 & 0xfff7ffff | (param_2 & 1) << 0x13;
  }
  else {
    puVar2 = (uint *)0x0;
    if (param_1 == 4) {
      *DAT_102044dc = *DAT_102044dc & 0xefffffff;
      uRam00000100 = uRam00000100 & 0xffefffff | (param_2 & 1) << 0x14;
      puVar2 = puVar1;
    }
  }
  *puVar2 = *puVar2 & 0xfbffffff | 0x4000000;
  do {
  } while (puVar2[5] != 0);
  *puVar2 = *puVar2 & 0xfbffffff;
  *puVar2 = *puVar2 & 0xf7ffffff | ((byte)~(param_2 != 0) & 1) << 0x1b;
  *puVar2 = *puVar2 & 0xfdffffff | ((byte)~(param_3 != 0) & 1) << 0x19;
  *puVar2 = *puVar2 & 0xfeffffff | 0x1000000;
  *puVar2 = *puVar2 & 0xffff0000 | 0x6000;
  *puVar2 = *puVar2 & 0x7fffffff | param_4 << 0x1f;
  puVar2[1] = puVar2[1] & 0xff00ffff;
  puVar2[1] = puVar2[1] & 0xffff0000 | 0x10;
  return;
}

