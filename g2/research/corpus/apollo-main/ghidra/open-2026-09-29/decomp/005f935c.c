
undefined8 tt_face_load_fpgm(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_18;
  undefined4 uStack_14;
  
  local_18 = param_3;
  uStack_14 = param_4;
  iVar1 = (**(code **)(param_1 + 0x204))(param_1,DAT_005f951c,param_2,&local_18);
  if (iVar1 == 0) {
    *(undefined4 *)(param_1 + 0x288) = local_18;
    uVar2 = FT_Stream_ExtractFrame(param_2,local_18,param_1 + 0x28c);
  }
  else {
    *(undefined4 *)(param_1 + 0x28c) = 0;
    *(undefined4 *)(param_1 + 0x288) = 0;
    uVar2 = 0;
  }
  return CONCAT44(local_18,uVar2);
}

