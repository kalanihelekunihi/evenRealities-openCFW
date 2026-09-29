
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void translate_ui_0059e6d0(ushort *param_1)

{
  char *pcVar1;
  int *piVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  ushort *puVar7;
  ushort *puVar8;
  
  if (param_1 == (ushort *)0x0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_translate_data_0059ea24,PTR_s_D__01_workspace_s200_ap510b_iar__0059ea20,
                   PTR_s_translate_data_update_0059ea1c,0x21,PTR_s_translate_data_is_NULL_0059ea18);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__translate_data_translate_data_i_0059ea28,
                          PTR_s__translate_data_translate_data_i_0059ea28);
    }
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_translate_data_0059ea24,PTR_s_D__01_workspace_s200_ap510b_iar__0059ea20,
                   PTR_s_translate_data_update_0059ea1c,0x25,PTR_s_endFlag___d_0059ea2c,
                   *(undefined4 *)(param_1 + 0x404));
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc400000,PTR_s__translate_data_endFlag___d_0059ea30,
                          PTR_s__translate_data_endFlag___d_0059ea30,
                          *(undefined4 *)(param_1 + 0x404));
    }
    if (*(int *)(param_1 + 0x404) == 1) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_translate_data_0059ea24,PTR_s_D__01_workspace_s200_ap510b_iar__0059ea20
                     ,PTR_s_translate_data_update_0059ea1c,0x27,PTR_s_src_text_len___d____s_0059ea34
                     ,*param_1,param_1 + 1);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0xc800000,PTR_s__translate_data_src_text_len___d_0059ea38,
                            PTR_s__translate_data_src_text_len___d_0059ea38,*param_1,param_1 + 1);
      }
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_translate_data_0059ea24,PTR_s_D__01_workspace_s200_ap510b_iar__0059ea20
                     ,PTR_s_translate_data_update_0059ea1c,0x28,PTR_s_dst_text_len___d____s_0059ea3c
                     ,param_1[0x201],param_1 + 0x202);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0xc800000,PTR_s__translate_data_dst_text_len___d_0059ea40,
                            PTR_s__translate_data_dst_text_len___d_0059ea40,param_1[0x201],
                            param_1 + 0x202);
      }
    }
    pcVar1 = _DAT_0059ea48;
    iVar3 = DAT_0059ea44;
    puVar7 = (ushort *)(DAT_0059ea44 + (uint)*(byte *)(DAT_0059ea44 + 0x2010) * 0x402);
    puVar8 = (ushort *)((uint)*(byte *)(DAT_0059ea44 + 0x2010) * 0x402 + DAT_0059ea44 + 0x1008);
    if (*_DAT_0059ea48 == '\x01') {
      *_DAT_0059ea48 = '\0';
      if (*puVar7 < 0x401) {
        *(undefined1 *)((int)puVar7 + *puVar7 + 2) = 10;
        *puVar7 = *puVar7 + 1;
      }
      if (*puVar8 < 0x401) {
        *(undefined1 *)((int)puVar8 + *puVar8 + 2) = 10;
        *puVar8 = *puVar8 + 1;
      }
      uVar4 = *(byte *)(iVar3 + 0x2010) + 1;
      *(char *)(iVar3 + 0x2010) = (char)uVar4 + (char)(uVar4 / 4) * -4;
      puVar7 = (ushort *)(iVar3 + (uint)*(byte *)(iVar3 + 0x2010) * 0x402);
      puVar8 = (ushort *)((uint)*(byte *)(iVar3 + 0x2010) * 0x402 + iVar3 + 0x1008);
    }
    FUN_0043c0e4(puVar7,0x402,0);
    FUN_0043c0e4(puVar8,0x402,0);
    FUN_00439be4(puVar7 + 1,param_1 + 1,*param_1);
    *puVar7 = *param_1;
    FUN_00439be4(puVar8 + 1,param_1 + 0x202,param_1[0x201]);
    *puVar8 = param_1[0x201];
    if (*(int *)(param_1 + 0x404) == 1) {
      *pcVar1 = '\x01';
    }
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_translate_data_0059ea24,PTR_s_D__01_workspace_s200_ap510b_iar__0059ea20,
                   PTR_s_translate_data_update_0059ea1c,0x51,_DAT_0059ea4c);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x10000000,_DAT_0059ea50,_DAT_0059ea50);
    }
    FUN_0043c0e4(DAT_0059ea54,0x1008,0);
    *_DAT_0059ea58 = 0;
    FUN_0043c0e4(DAT_0059ea5c,0x1008,0);
    *_DAT_0059ea60 = 0;
    for (iVar5 = 0; piVar2 = _DAT_0059ea58, iVar5 < 4; iVar5 = iVar5 + 1) {
      iVar6 = (int)(iVar5 + (uint)*(byte *)(iVar3 + 0x2010) + 1) % 4;
      puVar8 = (ushort *)(iVar3 + iVar6 * 0x402);
      iVar6 = iVar6 * 0x402 + iVar3;
      puVar7 = (ushort *)(iVar6 + 0x1008);
      if ((*puVar8 != 0) || (*puVar7 != 0)) {
        FUN_00439be4(DAT_0059ea54 + *_DAT_0059ea58,puVar8 + 1,*puVar8);
        *piVar2 = *piVar2 + (uint)*puVar8;
        piVar2 = _DAT_0059ea60;
        FUN_00439be4(DAT_0059ea5c + *_DAT_0059ea60,iVar6 + 0x100a,*puVar7);
        *piVar2 = *piVar2 + (uint)*puVar7;
      }
    }
  }
  return;
}

