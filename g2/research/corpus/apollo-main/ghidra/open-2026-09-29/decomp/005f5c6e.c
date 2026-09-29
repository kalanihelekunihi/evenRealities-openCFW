
undefined8 Ins_MD(int param_1,uint *param_2,undefined4 param_3)

{
  undefined4 uVar1;
  uint uVar2;
  int *piVar3;
  uint uVar4;
  int *piVar5;
  uint *local_20;
  undefined4 local_1c;
  
  uVar4 = param_2[1];
  uVar2 = *param_2;
  local_20 = param_2;
  local_1c = param_3;
  if (((uVar2 & 0xffff) < (uint)*(ushort *)(param_1 + 0x2c)) &&
     ((uVar4 & 0xffff) < (uint)*(ushort *)(param_1 + 0x50))) {
    if ((int)((uint)*(byte *)(param_1 + 0x174) << 0x1f) < 0) {
      uVar2 = (**(code **)(param_1 + 0x240))
                        (param_1,*(int *)(*(int *)(param_1 + 0x34) + (uVar2 & 0xffff) * 8) -
                                 *(int *)(*(int *)(param_1 + 0x58) + (uVar4 & 0xffff) * 8),
                         *(int *)(*(int *)(param_1 + 0x34) + (uVar2 & 0xffff) * 8 + 4) -
                         *(int *)(*(int *)(param_1 + 0x58) + (uVar4 & 0xffff) * 8 + 4));
    }
    else if ((*(short *)(param_1 + 0x15c) == 0) || (*(short *)(param_1 + 0x15e) == 0)) {
      piVar3 = (int *)(*(int *)(param_1 + 0x30) + (uVar2 & 0xffff) * 8);
      piVar5 = (int *)(*(int *)(param_1 + 0x54) + (uVar4 & 0xffff) * 8);
      uVar2 = (**(code **)(param_1 + 0x244))(param_1,*piVar3 - *piVar5,piVar3[1] - piVar5[1]);
    }
    else {
      piVar3 = (int *)(*(int *)(param_1 + 0x38) + (uVar2 & 0xffff) * 8);
      piVar5 = (int *)(*(int *)(param_1 + 0x5c) + (uVar4 & 0xffff) * 8);
      if (*(int *)(param_1 + 0xe0) == *(int *)(param_1 + 0xe4)) {
        uVar1 = (**(code **)(param_1 + 0x244))(param_1,*piVar3 - *piVar5,piVar3[1] - piVar5[1]);
        uVar2 = FT_MulFix(uVar1,*(undefined4 *)(param_1 + 0xe0));
      }
      else {
        local_20 = (uint *)FT_MulFix(*piVar3 - *piVar5,*(undefined4 *)(param_1 + 0xe0));
        local_1c = FT_MulFix(piVar3[1] - piVar5[1],*(undefined4 *)(param_1 + 0xe4));
        uVar2 = (**(code **)(param_1 + 0x244))(param_1,local_20,local_1c);
      }
    }
  }
  else {
    if (*(char *)(param_1 + 0x235) != '\0') {
      *(undefined4 *)(param_1 + 0xc) = 0x86;
    }
    uVar2 = 0;
  }
  *param_2 = uVar2;
  return CONCAT44(local_1c,local_20);
}

