
undefined8
drv_pdm_buffer_get(int *param_1,undefined4 *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 *puVar2;
  uint uVar3;
  undefined4 *local_28;
  undefined4 uStack_24;
  undefined4 uStack_20;
  
  local_28 = param_2;
  uStack_24 = param_3;
  uStack_20 = param_4;
  puVar2 = (undefined4 *)FUN_0059262c(*DAT_0057ba48);
  uStack_24 = *(undefined4 *)(DAT_0057ba80 + 4);
  local_28 = puVar2;
  FUN_00475014(&local_28,0);
  iVar1 = DAT_0057ba84;
  FUN_0043c0e4(DAT_0057ba84,0x140,0);
  for (uVar3 = 0; uVar3 < 0xa0; uVar3 = uVar3 + 1) {
    *(char *)(iVar1 + uVar3 * 2) = (char)((uint)puVar2[uVar3] >> 8);
    *(char *)(iVar1 + uVar3 * 2 + 1) = (char)((uint)puVar2[uVar3] >> 0x10);
  }
  *param_1 = iVar1;
  *param_2 = 0x140;
  return CONCAT44(uStack_24,local_28);
}

