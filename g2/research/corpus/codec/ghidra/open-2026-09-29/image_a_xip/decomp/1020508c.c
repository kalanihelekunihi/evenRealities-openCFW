
undefined4 aout_set_mute(int param_1,int param_2)

{
  uint uVar1;
  
  uVar1 = (uint)(param_2 != 0);
  uRam00000004 = uVar1 << 9 | uRam00000004 & 0xfffffdff;
  uRam00000014 = uVar1 << 0xf | uVar1 << 0xb | uRam00000014 & 0xffff77ff;
  *(undefined2 *)(param_1 + 0x10) = 1;
  return 0;
}

