
uint cff_slot_load(int param_1,int *param_2,uint param_3,uint param_4)

{
  bool bVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 *puVar6;
  int iVar7;
  undefined4 uVar8;
  int iVar9;
  int iVar10;
  char cVar11;
  int iVar12;
  undefined4 local_61c;
  undefined4 local_618;
  undefined4 local_614;
  int *local_610;
  undefined4 local_60c;
  undefined4 local_608;
  undefined4 *local_604;
  uint local_600;
  undefined4 local_5fc;
  ushort local_5f8;
  short local_5f6;
  short local_5f4;
  ushort local_5f2;
  int local_5f0;
  int local_5ec;
  int local_5e8;
  int local_5e4;
  int local_5e0;
  undefined4 local_5dc;
  undefined4 local_5d8;
  undefined4 local_5d4;
  undefined4 local_5d0;
  int local_5cc;
  int local_5c8;
  int local_5c4;
  int local_5c0;
  undefined1 auStack_5bc [652];
  undefined1 auStack_330 [32];
  undefined4 local_310;
  undefined4 local_308;
  undefined4 local_304;
  undefined1 local_2ee;
  int local_2ec;
  code *local_2e0;
  undefined4 local_e8;
  undefined1 local_df;
  uint uStack_28;
  
  iVar7 = *(int *)(param_1 + 4);
  iVar9 = *(int *)(iVar7 + 0x2a4);
  local_5f0 = *(int *)(iVar7 + 0x22c);
  local_604 = *(undefined4 **)(local_5f0 + 0x28);
  bVar1 = false;
  uStack_28 = param_4;
  if ((*(int *)(iVar9 + 0x5e0) == 0xffff) || (*(int *)(iVar9 + 0x4a8) == 0)) {
    if (*(uint *)(iVar9 + 0x14) <= param_3) {
      return 6;
    }
  }
  else if ((param_3 != 0) &&
          (param_3 = cff_charset_cid_to_gindex(iVar9 + 0x49c,param_3), param_3 == 0)) {
    return 6;
  }
  if ((int)(param_4 << 0x15) < 0) {
    param_4 = param_4 | 3;
  }
  *(undefined4 *)(param_1 + 0xa4) = 0x10000;
  *(undefined4 *)(param_1 + 0xa8) = 0x10000;
  local_610 = param_2;
  if (param_2 != (int *)0x0) {
    *(int *)(param_1 + 0xa4) = param_2[4];
    *(int *)(param_1 + 0xa8) = param_2[5];
    iVar12 = *(int *)(*param_2 + 0x21c);
    if (((param_2[0xb] != -1) && (*(int *)(iVar12 + 0x60) != 0)) && (-1 < (int)(param_4 << 0x1c))) {
      local_618 = &local_600;
      local_61c = param_1 + 0x4c;
      iVar12 = (**(code **)(iVar12 + 0x48))
                         (iVar7,param_2[0xb],param_3,param_4,*(undefined4 *)(*param_2 + 0x68));
      if (iVar12 == 0) {
        *(undefined2 *)(param_1 + 0x6e) = 0;
        *(undefined2 *)(param_1 + 0x6c) = 0;
        *(uint *)(param_1 + 0x18) = (local_600 >> 0x10) << 6;
        *(uint *)(param_1 + 0x1c) = (local_600 & 0xffff) << 6;
        *(int *)(param_1 + 0x20) = (int)(short)local_5fc << 6;
        *(int *)(param_1 + 0x24) = (int)local_5fc._2_2_ << 6;
        *(uint *)(param_1 + 0x28) = (uint)local_5f8 << 6;
        *(int *)(param_1 + 0x2c) = (int)local_5f6 << 6;
        *(int *)(param_1 + 0x30) = (int)local_5f4 << 6;
        *(uint *)(param_1 + 0x34) = (uint)local_5f2 << 6;
        *(undefined4 *)(param_1 + 0x48) = DAT_005ad344;
        if ((int)(param_4 << 0x1b) < 0) {
          *(int *)(param_1 + 100) = (int)local_5f6;
          *(int *)(param_1 + 0x68) = (int)local_5f4;
        }
        else {
          *(int *)(param_1 + 100) = (int)(short)local_5fc;
          *(int *)(param_1 + 0x68) = (int)local_5fc._2_2_;
        }
        (**(code **)(*(int *)(iVar7 + 0x21c) + 0x70))
                  (iVar7,0,param_3,(int)&local_614 + 2,(int)&local_61c + 2);
        *(uint *)(param_1 + 0x38) = local_61c >> 0x10;
        if ((*(char *)(iVar7 + 0x124) == '\0') || (*(short *)(iVar7 + 0x14a) == 0)) {
          bVar1 = false;
        }
        else {
          bVar1 = true;
        }
        if (bVar1) {
          (**(code **)(*(int *)(iVar7 + 0x21c) + 0x70))
                    (iVar7,1,param_3,(int)&local_614 + 2,(int)&local_61c + 2);
          *(uint *)(param_1 + 0x3c) = local_61c >> 0x10;
        }
        else if (*(short *)(iVar7 + 0x174) == -1) {
          *(int *)(param_1 + 0x3c) = (int)*(short *)(iVar7 + 0xdc) - (int)*(short *)(iVar7 + 0xde);
        }
        else {
          *(int *)(param_1 + 0x3c) = (int)*(short *)(iVar7 + 0x1ba) - (int)*(short *)(iVar7 + 0x1bc)
          ;
        }
        return 0;
      }
    }
  }
  if ((int)(param_4 << 0x11) < 0) {
    uVar2 = 6;
  }
  else {
    if (*(int *)(iVar9 + 0x7e8) == 0) {
      FUN_00439c04(&local_5ec,iVar9 + 0x58c,0x10);
      local_600 = *(uint *)(iVar9 + 0x5a4);
      local_5fc = *(int *)(iVar9 + 0x5a8);
    }
    else {
      uVar2 = cff_fd_select_get(iVar9 + 0xbec,param_3);
      if (*(uint *)(iVar9 + 0x7e8) <= (uVar2 & 0xff)) {
        uVar2 = *(int *)(iVar9 + 0x7e8) - 1;
      }
      iVar12 = *(int *)(iVar9 + 0x5a0);
      iVar10 = *(int *)(*(int *)(iVar9 + (uVar2 & 0xff) * 4 + 0x7ec) + 0x44);
      FUN_00439c04(&local_5ec,*(int *)(iVar9 + (uVar2 & 0xff) * 4 + 0x7ec) + 0x30,0x10);
      iVar3 = *(int *)(iVar9 + (uVar2 & 0xff) * 4 + 0x7ec);
      local_600 = *(uint *)(iVar3 + 0x48);
      local_5fc = *(int *)(iVar3 + 0x4c);
      if (iVar12 != iVar10) {
        uVar4 = FT_MulDiv(*(undefined4 *)(param_1 + 0xa4),iVar12,iVar10);
        *(undefined4 *)(param_1 + 0xa4) = uVar4;
        uVar4 = FT_MulDiv(*(undefined4 *)(param_1 + 0xa8),iVar12,iVar10);
        *(undefined4 *)(param_1 + 0xa8) = uVar4;
        bVar1 = true;
      }
    }
    *(undefined2 *)(param_1 + 0x6e) = 0;
    *(undefined2 *)(param_1 + 0x6c) = 0;
    uVar2 = (param_4 & 3) >> 1 ^ 1;
    cVar11 = (char)uVar2;
    *(char *)(param_1 + 0xa0) = cVar11;
    *(byte *)(param_1 + 0xa1) = (byte)param_4 & 1 ^ 1;
    *(undefined4 *)(param_1 + 0x48) = DAT_005ad348;
    local_614 = DAT_005ad34c;
    local_618 = (uint *)DAT_005ad350;
    local_61c = (int)param_4 >> 0x10 & 0xf;
    (*(code *)*local_604)(auStack_330,iVar7,local_610,param_1,uVar2);
    if ((int)(param_4 << 0x17) < 0) {
      local_df = 1;
    }
    local_2ee = 0;
    uVar2 = cff_get_glyph_data(iVar7,param_3,&local_608,&local_60c);
    if ((uVar2 == 0) && (uVar2 = (*(code *)local_604[1])(auStack_330,local_610,param_3), uVar2 == 0)
       ) {
      (**(code **)(local_5f0 + 0x18))(auStack_5bc,auStack_330,0);
      uVar2 = (*(code *)local_604[2])(auStack_5bc,local_608,local_60c);
      if ((uVar2 & 0xff) == 0xa4) {
        cVar11 = '\0';
        bVar1 = true;
        *(undefined1 *)(param_1 + 0xa0) = 0;
        uVar2 = (*(code *)local_604[2])(auStack_5bc,local_608,local_60c);
      }
      cff_free_glyph_data(iVar7,&local_608,local_60c);
      if (uVar2 == 0) {
        if (*(int *)(*(int *)(iVar7 + 0x80) + 0x34) == 0) {
          if (*(int *)(iVar9 + 0x4d0) != 0) {
            *(int *)(param_1 + 0x88) =
                 *(int *)(iVar9 + 0x4d4) + *(int *)(*(int *)(iVar9 + 0x4d0) + param_3 * 4) + -1;
            *(undefined4 *)(param_1 + 0x8c) = local_60c;
          }
        }
        else {
          *(undefined4 *)(param_1 + 0x88) = 0;
          *(undefined4 *)(param_1 + 0x8c) = 0;
        }
      }
    }
    if (((uVar2 == 0) && ((*local_2e0)(auStack_330), *(int *)(*(int *)(iVar7 + 0x80) + 0x34) != 0))
       && (*(int *)(**(int **)(*(int *)(iVar7 + 0x80) + 0x34) + 8) != 0)) {
      local_5dc = local_310;
      local_5d8 = 0;
      local_5d4 = local_308;
      local_5d0 = local_304;
      uVar2 = (**(code **)(**(int **)(*(int *)(iVar7 + 0x80) + 0x34) + 8))
                        (*(undefined4 *)(*(int *)(*(int *)(iVar7 + 0x80) + 0x34) + 4),param_3,0,
                         &local_5dc);
      local_310 = local_5dc;
      local_308 = local_5d4;
      local_304 = local_5d0;
    }
    if (uVar2 == 0) {
      if ((int)(param_4 << 0x15) < 0) {
        iVar7 = *(int *)(param_1 + 0x9c);
        *(undefined4 *)(param_1 + 0x20) = local_310;
        *(undefined4 *)(param_1 + 0x28) = local_e8;
        FUN_00439c04(iVar7 + 0xc,&local_5ec,0x10);
        *(uint *)(iVar7 + 0x1c) = local_600;
        *(int *)(iVar7 + 0x20) = local_5fc;
        *(undefined1 *)(iVar7 + 8) = 1;
      }
      else {
        if (*(short *)(iVar7 + 0xfa) == 0) {
          *(undefined4 *)(param_1 + 0x28) = local_e8;
          *(undefined4 *)(param_1 + 0x38) = local_e8;
        }
        else {
          local_614 = local_614 & 0xffff0000;
          local_61c = local_61c & 0xffff0000;
          (**(code **)(*(int *)(iVar7 + 0x21c) + 0x70))(iVar7,0,param_3,&local_614,&local_61c);
          *(uint *)(param_1 + 0x28) = local_61c & 0xffff;
          *(int *)(param_1 + 0x20) = (int)(short)local_614;
          *(uint *)(param_1 + 0x38) = local_61c & 0xffff;
        }
        *(undefined1 *)(*(int *)(param_1 + 0x9c) + 8) = 0;
        if ((*(char *)(iVar7 + 0x124) == '\0') || (*(short *)(iVar7 + 0x14a) == 0)) {
          local_61c = (uint)local_61c._1_3_ << 8;
        }
        else {
          local_61c = CONCAT31(local_61c._1_3_,1);
        }
        if ((char)local_61c == '\0') {
          if (*(short *)(iVar7 + 0x174) == -1) {
            *(int *)(param_1 + 0x34) = (int)*(short *)(iVar7 + 0xdc) - (int)*(short *)(iVar7 + 0xde)
            ;
          }
          else {
            *(int *)(param_1 + 0x34) =
                 (int)*(short *)(iVar7 + 0x1ba) - (int)*(short *)(iVar7 + 0x1bc);
          }
        }
        else {
          local_618 = (uint *)0x0;
          (**(code **)(*(int *)(iVar7 + 0x21c) + 0x70))
                    (iVar7,1,param_3,(int)&local_618 + 2,&local_618);
          *(int *)(param_1 + 0x30) = (int)local_618._2_2_;
          *(uint *)(param_1 + 0x34) = (uint)local_618 & 0xffff;
        }
        *(undefined4 *)(param_1 + 0x3c) = *(undefined4 *)(param_1 + 0x34);
        *(undefined4 *)(param_1 + 0x48) = DAT_005ad348;
        *(undefined4 *)(param_1 + 0x7c) = 0;
        if ((local_610 != (int *)0x0) && (*(ushort *)((int)local_610 + 0xe) < 0x18)) {
          *(uint *)(param_1 + 0x7c) = *(uint *)(param_1 + 0x7c) | 0x100;
        }
        *(uint *)(param_1 + 0x7c) = *(uint *)(param_1 + 0x7c) | 4;
        if ((((local_5ec != 0x10000) || (local_5e0 != 0x10000)) || (local_5e8 != 0)) ||
           (local_5e4 != 0)) {
          FT_Outline_Transform(param_1 + 0x6c,&local_5ec);
          uVar4 = FT_MulFix(*(undefined4 *)(param_1 + 0x28),local_5ec);
          *(undefined4 *)(param_1 + 0x28) = uVar4;
          uVar4 = FT_MulFix(*(undefined4 *)(param_1 + 0x34),local_5e0);
          *(undefined4 *)(param_1 + 0x34) = uVar4;
        }
        if ((local_600 != 0) || (local_5fc != 0)) {
          FT_Outline_Translate(param_1 + 0x6c,local_600,local_5fc);
          *(uint *)(param_1 + 0x28) = local_600 + *(int *)(param_1 + 0x28);
          *(int *)(param_1 + 0x34) = local_5fc + *(int *)(param_1 + 0x34);
        }
        if ((-1 < (int)(param_4 << 0x1f)) || (bVar1)) {
          puVar6 = *(undefined4 **)(param_1 + 0x70);
          uVar4 = *(undefined4 *)(param_1 + 0xa4);
          uVar8 = *(undefined4 *)(param_1 + 0xa8);
          if ((cVar11 == '\0') || (local_2ec == 0)) {
            for (iVar7 = (int)*(short *)(param_1 + 0x6e); 0 < iVar7; iVar7 = iVar7 + -1) {
              uVar5 = FT_MulFix(*puVar6,uVar4);
              *puVar6 = uVar5;
              uVar5 = FT_MulFix(puVar6[1],uVar8);
              puVar6[1] = uVar5;
              puVar6 = puVar6 + 2;
            }
          }
          uVar4 = FT_MulFix(*(undefined4 *)(param_1 + 0x28),uVar4);
          *(undefined4 *)(param_1 + 0x28) = uVar4;
          uVar4 = FT_MulFix(*(undefined4 *)(param_1 + 0x34),uVar8);
          *(undefined4 *)(param_1 + 0x34) = uVar4;
        }
        FT_Outline_Get_CBox(param_1 + 0x6c,&local_5cc);
        *(int *)(param_1 + 0x18) = local_5c4 - local_5cc;
        *(int *)(param_1 + 0x1c) = local_5c0 - local_5c8;
        *(int *)(param_1 + 0x20) = local_5cc;
        *(int *)(param_1 + 0x24) = local_5c0;
        if ((char)local_61c == '\0') {
          if ((int)(param_4 << 0x1b) < 0) {
            ft_synthesize_vertical_metrics((int *)(param_1 + 0x18),*(undefined4 *)(param_1 + 0x34));
          }
        }
        else {
          *(int *)(param_1 + 0x2c) = *(int *)(param_1 + 0x20) - *(int *)(param_1 + 0x28) / 2;
        }
      }
    }
  }
  return uVar2;
}

