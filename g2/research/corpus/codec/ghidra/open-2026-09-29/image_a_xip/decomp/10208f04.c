
/* WARNING: Type propagation algorithm not settling */

undefined4 gx8002_sample_event(int *param_1)

{
  uint *puVar1;
  int iVar2;
  undefined4 *puStack_3c;
  undefined1 auStack_38 [4];
  int iStack_34;
  int aiStack_30 [4];
  int iStack_20;
  
  gx8002_context_acquire(param_1[1],&puStack_3c,auStack_38);
  puVar1 = puRam10208fd8;
  if ((*(byte *)(puStack_3c + 3) & 7) != *puRam10208fd8) {
    gx8002_vad_notify();
    *puVar1 = *(byte *)(puStack_3c + 3) & 7;
  }
  if (*param_1 == 100) {
    gx8002_printf(PTR_s_wake_up_hey_even_10208fdc);
    gx8002_event_notify(*param_1);
  }
  if (*param_1 == 0x65) {
    gx8002_printf(PTR_s_wake_up_hi_even_10208fe0);
    gx8002_event_notify(*param_1);
  }
  iVar2 = iRam10208fe4;
  if (((*param_1 == 0x5b) && (*(int *)(iRam10208fe4 + 0x14) != 0)) && ((char)puVar1[1] != '\0')) {
    gx8002_printf(PTR_s_______S__d__first__d_______10208fe8,param_1[1],1);
    iStack_34 = 0;
    aiStack_30[0] = 0;
    aiStack_30[1] = 0;
    aiStack_30[2] = 0;
    gx8002_mic_buffer(*puStack_3c,0,param_1[1],&iStack_34,aiStack_30);
    gx8002_mic_buffer(*puStack_3c,1,param_1[1],aiStack_30 + 1,aiStack_30 + 2);
    aiStack_30[3] = iStack_34 - *(int *)(iVar2 + 0x18);
    iStack_20 = aiStack_30[0] + -1 + aiStack_30[3];
    gx8002_printf(PTR_s_______first_push_frame_S__d__E___10208fec);
    gx8002_audio_out_push_frame(*(undefined4 *)(iVar2 + 4),aiStack_30 + 3);
    *(undefined1 *)(puVar1 + 1) = 0;
  }
  return 0;
}

