
undefined8
tt_face_init(undefined4 param_1,int param_2,uint param_3,undefined4 param_4,undefined4 param_5)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  undefined4 local_28;
  
  iVar1 = FT_Get_Module_Interface(*(undefined4 *)(*(int *)(param_2 + 0x60) + 4),DAT_005f94f0);
  local_28 = param_4;
  if (iVar1 == 0) {
    uVar2 = 0xb;
  }
  else {
    uVar2 = FT_Stream_Seek(param_1,0);
    if (uVar2 == 0) {
      local_28 = param_5;
      uVar2 = (**(code **)(iVar1 + 4))(param_1,param_2,param_3,param_4);
      uVar3 = *(undefined4 *)(param_2 + 0x68);
      if (uVar2 == 0) {
        if ((((*(int *)(param_2 + 0x94) == 0x10000) || (*(int *)(param_2 + 0x94) == 0x20000)) ||
            (*(int *)(param_2 + 0x94) == DAT_005f94f4)) ||
           ((*(int *)(param_2 + 0x94) == DAT_005f94f8 || (*(int *)(param_2 + 0x94) == DAT_005f94fc))
           )) {
          *(uint *)(param_2 + 8) = *(uint *)(param_2 + 8) | 0x800;
          if ((int)param_3 < 0) {
            uVar2 = 0;
          }
          else {
            uVar2 = (**(code **)(iVar1 + 8))(uVar3,param_2,param_3,param_4);
            if (uVar2 == 0) {
              iVar1 = tt_check_trickyness(param_2);
              if (iVar1 != 0) {
                *(uint *)(param_2 + 8) = *(uint *)(param_2 + 8) | 0x2000;
              }
              uVar2 = tt_face_load_hdmx(param_2,uVar3);
              if (uVar2 == 0) {
                if ((int)((uint)*(byte *)(param_2 + 8) << 0x1f) < 0) {
                  if ((((*(int *)(*(int *)(param_2 + 0x80) + 0x34) == 0) &&
                       (((uVar2 = tt_face_load_loca(param_2,uVar3), *(int *)(param_2 + 0x2b0) != 0
                         && ((uVar2 & 0xff) == 0x8e)) || (uVar2 != 0)))) ||
                      (((uVar2 = tt_face_load_cvt(param_2,uVar3), uVar2 != 0 &&
                        ((uVar2 & 0xff) != 0x8e)) ||
                       ((uVar2 = tt_face_load_fpgm(param_2,uVar3), uVar2 != 0 &&
                        ((uVar2 & 0xff) != 0x8e)))))) ||
                     ((uVar2 = tt_face_load_prep(param_2,uVar3), uVar2 != 0 &&
                      ((uVar2 & 0xff) != 0x8e)))) goto LAB_005f89b8;
                  if ((*(int *)(*(int *)(param_2 + 0x80) + 0x34) == 0) &&
                     (((*(int *)(param_2 + 0x1c) != 0 && (*(int *)(param_2 + 0x2d8) != 0)) &&
                      (iVar1 = tt_check_single_notdef(param_2), iVar1 != 0)))) {
                    *(uint *)(param_2 + 8) = *(uint *)(param_2 + 8) & 0xfffffffe;
                  }
                }
                if ((*(int *)(param_2 + 8) << 0x17 < 0) && (param_3 >> 0x10 != 0)) {
                  uVar2 = TT_Set_Named_Instance(param_2);
                  if (uVar2 != 0) goto LAB_005f89b8;
                  tt_apply_mvar(param_2);
                }
                TT_Init_Glyph_Loading(param_2);
              }
            }
          }
        }
        else {
          uVar2 = 2;
        }
      }
    }
  }
LAB_005f89b8:
  return CONCAT44(local_28,uVar2);
}

