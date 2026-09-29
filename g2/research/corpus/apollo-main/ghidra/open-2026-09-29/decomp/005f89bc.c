
undefined4 tt_face_done(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  if (param_1 != 0) {
    uVar3 = *(undefined4 *)(param_1 + 100);
    uVar2 = *(undefined4 *)(param_1 + 0x68);
    iVar1 = *(int *)(param_1 + 0x21c);
    if (*(int *)(param_1 + 0x2a8) != 0) {
      (**(code **)(param_1 + 0x2a8))(*(undefined4 *)(param_1 + 0x2a4));
    }
    if (iVar1 != 0) {
      (**(code **)(iVar1 + 0xc))(param_1);
    }
    tt_face_done_loca(param_1);
    tt_face_free_hdmx(param_1);
    ft_mem_free(uVar3,*(undefined4 *)(param_1 + 0x29c));
    *(undefined4 *)(param_1 + 0x29c) = 0;
    *(undefined4 *)(param_1 + 0x298) = 0;
    FT_Stream_ReleaseFrame(uVar2,param_1 + 0x28c);
    FT_Stream_ReleaseFrame(uVar2,param_1 + 0x294);
    *(undefined4 *)(param_1 + 0x288) = 0;
    *(undefined4 *)(param_1 + 0x290) = 0;
    tt_done_blend(param_1);
    *(undefined4 *)(param_1 + 700) = 0;
  }
  return param_4;
}

