
undefined8 cff_ps_get_font_info(int param_1,undefined4 param_2)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  int iVar3;
  int iStack_18;
  
  iVar3 = *(int *)(param_1 + 0x2a4);
  iStack_18 = 0;
  if ((iVar3 != 0) && (*(int *)(iVar3 + 0xc14) == 0)) {
    puVar1 = (undefined4 *)ft_mem_alloc(*(undefined4 *)(param_1 + 100),0x20,&iStack_18);
    if (iStack_18 != 0) goto LAB_005ac304;
    uVar2 = cff_index_get_sid_string(iVar3,*(undefined4 *)(iVar3 + 0x55c));
    *puVar1 = uVar2;
    uVar2 = cff_index_get_sid_string(iVar3,*(undefined4 *)(iVar3 + 0x560));
    puVar1[1] = uVar2;
    uVar2 = cff_index_get_sid_string(iVar3,*(undefined4 *)(iVar3 + 0x568));
    puVar1[2] = uVar2;
    uVar2 = cff_index_get_sid_string(iVar3,*(undefined4 *)(iVar3 + 0x56c));
    puVar1[3] = uVar2;
    uVar2 = cff_index_get_sid_string(iVar3,*(undefined4 *)(iVar3 + 0x570));
    puVar1[4] = uVar2;
    puVar1[5] = *(undefined4 *)(iVar3 + 0x578);
    *(undefined1 *)(puVar1 + 6) = *(undefined1 *)(iVar3 + 0x574);
    *(short *)((int)puVar1 + 0x1a) = (short)*(undefined4 *)(iVar3 + 0x57c);
    *(short *)(puVar1 + 7) = (short)*(undefined4 *)(iVar3 + 0x580);
    *(undefined4 **)(iVar3 + 0xc14) = puVar1;
  }
  if (iVar3 != 0) {
    FUN_00439c04(param_2,*(undefined4 *)(iVar3 + 0xc14),0x20);
  }
LAB_005ac304:
  return CONCAT44(iStack_18,iStack_18);
}

