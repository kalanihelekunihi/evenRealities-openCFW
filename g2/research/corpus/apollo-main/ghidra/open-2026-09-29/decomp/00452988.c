
undefined8
FUN_00452988(undefined4 param_1,undefined4 param_2,undefined4 *param_3,undefined4 param_4)

{
  undefined1 uVar1;
  byte bVar2;
  undefined4 uVar3;
  undefined4 *local_18;
  undefined4 uStack_14;
  
  *param_3 = param_1;
  param_3[1] = param_2;
  local_18 = param_3;
  uStack_14 = param_4;
  uVar1 = FUN_004525b2(param_1,param_2);
  *(undefined1 *)(param_3 + 0x14) = uVar1;
  if (2 < *(byte *)(param_3 + 0x14)) {
    bVar2 = FUN_00452df0(param_1,param_2,param_3);
    if (bVar2 < 0xfd) {
      *(char *)(param_3 + 0x14) = (char)((uint)bVar2 * (uint)*(byte *)(param_3 + 0x14) >> 8);
    }
    if (2 < *(byte *)(param_3 + 0x14)) {
      uVar3 = FUN_00452592(param_1,param_2);
      local_18 = (undefined4 *)FUN_00452e22(param_1,param_2,param_3,uVar3);
      FUN_00439be4(param_3 + 9,&local_18,3);
      uVar3 = FUN_004525c8(param_1,param_2);
      param_3[0xb] = uVar3;
      uVar3 = FUN_004525d2(param_1,param_2);
      param_3[10] = uVar3;
      bVar2 = FUN_004525dc(param_1,param_2);
      *(byte *)((int)param_3 + 0x53) = *(byte *)((int)param_3 + 0x53) & 0xf8 | bVar2 & 7;
      uVar3 = FUN_004525be(param_1,param_2);
      param_3[8] = uVar3;
      uVar1 = FUN_004525e8(param_1,param_2);
      *(undefined1 *)((int)param_3 + 0x51) = uVar1;
    }
  }
  return CONCAT44(uStack_14,local_18);
}

