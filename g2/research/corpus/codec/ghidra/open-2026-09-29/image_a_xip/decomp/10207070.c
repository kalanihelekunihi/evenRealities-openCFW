
void gx8002_audio_input_output(uint param_1,int param_2)

{
  byte bVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  uint uVar8;
  undefined4 uVar9;
  uint uVar10;
  undefined4 local_24;
  undefined4 uStack_20;
  
  uVar2 = gx8002_audio_input_buffer_addr(param_2);
  uVar3 = gx8002_audio_input_buffer_size(param_2);
  iVar4 = audio_board_get();
  if (param_2 == 1) {
    bVar1 = *(byte *)(iVar4 + 5) >> 3;
    if (((param_1 & 9) == 0) && ((bVar1 & 1) != 0)) {
      uVar8 = (uVar3 >> 8) << 7;
    }
    else {
      uVar8 = uVar3 & 0xffffff80;
    }
    uVar5 = 0x80;
    if ((param_1 & 8) != 0) {
      uVar5 = 0x400;
    }
    uVar2 = uVar2 & 0xffffff8;
    *(uint *)(iVar4 + 0x84) = uVar8;
    *(uint *)(iVar4 + 0x7c) = uVar2;
    if ((param_1 & 8) == 0) {
      uVar3 = bVar1 & 1;
      if ((bVar1 & 1) != 0) {
        uVar3 = uVar2 + uVar8;
      }
      *(uint *)(iVar4 + 0x80) = uVar3;
      *(undefined4 *)(iVar4 + 0x8c) = 0;
    }
    else {
      *(uint *)(iVar4 + 0xe0) = uVar3;
      *(uint *)(iVar4 + 0xdc) = uVar2;
      *(uint *)(iVar4 + 0xe4) = uVar3 >> 3;
      gx_audio_in_set_logfbank_enable(1);
      local_24 = *(undefined4 *)(iVar4 + 0xe8);
      uStack_20 = *(undefined4 *)(iVar4 + 0xec);
      gx8002_audio_output_spectrum
                (1,*(undefined4 *)(iVar4 + 0xdc),*(undefined4 *)(iVar4 + 0xe0),
                 *(undefined4 *)(iVar4 + 0xe4));
    }
    *(undefined4 *)(iVar4 + 0x88) = uVar5;
    func_0x10025738(&local_24,iVar4 + 0x88,0xc);
    uVar6 = *(undefined4 *)(iVar4 + 0x7c);
    uVar7 = *(undefined4 *)(iVar4 + 0x80);
    uVar9 = *(undefined4 *)(iVar4 + 0x84);
    uVar5 = 1;
  }
  else {
    if (param_2 != 2) {
      if (param_2 == 4) {
        *(uint *)(iVar4 + 0xac) = uVar2 & 0xffffff8;
        *(uint *)(iVar4 + 0xb0) = uVar3;
        *(undefined4 *)(iVar4 + 0xb4) = 1;
        gx_audio_in_set_logfbank_enable(1);
        local_24 = *(undefined4 *)(iVar4 + 0xbc);
        gx8002_audio_output_logfbank
                  (*(undefined4 *)(iVar4 + 0xac),*(undefined4 *)(iVar4 + 0xb0),
                   *(undefined4 *)(iVar4 + 0xb4),*(undefined4 *)(iVar4 + 0xb8));
        return;
      }
      if (param_2 != 8) {
        return;
      }
      func_0x10025738(&local_24,iVar4 + 0xd0,0xc);
      gx8002_audio_output_i2s
                (*(undefined4 *)(iVar4 + 0xc0),*(undefined4 *)(iVar4 + 0xc4),
                 *(undefined4 *)(iVar4 + 200),*(undefined4 *)(iVar4 + 0xcc));
      gx_audio_in_set_i2sout_mode(0);
      return;
    }
    bVar1 = *(byte *)(iVar4 + 0x21) >> 3;
    if (((param_1 & 1) == 0) && ((bVar1 & 1) != 0)) {
      uVar3 = (uVar3 >> 8) << 7;
    }
    else {
      uVar3 = uVar3 & 0xffffff80;
    }
    uVar8 = gx8002_pcm_frame_size();
    if ((int)uVar8 < 0) {
      uVar8 = uVar8 + 0x3f;
    }
    *(uint *)(iVar4 + 0x9c) = uVar3;
    uVar10 = bVar1 & 1;
    if ((bVar1 & 1) != 0) {
      uVar10 = uVar3 + (uVar2 & 0xffffff8);
    }
    *(undefined4 *)(iVar4 + 0xa4) = 0;
    *(uint *)(iVar4 + 0xa0) = uVar8 & 0xffffffc0;
    *(uint *)(iVar4 + 0x94) = uVar2 & 0xffffff8;
    *(uint *)(iVar4 + 0x98) = uVar10;
    func_0x10025738(&local_24,iVar4 + 0xa0,0xc);
    uVar6 = *(undefined4 *)(iVar4 + 0x94);
    uVar7 = *(undefined4 *)(iVar4 + 0x98);
    uVar9 = *(undefined4 *)(iVar4 + 0x9c);
    uVar5 = 2;
  }
  gx8002_audio_output_pcm(uVar5,uVar6,uVar7,uVar9);
  return;
}

