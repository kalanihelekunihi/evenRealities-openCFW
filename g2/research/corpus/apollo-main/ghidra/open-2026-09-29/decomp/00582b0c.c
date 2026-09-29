
undefined4 FUN_00582b0c(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  undefined1 *puVar2;
  undefined1 uVar3;
  byte bVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  undefined4 uVar10;
  uint uVar11;
  int *piVar12;
  undefined4 uVar13;
  undefined4 uVar14;
  undefined4 *puVar15;
  byte *pbVar16;
  undefined1 uVar17;
  byte *pbVar18;
  ushort uVar19;
  uint uVar20;
  int local_38;
  int local_34;
  int local_30;
  undefined4 local_2c;
  undefined4 uStack_28;
  
  local_38 = 0;
  local_34 = 0;
  local_30 = 0;
  local_2c = 0;
  uStack_28 = param_4;
  iVar5 = FUN_005848fc(param_3,1,&local_38);
  iVar6 = FUN_005848fc(param_3,2,&local_34);
  iVar7 = FUN_005848fc(param_3,3,&local_30);
  iVar8 = FUN_005848fc(param_3,4,&local_2c);
  if ((iVar5 == 0) || (local_38 < 1)) {
    FUN_004733ee(DAT_005836c4);
  }
  else if ((local_38 == 4) &&
          (iVar9 = FUN_0044b610(iVar5,DAT_005836c8,4), puVar2 = DAT_005836d0, iVar9 == 0)) {
    if (iVar6 == 0) {
      FUN_004733ee(DAT_005836cc);
    }
    else {
      FUN_0043c0e4(DAT_005836d0,0x850,0);
      *puVar2 = 1;
      pbVar18 = DAT_005836d4;
      *DAT_005836d4 = *DAT_005836d4 + 1;
      puVar2[1] = *pbVar18;
      *(undefined2 *)(puVar2 + 2) = 3;
      iVar5 = thunk_FUN_0048d86c(iVar6);
      if (iVar5 == 0) {
        uVar3 = 1;
      }
      else {
        uVar3 = 2;
      }
      puVar2[4] = uVar3;
      FUN_00582960(puVar2);
    }
  }
  else if ((local_38 == 7) && (iVar9 = FUN_0044b610(iVar5,DAT_005836d8,7), iVar9 == 0)) {
    if (((iVar6 == 0) || (iVar7 == 0)) || (iVar8 == 0)) {
      FUN_004733ee(DAT_005836dc);
    }
    else {
      if (((local_34 == 2) && (iVar5 = FUN_0044b610(iVar6,&DAT_00582ea4,2), iVar5 == 0)) ||
         ((local_34 == 9 && (iVar5 = FUN_0044b610(iVar6,DAT_005836e0,9), iVar5 == 0)))) {
        uVar3 = 0;
      }
      else if ((local_34 == 3) && (iVar5 = FUN_0044b610(iVar6,&DAT_00582fec,3), iVar5 == 0)) {
        uVar3 = 1;
      }
      else {
        if ((local_34 != 4) || (iVar5 = FUN_0044b610(iVar6,DAT_005836e8,4), iVar5 != 0)) {
          FUN_004733ee(DAT_005836ec,local_34,iVar6);
          return 0;
        }
        uVar3 = 2;
      }
      if (((local_30 == 3) && (iVar5 = FUN_0044b610(iVar7,&DAT_00582f70,3), iVar5 == 0)) ||
         ((local_30 == 6 && (iVar5 = FUN_0044b610(iVar7,DAT_005836e4,6), iVar5 == 0)))) {
        uVar17 = 0;
      }
      else {
        if (((local_30 != 3) || (iVar5 = FUN_0044b610(iVar7,&DAT_00583040,3), iVar5 != 0)) &&
           ((local_30 != 7 || (iVar5 = FUN_0044b610(iVar7,DAT_005836f0,7), iVar5 != 0)))) {
          FUN_004733ee(DAT_005836f4,local_30,iVar7);
          return 0;
        }
        uVar17 = 1;
      }
      puVar2 = DAT_005836d0;
      FUN_0043c0e4(DAT_005836d0,0x850,0);
      *puVar2 = 5;
      pbVar18 = DAT_005836d4;
      *DAT_005836d4 = *DAT_005836d4 + 1;
      puVar2[1] = *pbVar18;
      *(undefined2 *)(puVar2 + 2) = 7;
      puVar2[4] = uVar3;
      puVar2[0x208] = uVar17;
      uVar10 = td_counter_b_get();
      *(undefined4 *)(puVar2 + 0x214) = uVar10;
      FUN_005829e0(puVar2 + 6,0x200,iVar8,local_2c);
      FUN_00582960(puVar2);
    }
  }
  else if ((local_38 == 9) &&
          (iVar9 = FUN_0044b610(iVar5,DAT_005836f8,9), puVar2 = DAT_005836d0, iVar9 == 0)) {
    FUN_0043c0e4(DAT_005836d0,0x850,0);
    *puVar2 = 3;
    pbVar18 = DAT_005836d4;
    *DAT_005836d4 = *DAT_005836d4 + 1;
    puVar2[1] = *pbVar18;
    *(undefined2 *)(puVar2 + 2) = 5;
    puVar2[0x206] = 1;
    puVar2[0x207] = 1;
    FUN_005829e0(puVar2 + 4,0x200,iVar6,local_34);
    FUN_00582960(puVar2);
  }
  else if ((local_38 == 10) &&
          (iVar9 = FUN_0044b610(iVar5,DAT_005836fc,10), puVar2 = DAT_005836d0, iVar9 == 0)) {
    FUN_0043c0e4(DAT_005836d0,0x850,0);
    *puVar2 = 3;
    pbVar18 = DAT_005836d4;
    *DAT_005836d4 = *DAT_005836d4 + 1;
    puVar2[1] = *pbVar18;
    *(undefined2 *)(puVar2 + 2) = 5;
    puVar2[0x206] = 1;
    puVar2[0x207] = 0;
    FUN_005829e0(puVar2 + 4,0x200,iVar6,local_34);
    FUN_00582960(puVar2);
  }
  else if ((local_38 == 3) &&
          (iVar9 = FUN_0044b610(iVar5,&DAT_00583044,3), puVar2 = DAT_005836d0, iVar9 == 0)) {
    FUN_0043c0e4(DAT_005836d0,0x850,0);
    *puVar2 = 3;
    pbVar18 = DAT_005836d4;
    *DAT_005836d4 = *DAT_005836d4 + 1;
    puVar2[1] = *pbVar18;
    *(undefined2 *)(puVar2 + 2) = 5;
    puVar2[0x206] = 0;
    puVar2[0x207] = 0;
    FUN_005829e0(puVar2 + 4,0x200,iVar6,local_34);
    FUN_00582960(puVar2);
  }
  else if ((local_38 == 6) && (iVar9 = FUN_0044b610(iVar5,DAT_00583700,6), iVar9 == 0)) {
    if (iVar6 == 0) {
      FUN_004733ee(DAT_00583704);
    }
    else {
      uVar11 = thunk_FUN_0048d86c(iVar6);
      puVar2 = DAT_005836d0;
      if (uVar11 < 5) {
        FUN_0043c0e4(DAT_005836d0,0x850,0);
        *puVar2 = 4;
        pbVar18 = DAT_005836d4;
        *DAT_005836d4 = *DAT_005836d4 + 1;
        puVar2[1] = *pbVar18;
        *(undefined2 *)(puVar2 + 2) = 6;
        puVar2[4] = (char)uVar11;
        uVar10 = td_counter_b_get();
        *(undefined4 *)(puVar2 + 8) = uVar10;
        FUN_00582960(puVar2);
      }
      else {
        FUN_004733ee(DAT_00583708);
      }
    }
  }
  else if ((local_38 == 5) &&
          (iVar9 = FUN_0044b610(iVar5,DAT_0058370c,5), puVar2 = DAT_005836d0, iVar9 == 0)) {
    FUN_0043c0e4(DAT_005836d0,0x850,0);
    *puVar2 = 4;
    pbVar18 = DAT_005836d4;
    *DAT_005836d4 = *DAT_005836d4 + 1;
    puVar2[1] = *pbVar18;
    *(undefined2 *)(puVar2 + 2) = 6;
    puVar2[4] = 4;
    uVar10 = td_counter_b_get();
    *(undefined4 *)(puVar2 + 8) = uVar10;
    FUN_00582960(puVar2);
  }
  else if ((local_38 == 4) && (iVar9 = FUN_0044b610(iVar5,DAT_00583710,4), iVar9 == 0)) {
    if (iVar6 == 0) {
      FUN_004733ee(DAT_00583714);
    }
    else {
      uVar11 = thunk_FUN_0048d86c(iVar6);
      puVar2 = DAT_005836d0;
      if (uVar11 < 3) {
        FUN_0043c0e4(DAT_005836d0,0x850,0);
        *puVar2 = 2;
        pbVar18 = DAT_005836d4;
        *DAT_005836d4 = *DAT_005836d4 + 1;
        puVar2[1] = *pbVar18;
        *(undefined2 *)(puVar2 + 2) = 4;
        puVar2[4] = (char)uVar11;
        puVar2[5] = 0;
        FUN_00582960(puVar2);
      }
      else {
        FUN_004733ee(DAT_00583718);
      }
    }
  }
  else if ((local_38 == 3) && (iVar9 = FUN_0044b610(iVar5,&DAT_00583294,3), iVar9 == 0)) {
    if (iVar6 == 0) {
      FUN_004733ee(DAT_0058371c);
    }
    else {
      uVar11 = thunk_FUN_0048d86c(iVar6);
      if ((uVar11 == 0) || (uVar11 == 1)) {
        CB_BLE_STATUS_Notify(0,uVar11 & 0xff);
        FUN_004733ee(DAT_00583724,uVar11);
      }
      else {
        FUN_004733ee(DAT_00583720);
      }
    }
  }
  else if ((local_38 == 5) &&
          (iVar9 = FUN_0044b610(iVar5,DAT_00583728,5), puVar2 = DAT_005836d0, iVar9 == 0)) {
    if (iVar6 == 0) {
      FUN_004733ee(DAT_0058372c);
    }
    else if (iVar7 == 0) {
      FUN_004733ee(DAT_00583730);
    }
    else {
      FUN_0043c0e4(DAT_005836d0,0x850,0);
      *puVar2 = 6;
      pbVar18 = DAT_005836d4;
      *DAT_005836d4 = *DAT_005836d4 + 1;
      puVar2[1] = *pbVar18;
      *(undefined2 *)(puVar2 + 2) = 8;
      *pbVar18 = *pbVar18 + 1;
      *(uint *)(puVar2 + 4) = (uint)*pbVar18;
      uVar10 = td_counter_b_get();
      *(undefined4 *)(puVar2 + 0x84c) = uVar10;
      iVar5 = thunk_FUN_0048d86c(iVar7);
      if (iVar5 < 1) {
        FUN_004733ee(DAT_00583734);
      }
      else {
        if (8 < iVar5) {
          iVar5 = 8;
        }
        FUN_005829e0(puVar2 + 8,0x400,iVar6,local_34);
        *(short *)(puVar2 + 0x40a) = (short)iVar5;
        for (iVar6 = 0; iVar6 < iVar5; iVar6 = iVar6 + 1) {
          *(int *)(puVar2 + iVar6 * 0x88 + 0x40c) = iVar6 + 1;
          uVar11 = FUN_0044b728(puVar2 + iVar6 * 0x88 + 0x412,0x80,DAT_00583738,iVar6 + 1);
          if ((int)uVar11 < 0) {
            uVar11 = 0;
          }
          if (0x7f < uVar11) {
            uVar11 = 0x7f;
          }
          *(short *)(puVar2 + iVar6 * 0x88 + 0x410) = (short)uVar11;
        }
        FUN_00582960(puVar2);
      }
    }
  }
  else if ((local_38 == 10) &&
          (iVar9 = FUN_0044b610(iVar5,DAT_0058373c,10), puVar2 = DAT_005836d0, iVar9 == 0)) {
    FUN_0043c0e4(DAT_005836d0,0x850,0);
    *puVar2 = 6;
    pbVar18 = DAT_005836d4;
    *DAT_005836d4 = *DAT_005836d4 + 1;
    puVar2[1] = *pbVar18;
    *(undefined2 *)(puVar2 + 2) = 8;
    *pbVar18 = *pbVar18 + 1;
    *(uint *)(puVar2 + 4) = (uint)*pbVar18;
    uVar10 = td_counter_b_get();
    *(undefined4 *)(puVar2 + 0x84c) = uVar10;
    puVar15 = DAT_00583740;
    uVar10 = FUN_0044a43c(*DAT_00583740);
    FUN_005829e0(puVar2 + 8,0x400,*puVar15,uVar10);
    *(undefined2 *)(puVar2 + 0x40a) = 8;
    for (iVar5 = 0; iVar5 < 8; iVar5 = iVar5 + 1) {
      *(int *)(puVar2 + iVar5 * 0x88 + 0x40c) = iVar5 + 1;
      uVar11 = FUN_0044b728(puVar2 + iVar5 * 0x88 + 0x412,0x80,DAT_00583738,iVar5 + 1);
      if ((int)uVar11 < 0) {
        uVar11 = 0;
      }
      if (0x7f < uVar11) {
        uVar11 = 0x7f;
      }
      *(short *)(puVar2 + iVar5 * 0x88 + 0x410) = (short)uVar11;
    }
    FUN_00582960(puVar2);
  }
  else if ((local_38 == 0xb) && (iVar9 = FUN_0044b610(iVar5,DAT_00583744,0xb), iVar9 == 0)) {
    if (iVar6 == 0) {
      FUN_004733ee(DAT_00583748);
    }
    else {
      uVar10 = thunk_FUN_0048d86c(iVar6);
      if (iVar7 == 0) {
        piVar12 = (int *)td_session_struct_ptr();
        if ((piVar12 == (int *)0x0) || (*piVar12 == 0)) {
          FUN_004733ee(DAT_0058374c);
          return 0;
        }
        iVar5 = *piVar12;
      }
      else {
        iVar5 = thunk_FUN_0048d86c(iVar7);
      }
      puVar2 = DAT_005836d0;
      FUN_0043c0e4(DAT_005836d0,0x850,0);
      *puVar2 = 0xa3;
      pbVar18 = DAT_005836d4;
      *DAT_005836d4 = *DAT_005836d4 + 1;
      puVar2[1] = *pbVar18;
      *(undefined2 *)(puVar2 + 2) = 0xb;
      *(int *)(puVar2 + 4) = iVar5;
      *(undefined4 *)(puVar2 + 8) = uVar10;
      FUN_004733ee(DAT_00583750,iVar5,uVar10);
      FUN_00582960(puVar2);
    }
  }
  else if ((local_38 == 3) && (iVar9 = FUN_0044b610(iVar5,&DAT_00583530,3), iVar9 == 0)) {
    if (iVar6 == 0) {
      FUN_004733ee(DAT_00583754);
    }
    else {
      uVar11 = thunk_FUN_0048d86c(iVar6);
      puVar2 = DAT_005836d0;
      if (uVar11 < 3) {
        FUN_0043c0e4(DAT_005836d0,0x850,0);
        *puVar2 = 7;
        pbVar18 = DAT_005836d4;
        *DAT_005836d4 = *DAT_005836d4 + 1;
        puVar2[1] = *pbVar18;
        *(undefined2 *)(puVar2 + 2) = 0xf;
        puVar2[4] = (char)uVar11;
        FUN_00582960(puVar2);
      }
      else {
        FUN_004733ee(DAT_00583758);
      }
    }
  }
  else if ((local_38 == 0xc) && (iVar9 = FUN_0044b610(iVar5,DAT_0058375c,0xc), iVar9 == 0)) {
    if (((iVar6 == 0) || (iVar7 == 0)) || (iVar8 == 0)) {
      FUN_004733ee(DAT_00583760);
    }
    else {
      uVar10 = thunk_FUN_0048d86c(iVar6);
      uVar13 = thunk_FUN_0048d86c(iVar7);
      uVar14 = thunk_FUN_0048d86c(iVar8);
      puVar2 = DAT_005836d0;
      FUN_0043c0e4(DAT_005836d0,0x850,0);
      *puVar2 = 8;
      pbVar18 = DAT_005836d4;
      *DAT_005836d4 = *DAT_005836d4 + 1;
      puVar2[1] = *pbVar18;
      *(undefined2 *)(puVar2 + 2) = 0x10;
      FUN_00582a48(puVar2 + 4,uVar10,uVar13,uVar14);
      FUN_00582960(puVar2);
    }
  }
  else if ((local_38 == 0xd) && (iVar7 = FUN_0044b610(iVar5,DAT_00583764,0xd), iVar7 == 0)) {
    if (iVar6 == 0) {
      FUN_004733ee(DAT_00583768);
    }
    else {
      uVar11 = thunk_FUN_0048d86c(iVar6);
      puVar2 = DAT_005836d0;
      if (uVar11 < 2) {
        FUN_0043c0e4(DAT_005836d0,0x850,0);
        *puVar2 = 9;
        pbVar18 = DAT_005836d4;
        *DAT_005836d4 = *DAT_005836d4 + 1;
        puVar2[1] = *pbVar18;
        *(undefined2 *)(puVar2 + 2) = 0x11;
        puVar2[4] = (char)uVar11;
        FUN_00582960(puVar2);
      }
      else {
        FUN_004733ee(DAT_0058376c);
      }
    }
  }
  else if ((local_38 == 10) && (iVar7 = FUN_0044b610(iVar5,DAT_00583770,10), iVar7 == 0)) {
    if (iVar6 == 0) {
      FUN_004733ee(DAT_00583774);
    }
    else {
      uVar11 = thunk_FUN_0048d86c(iVar6);
      puVar2 = DAT_005836d0;
      if (uVar11 < 2) {
        FUN_0043c0e4(DAT_005836d0,0x850,0);
        *puVar2 = 0xb;
        pbVar18 = DAT_005836d4;
        *DAT_005836d4 = *DAT_005836d4 + 1;
        puVar2[1] = *pbVar18;
        *(undefined2 *)(puVar2 + 2) = 0x17;
        puVar2[4] = (char)uVar11;
        FUN_00582960(puVar2);
      }
      else {
        FUN_004733ee(DAT_00583778);
      }
    }
  }
  else if ((local_38 == 0xf) && (iVar7 = FUN_0044b610(iVar5,DAT_0058377c,0xf), iVar7 == 0)) {
    if (iVar6 == 0) {
      FUN_004733ee(DAT_00583780);
    }
    else {
      uVar10 = thunk_FUN_0048d86c(iVar6);
      puVar2 = DAT_005836d0;
      FUN_0043c0e4(DAT_005836d0,0x850,0);
      *puVar2 = 10;
      pbVar18 = DAT_005836d4;
      *DAT_005836d4 = *DAT_005836d4 + 1;
      puVar2[1] = *pbVar18;
      *(undefined2 *)(puVar2 + 2) = 0x15;
      *(undefined4 *)(puVar2 + 4) = uVar10;
      FUN_00582960(puVar2);
    }
  }
  else if ((local_38 == 5) && (iVar6 = FUN_0044b610(iVar5,DAT_00583784,5), iVar6 == 0)) {
    iVar5 = td_state_ptr_alias1();
    iVar6 = td_state_ptr();
    iVar7 = td_ring_ptr();
    puVar15 = (undefined4 *)td_session_struct_ptr();
    iVar8 = td_active_session();
    uVar11 = (uint)*(byte *)(iVar5 + 0xa1d8);
    bVar4 = td_record_status_read();
    iVar5 = UX_GetSystemBLEStatus();
    FUN_004733ee(DAT_00583788);
    FUN_004733ee(DAT_0058378c,*(undefined2 *)(iVar6 + 0x800),*(undefined2 *)(iVar6 + 0x802),
                 *(undefined1 *)(iVar6 + 0x804),*(undefined1 *)(iVar6 + 0x805),iVar6);
    uVar13 = FUN_00582942(uVar11 & 0xff);
    uVar10 = DAT_00583794;
    if (iVar5 != 0) {
      uVar10 = DAT_00583790;
    }
    FUN_004733ee(DAT_00583798,uVar10,iVar5 != 0,uVar13,uVar11 & 0xff,iVar6);
    uVar11 = FUN_005828f8(bVar4);
    pbVar18 = (byte *)(uint)bVar4;
    uVar20 = (uint)(bVar4 == 3);
    FUN_004733ee(DAT_0058379c,*(undefined4 *)(iVar7 + 0x8504),*(undefined2 *)(iVar7 + 0x8500),
                 bVar4 == 1,uVar20,uVar11,pbVar18);
    if (*(short *)(iVar7 + 0x8500) != 0) {
      for (uVar19 = 0; uVar19 < *(ushort *)(iVar7 + 0x8500); uVar19 = uVar19 + 1) {
        pbVar16 = (byte *)td_session_record_at(uVar19);
        if (pbVar16 != (byte *)0x0) {
          uVar10 = FUN_00582924(*pbVar16);
          pbVar18 = pbVar16 + 2;
          uVar11 = (uint)*(ushort *)(pbVar16 + 0x204);
          uVar20 = (uint)*pbVar16;
          FUN_004733ee(DAT_005837a0,uVar19,*(undefined4 *)(pbVar16 + 0x210),uVar10,uVar20,uVar11,
                       pbVar18);
        }
      }
    }
    FUN_004733ee(DAT_005837a4,*puVar15,*(undefined2 *)(puVar15 + 1),
                 *(undefined2 *)((int)puVar15 + 0x406),uVar20,uVar11,pbVar18);
    if (iVar8 == 0) {
      uVar10 = 0;
    }
    else {
      uVar10 = *(undefined4 *)(iVar8 + 8);
    }
    uVar13 = td_counter_b_get();
    uVar14 = td_counter_a_get();
    iVar5 = td_flag_b_get();
    iVar6 = td_flag_get();
    FUN_004733ee(DAT_005837a8,iVar6 != 0,iVar5 != 0,uVar14,uVar13,uVar10);
    if (iVar8 != 0) {
      for (uVar11 = 0; uVar11 < *(uint *)(iVar8 + 8); uVar11 = uVar11 + 1) {
        iVar5 = uVar11 * 0x90 + iVar8;
        uVar19 = *(ushort *)(iVar5 + 0xa0);
        if (0x80 < uVar19) {
          uVar19 = 0x80;
        }
        cVar1 = *(char *)(uVar11 * 0x90 + iVar8 + 0x128);
        uVar10 = FUN_005828f8(*(undefined1 *)(iVar5 + 0x122));
        FUN_004733ee(DAT_005837ac,uVar11,*(undefined4 *)(iVar5 + 0x9c),*(undefined2 *)(iVar5 + 0xa0)
                     ,uVar19,iVar5 + 0xa2,uVar10,*(undefined1 *)(iVar5 + 0x122),cVar1 != '\0',
                     *(undefined4 *)(iVar8 + uVar11 * 0x90 + 0x124));
      }
    }
  }
  else {
    FUN_004733ee(DAT_005837b0,local_38,iVar5);
    FUN_004733ee(DAT_005837b4);
  }
  return 0;
}

