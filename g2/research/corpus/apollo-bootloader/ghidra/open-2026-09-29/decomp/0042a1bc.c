
void spotmgr_power_ton_adjust_42a1bc(uint param_1,int param_2)

{
  uint uVar1;
  uint uVar2;
  
  if (param_2 == 8) {
    param_1 = 7;
  }
  if (param_1 == 0) {
    uVar1 = *(byte *)(DAT_0042ac50 + 0x5c) & 0x1f;
    uVar2 = (*(uint *)(DAT_0042ac50 + 0x5c) & 0x7fff) >> 10;
  }
  else if (param_1 == 2) {
    uVar1 = *(byte *)(DAT_0042ac50 + 0x54) & 0x1f;
    uVar2 = *(byte *)(DAT_0042ac50 + 0x58) & 0x1f;
  }
  else if (param_1 < 2) {
    uVar1 = (*(uint *)(DAT_0042ac50 + 0x5c) & 0x3ff) >> 5;
    uVar2 = (*(uint *)(DAT_0042ac50 + 0x5c) & 0xfffff) >> 0xf;
  }
  else if (param_1 == 4) {
    uVar1 = (*(uint *)(DAT_0042ac50 + 0x54) & 0x3ff) >> 5;
    uVar2 = (*(uint *)(DAT_0042ac50 + 0x58) & 0x3ff) >> 5;
  }
  else if (param_1 < 4) {
    uVar1 = (*(uint *)(DAT_0042ac50 + 0x54) & 0x7fff) >> 10;
    uVar2 = (*(uint *)(DAT_0042ac50 + 0x58) & 0x7fff) >> 10;
  }
  else if (param_1 == 6) {
    uVar1 = *(byte *)(DAT_0042ac50 + 0x60) & 0x1f;
    uVar2 = (*(uint *)(DAT_0042ac50 + 0x60) & 0x7fff) >> 10;
  }
  else if (param_1 < 6) {
    uVar1 = (*(uint *)(DAT_0042ac50 + 0x54) & 0xfffff) >> 0xf;
    uVar2 = (*(uint *)(DAT_0042ac50 + 0x58) & 0xfffff) >> 0xf;
  }
  else if (param_1 == 7) {
    uVar1 = (*DAT_0042aca8 & 0xffff) >> 0xb;
    uVar2 = (*DAT_0042acac & 0x3fffff) >> 0x11;
  }
  else {
    uVar1 = (*(uint *)(DAT_0042ac50 + 0x54) & 0xfffff) >> 0xf;
    uVar2 = (*(uint *)(DAT_0042ac50 + 0x58) & 0xfffff) >> 0xf;
  }
  *DAT_0042aca8 = *DAT_0042aca8 & 0xc1ffffff | uVar1 << 0x19;
  *DAT_0042acb0 = *DAT_0042acb0 & 0xffffe0ff | uVar2 << 8;
  return;
}

