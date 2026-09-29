
undefined8 tt_get_advances(int param_1,int param_2,undefined4 *param_3,uint param_4,int param_5)

{
  undefined4 uVar1;
  undefined4 *puVar2;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  
  uStack_20 = param_3;
  uStack_1c = param_4;
  if ((int)(param_4 << 0x1b) < 0) {
    if ((((*(uint *)(param_1 + 4) & DAT_005efb00) != 0) || (*(int *)(param_1 + 8) << 0x10 < 0)) &&
       (-1 < (int)((uint)*(byte *)(param_1 + 0x2c0) << 0x1b))) {
      uVar1 = 7;
      goto LAB_005ef1b8;
    }
    for (puVar2 = (undefined4 *)0x0; puVar2 < param_3; puVar2 = (undefined4 *)((int)puVar2 + 1)) {
      uStack_20 = &uStack_1c;
      TT_Get_VMetrics(param_1,(int)puVar2 + param_2,0,(int)&uStack_1c + 2);
      *(uint *)(param_5 + (int)puVar2 * 4) = uStack_1c & 0xffff;
    }
  }
  else {
    if ((((*(uint *)(param_1 + 4) & DAT_005efb00) != 0) || (*(int *)(param_1 + 8) << 0x10 < 0)) &&
       (-1 < (int)((uint)*(byte *)(param_1 + 0x2c0) << 0x1e))) {
      uVar1 = 7;
      goto LAB_005ef1b8;
    }
    for (puVar2 = (undefined4 *)0x0; puVar2 < param_3; puVar2 = (undefined4 *)((int)puVar2 + 1)) {
      TT_Get_HMetrics(param_1,(int)puVar2 + param_2,(int)&uStack_20 + 2,&uStack_20);
      *(uint *)(param_5 + (int)puVar2 * 4) = (uint)uStack_20 & 0xffff;
    }
  }
  uVar1 = 0;
LAB_005ef1b8:
  return CONCAT44(uStack_20,uVar1);
}

