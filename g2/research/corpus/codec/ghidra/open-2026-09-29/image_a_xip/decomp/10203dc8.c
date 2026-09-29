
undefined4
_pcm_channel_setting_isra_0(int param_1,uint param_2,uint param_3,uint param_4,undefined4 param_5)

{
  int iVar1;
  undefined4 uVar2;
  
  if (((param_4 & 0x7f) == 0) && (((param_2 | param_3) & 7) == 0)) {
    iVar1 = param_1 * 0x24;
    *(undefined4 *)(iVar1 + 0x110) = param_5;
    *(uint *)(iVar1 + 0x114) = param_2;
    *(uint *)(iVar1 + 0x11c) = param_3;
    *(uint *)(iVar1 + 0x120) = param_4;
    iRam00000104 = 1 << (param_1 + 0xbU & 0x3f);
    uVar2 = 0;
  }
  else {
    uVar2 = 0xffffffff;
  }
  return uVar2;
}

