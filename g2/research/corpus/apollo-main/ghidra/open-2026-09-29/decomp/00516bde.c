
undefined4
FUN_00516bde(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,int param_5
            ,int param_6)

{
  undefined4 uVar1;
  undefined4 *puVar2;
  uint uVar3;
  uint uVar4;
  
  uVar3 = 0xb;
  if (param_5 != 0) {
    uVar3 = 10;
  }
  uVar4 = 0;
  if (param_6 != 0) {
    if ((*(int *)(*DAT_00517850 + 0x114) == 0) || (param_5 != 0)) {
      uVar4 = 0x7800000;
    }
    else {
      uVar4 = 0x4000000;
    }
  }
  uVar4 = uVar4 & *(uint *)(*DAT_00517850 + 0x8c);
  if (*(char *)(*DAT_005171ec + 8) == '\x01') {
    uVar4 = uVar4 | *(uint *)(*DAT_005171ec + 0xc) & 0xc0000000;
  }
  puVar2 = (undefined4 *)FUN_00514aec(5);
  if (puVar2 == (undefined4 *)0x0) {
    return 0x200;
  }
  *puVar2 = 800;
  puVar2[2] = 0x324;
  puVar2[4] = 0x330;
  uVar1 = DAT_005171f0;
  puVar2[1] = param_1;
  puVar2[3] = param_2;
  puVar2[5] = param_3;
  puVar2[6] = 0x334;
  puVar2[7] = param_4;
  puVar2[8] = uVar1;
  puVar2[9] = uVar3 | uVar4;
  return 0;
}

