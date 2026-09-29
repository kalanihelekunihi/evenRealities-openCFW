
undefined4 Cy_MSCLP_Configure(undefined4 *param_1,undefined4 *param_2,uint param_3,byte *param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  
  uVar2 = DAT_00009174;
  if ((param_3 != 0) && (uVar2 = DAT_0000915c, *param_4 == param_3)) {
    *param_1 = *param_2;
    param_1[2] = param_2[1];
    param_1[3] = param_2[2];
    param_1[4] = param_2[3];
    param_1[5] = param_2[4];
    param_1[6] = param_2[5];
    param_1[7] = param_2[6];
    param_1[8] = param_2[7];
    param_1[9] = param_2[8];
    param_1[10] = param_2[9];
    param_1[0xc] = param_2[10];
    param_1[0xd] = param_2[0xb];
    param_1[0xe] = param_2[0xc];
    param_1[0x14] = param_2[0xd];
    param_1[0x1c] = param_2[0xe];
    param_1[0x1d] = param_2[0xf];
    param_1[0x20] = param_2[0x10];
    param_1[0x21] = param_2[0x11];
    param_1[0x40] = param_2[0x12];
    param_1[0x41] = param_2[0x13];
    param_1[0x42] = param_2[0x14];
    param_1[0x48] = param_2[0x15];
    param_1[0x49] = param_2[0x16];
    param_1[0x4a] = param_2[0x17];
    param_1[0x81] = param_2[0x18];
    param_1[0x82] = param_2[0x19];
    param_1[0x83] = param_2[0x1a];
    param_1[0x88] = param_2[0x1b];
    for (uVar3 = 0; uVar3 < 8; uVar3 = uVar3 + 1) {
      param_1[uVar3 + 0x100] = param_2[uVar3 + 0x1c];
    }
    for (uVar3 = 0; iVar1 = DAT_00009168, uVar3 < 3; uVar3 = uVar3 + 1) {
      param_1[(uVar3 + 0x18) * 0x10] = param_2[uVar3 * 7 + 0x24];
      param_1[(uVar3 + 0x18) * 0x10 + 1] = param_2[uVar3 * 7 + 0x25];
      param_1[uVar3 * 0x10 + 0x182] = param_2[uVar3 * 7 + 0x26];
      *(undefined4 *)((int)param_1 + DAT_00009160 + uVar3 * 0x40) = param_2[uVar3 * 7 + 0x27];
      param_1[uVar3 * 0x10 + 0x184] = param_2[uVar3 * 7 + 0x28];
      *(undefined4 *)((int)param_1 + DAT_00009164 + uVar3 * 0x40) = param_2[uVar3 * 7 + 0x29];
      param_1[uVar3 * 0x10 + 0x186] = param_2[uVar3 * 7 + 0x2a];
    }
    uVar3 = param_2[0x11] & 7;
    if (uVar3 == 3) {
      *(uint *)((int)param_1 + DAT_0000916c) = (uint)*(byte *)(DAT_00009168 + 0x95);
      *(uint *)((int)param_1 + DAT_00009170) = (uint)*(byte *)(iVar1 + 0x97);
      uVar2 = 0;
    }
    else if (uVar3 == 6) {
      *(uint *)((int)param_1 + DAT_0000916c) = (uint)*(byte *)(DAT_00009168 + 0x8c);
      *(uint *)((int)param_1 + DAT_00009170) = (uint)*(byte *)(iVar1 + 0x8e);
      uVar2 = 0;
    }
    else {
      uVar2 = DAT_00009174;
      if (uVar3 == 0) {
        *(uint *)((int)param_1 + DAT_0000916c) = (uint)*(byte *)(DAT_00009168 + 0x9e);
        *(uint *)((int)param_1 + DAT_00009170) = (uint)*(byte *)(iVar1 + 0xa0);
        uVar2 = 0;
      }
    }
  }
  return uVar2;
}

