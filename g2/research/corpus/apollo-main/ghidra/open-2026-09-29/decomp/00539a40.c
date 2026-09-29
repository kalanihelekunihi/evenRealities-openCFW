
undefined4 FUN_00539a40(uint *param_1,byte *param_2)

{
  uint *puVar1;
  uint *puVar2;
  undefined4 uVar3;
  
  puVar1 = DAT_00539db4;
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_00539dac)) {
    uVar3 = 2;
  }
  else if ((int)(*param_1 << 6) < 0) {
    uVar3 = 7;
  }
  else if (param_2[3] < 0x40) {
    if (param_2[2] == 1) {
      if (0x3bc < *(ushort *)(param_2 + 6) - 4) {
        return 6;
      }
    }
    else if (0x56 < *(ushort *)(param_2 + 6) - 10) {
      return 6;
    }
    if (((param_2[4] < 8) && (param_2[5] < 8)) && (param_2[5] <= param_2[4])) {
      *DAT_00539db4 = *DAT_00539db4 & 0xfffffdff | (param_2[1] & 1) << 9;
      *puVar1 = *puVar1 & 0xffffffdf | (*param_2 & 1) << 5;
      *puVar1 = *puVar1 & 0xfffffff7 | (param_2[2] & 1) << 3;
      *DAT_00539db8 = *(uint *)(param_2 + 8) & 0xffffff | *DAT_00539db8 & 0xff000000;
      puVar2 = DAT_00539dbc;
      *DAT_00539dbc = *DAT_00539dbc & 0xf000ffff | (*(ushort *)(param_2 + 6) & 0xfff) << 0x10;
      *puVar2 = param_2[3] & 0x3f | *puVar2 & 0xffffffc0;
      *puVar2 = *puVar2 & 0xffff8fff | (param_2[4] & 7) << 0xc;
      *puVar2 = *puVar2 & 0xfffff8ff | (param_2[5] & 7) << 8;
      FUN_0044b0b6(*param_2);
      *puVar1 = *puVar1 & 0xffffffef;
      *puVar1 = *puVar1 | 1;
      *puVar1 = *puVar1 & 0xfffffffd;
      *puVar1 = *puVar1 & 0xfffffffb;
      uVar3 = 0;
    }
    else {
      uVar3 = 6;
    }
  }
  else {
    uVar3 = 6;
  }
  return uVar3;
}

