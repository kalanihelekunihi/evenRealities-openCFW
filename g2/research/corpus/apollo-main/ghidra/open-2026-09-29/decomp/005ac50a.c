
undefined4 cff_get_cid_from_glyph_index(int param_1,uint param_2,uint *param_3)

{
  undefined4 uVar1;
  int iVar2;
  
  uVar1 = 0;
  iVar2 = *(int *)(param_1 + 0x2a4);
  if (iVar2 != 0) {
    if (*(int *)(iVar2 + 0x5e0) == 0xffff) {
      uVar1 = 6;
    }
    else if (*(uint *)(iVar2 + 0x14) < param_2) {
      uVar1 = 6;
    }
    else if (param_3 != (uint *)0x0) {
      *param_3 = (uint)*(ushort *)(*(int *)(iVar2 + 0x4a4) + param_2 * 2);
    }
  }
  return uVar1;
}

