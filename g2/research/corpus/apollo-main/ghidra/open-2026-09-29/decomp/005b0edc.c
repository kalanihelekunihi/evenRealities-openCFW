
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_005b0edc(byte param_1,char param_2,undefined *param_3)

{
  byte bVar1;
  byte bVar2;
  int iVar3;
  undefined *puVar4;
  uint uVar5;
  byte bVar6;
  
  iVar3 = DAT_005b15d8;
  if (*(int *)(DAT_005b15d8 + 100) != 0) {
    if (param_1 < 3) {
      bVar1 = FUN_005b0c30(*(undefined1 *)(DAT_005b15d8 + 0x97));
      bVar2 = FUN_005b0c30(param_1);
      if (param_2 == '\0') {
        FUN_005b0d24(iVar3,param_1);
      }
      else {
        bVar6 = bVar1;
        if (bVar1 < bVar2) {
          for (; (bVar6 < bVar2 && (bVar6 < 4)); bVar6 = bVar6 + 1) {
            FUN_005b0ca0(*(undefined4 *)(iVar3 + (uint)bVar6 * 4 + 0x6c),0xff,0,
                         ((uint)bVar6 - (uint)bVar1) * 0x32,300);
          }
        }
        else {
          bVar6 = 0;
          uVar5 = (uint)bVar1;
          while ((uVar5 = uVar5 - 1, (int)(uint)bVar2 <= (int)uVar5 && (-1 < (int)uVar5))) {
            FUN_005b0ca0(*(undefined4 *)(iVar3 + uVar5 * 4 + 0x6c),0,0xff,(uint)bVar6 * 0x32,300);
            bVar6 = bVar6 + 1;
          }
        }
      }
      *(byte *)(iVar3 + 0x97) = param_1;
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        puVar4 = PTR_DAT_005b1a64;
        if (param_3 != (undefined *)0x0) {
          puVar4 = param_3;
        }
        FUN_0043d574(3,DAT_005b15d0,DAT_005b15cc,PTR_s_conversate_ui_list_view_mode_set_005b1994,
                     0x11b,PTR_s_List_view_mode__>__d__reason___s_005b1a68,param_1,puVar4);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        if (param_3 == (undefined *)0x0) {
          param_3 = PTR_DAT_005b1a64;
        }
        compress_log_output(0xc800000,PTR_s__conversate_ui_List_view_mode__>_005b1a6c,
                            PTR_s__conversate_ui_List_view_mode__>_005b1a6c,param_1,param_3);
      }
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(2,DAT_005b15d0,DAT_005b15cc,PTR_s_conversate_ui_list_view_mode_set_005b1994,
                     0x100,PTR_s_Invalid_list_view_mode___d_005b1990,param_1);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x8400000,_DAT_005b1a10,_DAT_005b1a10,param_1);
      }
    }
  }
  return;
}

