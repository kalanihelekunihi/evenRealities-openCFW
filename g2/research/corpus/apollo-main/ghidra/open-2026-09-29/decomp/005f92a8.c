
int tt_face_load_cvt(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined2 uVar1;
  undefined4 uVar2;
  undefined2 *puVar3;
  undefined2 *puVar4;
  int local_20;
  uint local_1c;
  undefined4 uStack_18;
  
  uVar2 = *(undefined4 *)(param_2 + 0x1c);
  uStack_18 = param_4;
  local_20 = (**(code **)(param_1 + 0x204))(param_1,DAT_005f9518,param_2,&local_1c);
  if (local_20 == 0) {
    *(uint *)(param_1 + 0x298) = local_1c >> 1;
    uVar2 = ft_mem_realloc(uVar2,2,0,*(undefined4 *)(param_1 + 0x298),0,&local_20);
    *(undefined4 *)(param_1 + 0x29c) = uVar2;
    if ((local_20 == 0) &&
       (local_20 = FT_Stream_EnterFrame(param_2,*(int *)(param_1 + 0x298) << 1), local_20 == 0)) {
      puVar3 = *(undefined2 **)(param_1 + 0x29c);
      puVar4 = puVar3 + *(int *)(param_1 + 0x298);
      for (; puVar3 < puVar4; puVar3 = puVar3 + 1) {
        uVar1 = FT_Stream_GetUShort(param_2);
        *puVar3 = uVar1;
      }
      FT_Stream_ExitFrame(param_2);
      if (*(char *)(param_1 + 0x2b9) != '\0') {
        local_20 = tt_face_vary_cvt(param_1,param_2);
      }
    }
  }
  else {
    *(undefined4 *)(param_1 + 0x298) = 0;
    *(undefined4 *)(param_1 + 0x29c) = 0;
    local_20 = 0;
  }
  return local_20;
}

