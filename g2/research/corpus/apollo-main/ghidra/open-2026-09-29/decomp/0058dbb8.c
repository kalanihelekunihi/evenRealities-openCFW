
undefined8 FUN_0058dbb8(uint *param_1,uint param_2,char param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  
  iVar1 = DAT_0058e450;
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_0058e3f0)) {
    uVar2 = 2;
  }
  else {
    uVar3 = param_1[10];
    if (param_2 == 0) {
      if ((param_3 != '\0') && ((char)param_1[1] == '\0')) {
        uVar2 = 7;
        goto LAB_0058dc86;
      }
      FUN_0047f5b8(uVar3 + 0xb & 0xff);
      if (param_3 != '\0') {
        if ((DAT_0058e444 <= param_1[0xc]) && (0x21 < (*DAT_0058e448 & 0xff))) {
          *DAT_0058e44c = *DAT_0058e44c | 0x400000 << (uVar3 & 0xff);
        }
        FUN_004c44bc((char)param_1[0x46],uVar3 + 0xb & 0xff);
        iVar1 = DAT_0058e450;
        *(uint *)(DAT_0058e450 + uVar3 * 0x1000 + 0x20) = param_1[2];
        *(uint *)(iVar1 + uVar3 * 0x1000 + 0x24) = param_1[3];
        *(uint *)(iVar1 + uVar3 * 0x1000 + 0x28) = param_1[4];
        *(uint *)(iVar1 + uVar3 * 0x1000 + 0x2c) = param_1[5];
        *(uint *)(iVar1 + uVar3 * 0x1000 + 0x30) = param_1[6];
        *(uint *)(iVar1 + uVar3 * 0x1000 + 0x34) = param_1[7];
        *(uint *)(iVar1 + uVar3 * 0x1000 + 0x38) = param_1[8];
        *(uint *)(iVar1 + uVar3 * 0x1000 + 0x48) = param_1[9];
        *(undefined1 *)(param_1 + 1) = 0;
      }
    }
    else {
      if ((param_2 != 2) && (1 < param_2)) {
        uVar2 = 6;
        goto LAB_0058dc86;
      }
      if (param_3 != '\0') {
        param_1[2] = *(uint *)(DAT_0058e450 + uVar3 * 0x1000 + 0x20);
        param_1[3] = *(uint *)(iVar1 + uVar3 * 0x1000 + 0x24);
        param_1[4] = *(uint *)(iVar1 + uVar3 * 0x1000 + 0x28);
        param_1[5] = *(uint *)(iVar1 + uVar3 * 0x1000 + 0x2c);
        param_1[6] = *(uint *)(iVar1 + uVar3 * 0x1000 + 0x30);
        param_1[7] = *(uint *)(iVar1 + uVar3 * 0x1000 + 0x34);
        param_1[8] = *(uint *)(iVar1 + uVar3 * 0x1000 + 0x38);
        param_1[9] = *(uint *)(iVar1 + uVar3 * 0x1000 + 0x48);
        *(undefined1 *)(param_1 + 1) = 1;
      }
      if ((DAT_0058e444 <= param_1[0xc]) && (0x21 < (*DAT_0058e448 & 0xff))) {
        *DAT_0058e44c = *DAT_0058e44c & ~(0x400000 << (uVar3 & 0xff));
      }
      FUN_004c4530((char)param_1[0x46],uVar3 + 0xb & 0xff);
      FUN_0058e7e4(param_1,0xffffffff);
      *(undefined4 *)(DAT_0058e450 + uVar3 * 0x1000 + 0x30) = 0;
      FUN_0047f7ae(uVar3 + 0xb & 0xff);
    }
    uVar2 = 0;
  }
LAB_0058dc86:
  return CONCAT44(param_4,uVar2);
}

