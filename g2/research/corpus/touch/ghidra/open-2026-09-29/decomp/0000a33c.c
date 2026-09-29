
void power_mode_set(uint param_1)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  iVar1 = DAT_0000a370;
  if (param_1 < 0x11) {
    uVar2 = 0;
  }
  else if (param_1 < 0x21) {
    uVar2 = 1;
  }
  else {
    uVar2 = 2;
  }
  *(uint *)(DAT_0000a370 + 0x30) = *(uint *)(DAT_0000a370 + 0x30) & 0xfffffffc | uVar2;
  uVar3 = 0;
  if (uVar2 != 0) {
    uVar3 = 0x10;
  }
  *(uint *)(DAT_0000a370 + 0x30) = *(uint *)(iVar1 + 0x30) & 0xffffffef | uVar3;
  return;
}

