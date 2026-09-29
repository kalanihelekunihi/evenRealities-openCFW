
undefined4 gx8002_aout_handle_isr(int param_1,int param_2)

{
  uint uVar1;
  
  if (param_1 == 0xd) {
    uVar1 = uRam0000000c & uRam00000008;
    if ((uVar1 & 4) != 0) {
      uRam00000018 = uRam00000018 & 0x3fffffff;
      uRam0000000c = uRam0000000c & 4;
      uRam00000008 = uRam00000008 & 0xfffffffb;
    }
    if ((uVar1 & 8) != 0) {
      uRam0000001c = uRam0000001c & 0x3fffffff;
      uRam0000000c = uRam0000000c & 8;
      uRam00000008 = uRam00000008 & 0xfffffff7;
    }
    if ((uVar1 & 0x40) != 0) {
      uRam0000000c = uRam0000000c & 0x40;
    }
    if ((uVar1 & 1) != 0) {
      uRam0000000c = uRam0000000c & 1;
      if (*(uint *)(param_2 + 0x28) != 0) {
        (*(code *)(*(uint *)(param_2 + 0x28) & 0xfffffffe))
                  (*(undefined4 *)(param_2 + 0x20),*(undefined4 *)(param_2 + 0x24));
      }
    }
    if ((uVar1 & 2) != 0) {
      uRam0000000c = 0;
      aout_play_check_idle(0,0);
      aout_set_r1_frame_over_int_enable(0,0);
      uRam0000000c = uRam0000000c & 2;
      *(undefined1 *)(param_2 + 0x1c) = 1;
      if (*(uint *)(param_2 + 0x2c) != 0) {
        (*(code *)(*(uint *)(param_2 + 0x2c) & 0xfffffffe))();
      }
    }
  }
  return 0;
}

