
undefined4
load_face_in_embedded_rfork
          (undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,int param_5)

{
  bool bVar1;
  char cVar2;
  uint uVar3;
  undefined4 uVar4;
  uint uVar5;
  undefined4 local_b8;
  undefined4 local_b4 [3];
  int local_a8;
  int local_94 [9];
  undefined4 local_70 [9];
  int local_4c [9];
  undefined4 local_28;
  
  uVar4 = *param_1;
  uVar3 = 2;
  bVar1 = false;
  local_b8 = 0;
  local_28 = param_3;
  FT_Raccess_Guess(param_1,param_2,*(undefined4 *)(param_5 + 0xc),local_4c,local_70,local_94);
  for (uVar5 = 0; uVar5 < 9; uVar5 = uVar5 + 1) {
    cVar2 = ft_raccess_rule_by_darwin_vfs(param_1,uVar5);
    if (((cVar2 == '\0') || (!bVar1)) && (local_94[uVar5] == 0)) {
      local_b4[0] = 4;
      if (local_4c[uVar5] == 0) {
        local_a8 = *(int *)(param_5 + 0xc);
      }
      else {
        local_a8 = local_4c[uVar5];
      }
      uVar3 = FT_Stream_New(param_1,local_b4,&local_b8);
      if ((cVar2 != '\0') && ((uVar3 & 0xff) == 0x51)) {
        bVar1 = true;
      }
      if (uVar3 == 0) {
        uVar3 = IsMacResource(param_1,local_b8,local_70[uVar5],local_28,param_4);
        FT_Stream_Free(local_b8,0);
        if (uVar3 == 0) break;
        if (cVar2 != '\0') {
          bVar1 = true;
        }
      }
    }
  }
  for (uVar5 = 0; uVar5 < 9; uVar5 = uVar5 + 1) {
    if (local_4c[uVar5] != 0) {
      ft_mem_free(uVar4,local_4c[uVar5]);
      local_4c[uVar5] = 0;
    }
  }
  uVar4 = 0;
  if (uVar3 != 0) {
    uVar4 = 2;
  }
  return uVar4;
}

