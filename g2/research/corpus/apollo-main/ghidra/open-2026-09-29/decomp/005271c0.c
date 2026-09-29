
undefined8 FT_Render_Glyph_Internal(int param_1,int param_2,undefined1 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  undefined4 local_18;
  
  uVar2 = 0;
  local_18 = param_4;
  if (*(int *)(param_2 + 0x48) != DAT_00527504) {
    local_18 = 0;
    if (*(int *)(param_2 + 0x48) == DAT_00527500) {
      iVar1 = *(int *)(param_1 + 0x9c);
      local_18 = *(undefined4 *)(param_1 + 0x94);
    }
    else {
      iVar1 = FT_Lookup_Renderer(param_1,*(undefined4 *)(param_2 + 0x48),&local_18);
    }
    uVar2 = 7;
    while (((iVar1 != 0 &&
            (uVar2 = (**(code **)(iVar1 + 0x3c))(iVar1,param_2,param_3,0), uVar2 != 0)) &&
           ((uVar2 & 0xff) == 0x13))) {
      iVar1 = FT_Lookup_Renderer(param_1,*(undefined4 *)(param_2 + 0x48),&local_18);
    }
  }
  return CONCAT44(local_18,uVar2);
}

