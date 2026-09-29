
int tt_face_load_hdmx(int param_1,int param_2,int param_3,uint param_4)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  undefined4 uVar4;
  uint uVar5;
  undefined1 *puVar6;
  undefined1 *puVar7;
  int local_28;
  uint local_24;
  
  uVar4 = *(undefined4 *)(param_2 + 0x1c);
  local_28 = param_3;
  local_24 = param_4;
  local_28 = (**(code **)(param_1 + 0x204))(param_1,DAT_005f9524,param_2,&local_24,param_1,param_2);
  if ((local_28 == 0) && (7 < local_24)) {
    local_28 = FT_Stream_ExtractFrame(param_2,local_24,param_1 + 0x2dc);
    if (local_28 == 0) {
      iVar1 = *(int *)(param_1 + 0x2dc);
      puVar7 = (undefined1 *)(iVar1 + local_24);
      uVar3 = (uint)CONCAT11(*(undefined1 *)(iVar1 + 2),*(undefined1 *)(iVar1 + 3));
      puVar6 = (undefined1 *)(iVar1 + 8);
      uVar5 = (uint)*(byte *)(iVar1 + 7) |
              (uint)*(byte *)(iVar1 + 5) << 0x10 | (uint)*(byte *)(iVar1 + 4) << 0x18 |
              (uint)*(byte *)(iVar1 + 6) << 8;
      if (DAT_005f9528 <= uVar5) {
        uVar5 = (uint)CONCAT11(*(byte *)(iVar1 + 6),*(byte *)(iVar1 + 7));
      }
      if ((uVar3 < 0x100) && ((uVar3 == 0 || (uVar5 - 4 < 0xfffe)))) {
        uVar4 = ft_mem_realloc(uVar4,1,0,uVar3,0,&local_28);
        *(undefined4 *)(param_1 + 0x2ec) = uVar4;
        if (local_28 == 0) {
          uVar2 = 0;
          for (; (uVar2 < uVar3 && (puVar6 + uVar5 <= puVar7)); puVar6 = puVar6 + uVar5) {
            *(undefined1 *)(*(int *)(param_1 + 0x2ec) + uVar2) = *puVar6;
            uVar2 = uVar2 + 1;
          }
          *(uint *)(param_1 + 0x2e4) = uVar2;
          *(uint *)(param_1 + 0x2e0) = local_24;
          *(uint *)(param_1 + 0x2e8) = uVar5;
          return 0;
        }
      }
      else {
        local_28 = 3;
      }
      FT_Stream_ReleaseFrame(param_2,param_1 + 0x2dc);
      *(undefined4 *)(param_1 + 0x2e0) = 0;
    }
  }
  else {
    local_28 = 0;
  }
  return local_28;
}

