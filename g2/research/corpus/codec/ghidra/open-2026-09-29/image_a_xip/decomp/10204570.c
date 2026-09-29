
undefined4 gx_audio_in_set_fftvad_enable(uint param_1,int param_2,int param_3)

{
  uint uVar1;
  
  uVar1 = 0;
  if (param_3 != 0) {
    uVar1 = param_3 - 1U & 0xff;
  }
  uRam00000104 = 0x20000;
  uRam00000100 = uRam00000100 & 0xfffcffff | 0x30000;
  uRam00000158 = uRam00000158 & 0x3cffff80 | uVar1 & 0x7f | ((byte)~(param_2 != 0) & 1) << 0x18 |
                 (param_1 & 1) << 0x19 | (param_1 & 1) << 0x1e | (uint)(byte)~(param_1 != 0) << 0x1f
  ;
  return 0;
}

