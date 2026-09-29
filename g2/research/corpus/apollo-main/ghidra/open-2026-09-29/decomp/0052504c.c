
undefined8 ft_glyphslot_init(undefined4 *param_1)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 *puVar3;
  undefined4 uVar4;
  int local_18;
  
  puVar3 = *(undefined4 **)(param_1[1] + 0x60);
  iVar2 = puVar3[3];
  uVar4 = puVar3[2];
  local_18 = 0;
  *param_1 = puVar3[1];
  uVar1 = ft_mem_alloc(uVar4,0x28,&local_18);
  if (local_18 == 0) {
    param_1[0x27] = uVar1;
    if (-1 < *(int *)*puVar3 << 0x16) {
      local_18 = FT_GlyphLoader_New(uVar4);
    }
    if ((local_18 == 0) && (*(int *)(iVar2 + 0x40) != 0)) {
      local_18 = (**(code **)(iVar2 + 0x40))(param_1);
    }
  }
  return CONCAT44(local_18,local_18);
}

