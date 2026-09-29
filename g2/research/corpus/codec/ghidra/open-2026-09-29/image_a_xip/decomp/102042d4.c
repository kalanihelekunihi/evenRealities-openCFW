
undefined4 gx8002_audio_pga_gain(uint param_1)

{
  uint uVar1;
  
  uVar1 = param_1 / 6 - 4;
  if (uVar1 < 5) {
    uVar1 = (uint)(byte)PTR_gx8002_pga_corrections_1020431c[uVar1];
  }
  else {
    uVar1 = 0;
  }
  uRam000001a4 = uRam000001a4 & 0xffffffc0 | param_1 % 6 + param_1 / 6 + uVar1 & 0x3f;
  uRam000001a0 = uRam000001a0 & 0x7fffffff | 0x80000000;
  return 0;
}

