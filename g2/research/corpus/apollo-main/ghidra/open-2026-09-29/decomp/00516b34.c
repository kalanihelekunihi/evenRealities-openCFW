
undefined4
FUN_00516b34(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
            undefined4 param_5,undefined4 param_6,undefined4 param_7,undefined4 param_8)

{
  undefined4 uVar1;
  undefined4 *puVar2;
  
  puVar2 = (undefined4 *)FUN_00514aec(9);
  if (puVar2 == (undefined4 *)0x0) {
    return 0x200;
  }
  *puVar2 = 800;
  puVar2[2] = 0x324;
  puVar2[4] = 0x330;
  puVar2[6] = 0x334;
  puVar2[8] = 0x340;
  puVar2[10] = 0x344;
  puVar2[0xc] = 0x350;
  puVar2[0xe] = 0x354;
  uVar1 = DAT_005171f0;
  puVar2[1] = param_1;
  puVar2[3] = param_2;
  puVar2[5] = param_3;
  puVar2[7] = param_4;
  puVar2[9] = param_5;
  puVar2[0xb] = param_6;
  puVar2[0xd] = param_7;
  puVar2[0xf] = param_8;
  puVar2[0x10] = uVar1;
  puVar2[0x11] = *(uint *)(*DAT_005171ec + 0x18) | 5;
  return 0;
}

