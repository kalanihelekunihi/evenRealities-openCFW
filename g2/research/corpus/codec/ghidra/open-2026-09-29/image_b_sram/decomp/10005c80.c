
undefined4 gx_audio_in_get_fftvad_state(undefined4 *param_1)

{
  undefined4 uVar1;
  
  if (param_1 == (undefined4 *)0x0) {
    uVar1 = 0xffffffff;
  }
  else {
    param_1[2] = uRam00000174;
    param_1[1] = uRam00000178;
    *param_1 = uRam0000017c;
    *(ushort *)(param_1 + 3) = (ushort)((uint)uRam0000010c >> 0x10) & 0x3f;
    uVar1 = 0;
  }
  return uVar1;
}

