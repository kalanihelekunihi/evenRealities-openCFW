
undefined4 gx8002_aout_push_frame(int param_1,int param_2)

{
  undefined4 uVar1;
  
  if (param_2 == 0) {
    uVar1 = 0xffffffff;
  }
  else {
    func_0x10025738(param_1 + 0x20,param_2,8);
    iRam00000014 = *(int *)(param_1 + 0x20);
    uRam00000018 = *(undefined4 *)(param_1 + 0x24);
    uRam00000024 = ((*(int *)(param_1 + 0x24) + 1) - iRam00000014) /
                   (int)(uint)*(byte *)(param_1 + 0x19) & 0x7fffffU | uRam00000024 & 0xff000000;
    uRam0000002c = uRam0000002c | 2;
    if (*(char *)(param_1 + 0x1a) == '\0') {
      if (*(int *)(param_1 + 0x2c) == 0) {
        return 0;
      }
      *(undefined1 *)(param_1 + 0x1a) = 1;
      aout_play_check_idle(0,1);
      aout_set_r1_frame_over_int_enable(0,1);
    }
    uVar1 = 0;
  }
  return uVar1;
}

