
void FUN_00522e9c(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                 undefined4 param_5,undefined4 param_6,undefined4 param_7,undefined4 param_8)

{
  undefined4 uVar1;
  undefined4 *puVar2;
  
  puVar2 = (undefined4 *)FUN_00514aec(9);
  if (puVar2 != (undefined4 *)0x0) {
    *puVar2 = 0x120;
    puVar2[5] = param_3;
    puVar2[0xd] = param_7;
    puVar2[1] = param_1;
    puVar2[3] = param_2;
    puVar2[6] = 0x134;
    puVar2[7] = param_4;
    puVar2[0xb] = param_6;
    puVar2[0xf] = param_8;
    puVar2[0xe] = 0x154;
    uVar1 = DAT_005232cc;
    puVar2[2] = 0x124;
    puVar2[4] = 0x130;
    puVar2[8] = 0x140;
    puVar2[9] = param_5;
    puVar2[10] = 0x144;
    puVar2[0xc] = 0x150;
    puVar2[0x10] = uVar1;
    puVar2[0x11] = *(uint *)(*DAT_005232d0 + 0x18) | 5;
  }
  return;
}

