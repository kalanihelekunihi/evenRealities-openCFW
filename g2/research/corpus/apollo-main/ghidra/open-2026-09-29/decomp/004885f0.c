
uint FUN_004885f0(short param_1)

{
  uint uVar1;
  
  for (; param_1 < 0; param_1 = param_1 + 0x168) {
  }
  for (; 0x167 < param_1; param_1 = param_1 + -0x168) {
  }
  if (param_1 < 0x5a) {
    uVar1 = (uint)*(ushort *)(DAT_004888fc + param_1 * 2);
  }
  else if ((int)param_1 - 0x5aU < 0x5a) {
    uVar1 = (uint)*(ushort *)(DAT_004888fc + (short)(0xb4 - param_1) * 2);
  }
  else if ((int)param_1 - 0xb4U < 0x5a) {
    uVar1 = -(uint)*(ushort *)(DAT_004888fc + (short)(param_1 + -0xb4) * 2);
  }
  else {
    uVar1 = -(uint)*(ushort *)(DAT_004888fc + (short)(0x168 - param_1) * 2);
  }
  if (uVar1 == 0x7fff) {
    uVar1 = 0x8000;
  }
  else if (uVar1 == DAT_00488900) {
    uVar1 = DAT_00488904;
  }
  return uVar1;
}

