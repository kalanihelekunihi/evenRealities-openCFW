
undefined8 FUN_005e1dce(int param_1,int param_2,int param_3,int param_4,uint param_5)

{
  undefined1 uVar1;
  uint uVar2;
  undefined1 *puVar3;
  undefined2 local_18;
  undefined2 local_16;
  int local_14;
  
  local_18 = (undefined2)param_3;
  local_16 = (undefined2)((uint)param_3 >> 0x10);
  uVar2 = param_4 >> 9;
  if ((int)uVar2 < 0) {
    uVar2 = ~uVar2;
  }
  if ((int)((uint)*(byte *)(param_1 + 0xcc) << 0x1e) < 0) {
    uVar2 = uVar2 & 0x1ff;
    if (0xff < uVar2) {
      uVar2 = 0x1ff - uVar2;
    }
  }
  else if (0xff < (int)uVar2) {
    uVar2 = 0xff;
  }
  uVar1 = (undefined1)uVar2;
  if (*(int *)(param_1 + 0xd8) != 0) {
    local_18 = (undefined2)param_2;
    local_16 = (undefined2)param_5;
    local_14 = CONCAT31((int3)((uint)param_4 >> 8),uVar1);
    (**(code **)(param_1 + 0xd8))(param_3,1,&local_18,*(undefined4 *)(param_1 + 0xdc));
    goto LAB_005e1e7c;
  }
  puVar3 = (undefined1 *)((*(int *)(param_1 + 0xd0) - param_3 * *(int *)(param_1 + 0xd4)) + param_2)
  ;
  local_14 = param_4;
  if (param_5 == 0) goto LAB_005e1e7c;
  if (param_5 == 2) {
LAB_005e1e68:
    *puVar3 = uVar1;
    puVar3 = puVar3 + 1;
  }
  else if (1 < param_5) {
    if (param_5 == 4) {
LAB_005e1e60:
      *puVar3 = uVar1;
      puVar3 = puVar3 + 1;
    }
    else if (3 < param_5) {
      if (param_5 == 6) {
LAB_005e1e58:
        *puVar3 = uVar1;
        puVar3 = puVar3 + 1;
      }
      else if (5 < param_5) {
        if (param_5 != 7) {
          FUN_0043c0e4(puVar3,param_5,uVar2 & 0xff);
          goto LAB_005e1e7c;
        }
        *puVar3 = uVar1;
        puVar3 = puVar3 + 1;
        goto LAB_005e1e58;
      }
      *puVar3 = uVar1;
      puVar3 = puVar3 + 1;
      goto LAB_005e1e60;
    }
    *puVar3 = uVar1;
    puVar3 = puVar3 + 1;
    goto LAB_005e1e68;
  }
  *puVar3 = uVar1;
LAB_005e1e7c:
  return CONCAT44(local_14,CONCAT22(local_16,local_18));
}

