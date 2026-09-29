
undefined4 gx8002_aout_config_pcm(int param_1,uint *param_2)

{
  byte bVar1;
  uint uVar2;
  undefined4 uVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;
  
  bVar1 = *(byte *)((int)param_2 + 5);
  if (bVar1 == 0x10) {
    uVar6 = 8;
  }
  else {
    if (bVar1 != 0x20) {
      return 0xffffffff;
    }
    uVar6 = 0;
  }
  uVar2 = param_2[2];
  if ((uVar2 != 0) && (uVar4 = uVar2 / *param_2, uVar2 == uVar4 * *param_2)) {
    if (uVar4 == 0x180) {
      iVar5 = *(int *)(param_1 + 0x30);
      uVar3 = 4;
    }
    else if (uVar4 < 0x181) {
      if (uVar4 == 0xc0) {
        iVar5 = *(int *)(param_1 + 0x30);
        uVar3 = 7;
      }
      else if (uVar4 == 0x100) {
        iVar5 = *(int *)(param_1 + 0x30);
        uVar3 = 0;
      }
      else {
        if (uVar4 != 0x80) {
          return 0xffffffff;
        }
        iVar5 = *(int *)(param_1 + 0x30);
        uVar3 = 3;
      }
    }
    else if (uVar4 == 0x300) {
      iVar5 = *(int *)(param_1 + 0x30);
      uVar3 = 5;
    }
    else if (uVar4 < 0x301) {
      if (uVar4 != 0x200) {
        return 0xffffffff;
      }
      iVar5 = *(int *)(param_1 + 0x30);
      uVar3 = 1;
    }
    else if (uVar4 == 0x400) {
      iVar5 = *(int *)(param_1 + 0x30);
      uVar3 = 2;
    }
    else {
      if (uVar4 != 0x600) {
        return 0xffffffff;
      }
      iVar5 = *(int *)(param_1 + 0x30);
      uVar3 = 6;
    }
    *(undefined4 *)(iVar5 + 0x10) = uVar3;
    *(byte *)(param_1 + 0x19) = bVar1 >> 3;
    uRam00000000 = (uint)(*(char *)((int)param_2 + 7) != '\0') << 4 |
                   (uint)(*(char *)((int)param_2 + 6) != '\0') << 7 |
                   (uint)((char)param_2[1] != '\x01') << 6 | uVar6 | uRam00000000 & 0xffffff00;
    aout_i2s_config(0,*(int *)(param_1 + 0x30) + 8);
    aout_dac_config(0,*(int *)(param_1 + 0x30) + 0x30);
    gx8002_aout_set_lodac();
    return 0;
  }
  gx8002_printf(uRam10204e68);
  return 0xffffffff;
}

