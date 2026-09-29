
undefined8
FUN_00452bca(undefined4 param_1,undefined4 param_2,undefined4 *param_3,undefined4 param_4)

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
  uVar3 = FUN_0045253c(param_1,param_2);
  param_3[8] = uVar3;
  if (param_3[8] != 0) {
    uVar1 = FUN_0045257c(param_1,param_2);
    *(undefined1 *)(param_3 + 0xf) = uVar1;
    if (2 < *(byte *)(param_3 + 0xf)) {
      bVar2 = FUN_00452df0(param_1,param_2,param_3);
      if (bVar2 < 0xfd) {
        *(char *)(param_3 + 0xf) = (char)((uint)bVar2 * (uint)*(byte *)(param_3 + 0xf) >> 8);
      }
      if (2 < *(byte *)(param_3 + 0xf)) {
        uVar3 = FUN_0045255c(param_1,param_2);
        local_18 = (undefined4 *)FUN_00452e22(param_1,param_2,param_3,uVar3);
        FUN_00439be4(param_3 + 7,&local_18,3);
        uVar3 = FUN_00452588(param_1,param_2);
        param_3[0xe] = uVar3;
        bVar2 = FUN_00452546(param_1,param_2);
        *(byte *)((int)param_3 + 0x3d) = *(byte *)((int)param_3 + 0x3d) & 0xfe | bVar2 & 1;
      }
    }
  }
  return CONCAT44(uStack_14,local_18);
}

