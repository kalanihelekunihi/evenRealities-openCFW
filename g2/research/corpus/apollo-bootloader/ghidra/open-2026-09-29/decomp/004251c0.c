
int am_hal_mspi_control(uint *param_1,int *param_2,uint *param_3,uint param_4)

{
  byte bVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  uint *puVar6;
  undefined1 uVar7;
  int iVar8;
  uint uVar9;
  uint uVar10;
  char cVar11;
  bool bVar12;
  uint *local_30;
  int *local_2c;
  uint *local_28;
  uint local_24;
  
  iVar4 = DAT_00426804;
  iVar3 = DAT_00425e98;
  iVar8 = 0;
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_00425e94)) {
    return 2;
  }
  if (0x28 < ((uint)param_2 & 0xff)) {
    return 6;
  }
  if ((char)param_1[2] == '\0') {
    return 7;
  }
  uVar9 = param_1[1];
  uVar5 = (uint)param_2 & 0xff;
  if (uVar5 == 0) {
    if (param_3 == (uint *)0x0) {
      return 6;
    }
    puVar6 = (uint *)(DAT_00425e98 + uVar9 * 0x1000 + 0x30);
    *puVar6 = (byte)*param_3 & 1 | *puVar6 & 0xfffffffe;
    return 0;
  }
  if (uVar5 == 2) {
    if (param_3 == (uint *)0x0) {
      return 6;
    }
    if ((7 < *param_3) && (*param_3 != 7)) {
      return 6;
    }
    puVar6 = (uint *)(DAT_00425e98 + uVar9 * 0x1000 + 0x30);
    *puVar6 = *puVar6 & 0xffffff0f | ((byte)*param_3 & 0xf) << 4;
    return 0;
  }
  if (uVar5 < 2) {
    if (param_3 == (uint *)0x0) {
      return 6;
    }
    if ((*param_3 & DAT_00425e9c) != 0) {
      return 6;
    }
    *(uint *)(DAT_00425e98 + uVar9 * 0x1000 + 0x2b4) = *param_3;
    return 0;
  }
  if (uVar5 == 4) {
    puVar6 = (uint *)(DAT_00425e98 + uVar9 * 0x1000 + 0x90);
    *puVar6 = *puVar6 & 0xffffefff;
    return 0;
  }
  if (uVar5 < 4) {
    if (param_3 == (uint *)0x0) {
      return 6;
    }
    if ((3 < *param_3) && (*param_3 != 7)) {
      return 6;
    }
    puVar6 = (uint *)(DAT_00425e98 + uVar9 * 0x1000 + 0x30);
    *puVar6 = *puVar6 & 0xffffff0f | (*param_3 + 8 & 0xf) << 4;
    return 0;
  }
  if (uVar5 == 6) {
    puVar6 = (uint *)(DAT_00425e98 + uVar9 * 0x1000 + 0x9c);
    *puVar6 = *puVar6 & 0x7fffffff;
    return 0;
  }
  if (uVar5 < 6) {
    puVar6 = (uint *)(DAT_00425e98 + uVar9 * 0x1000 + 0x90);
    *puVar6 = *puVar6 | 0x1000;
    return 0;
  }
  if (uVar5 == 8) {
    if (param_3 == (uint *)0x0) {
      return 6;
    }
    puVar6 = (uint *)(DAT_00425e98 + uVar9 * 0x1000 + 0x90);
    *puVar6 = *puVar6 & 0xfffffff3 | ((byte)*param_3 & 3) << 2;
    return 0;
  }
  if (uVar5 < 8) {
    puVar6 = (uint *)(DAT_00425e98 + uVar9 * 0x1000 + 0x9c);
    *puVar6 = *puVar6 | 0x80000000;
    return 0;
  }
  if (uVar5 == 10) {
    puVar6 = (uint *)(DAT_00425e98 + uVar9 * 0x1000 + 0x8c);
    *puVar6 = *puVar6 & 0x7fffffff;
    return 0;
  }
  if (uVar5 < 10) {
    if (param_3 == (uint *)0x0) {
      return 6;
    }
    puVar6 = (uint *)(DAT_00425e98 + uVar9 * 0x1000 + 0x8c);
    *puVar6 = *puVar6 & 0xfff9ffff | ((byte)*param_3 & 3) << 0x11;
    return 0;
  }
  if (uVar5 == 0xc) {
    puVar6 = (uint *)(DAT_00425e98 + uVar9 * 0x1000 + 0x88);
    *puVar6 = *puVar6 & 0xfffffffe;
    return 0;
  }
  if (uVar5 < 0xc) {
    puVar6 = (uint *)(DAT_00425e98 + uVar9 * 0x1000 + 0x8c);
    *puVar6 = *puVar6 | 0x80000000;
    return 0;
  }
  if (uVar5 == 0xe) {
    if (param_3 == (uint *)0x0) {
      return 6;
    }
    puVar6 = (uint *)(DAT_00425e98 + uVar9 * 0x1000 + 0x88);
    *puVar6 = *puVar6 & 0xfffffffb | ((byte)*param_3 & 1) << 2;
    puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x88);
    *puVar6 = *puVar6 & 0xfffffff7 | (*(byte *)((int)param_3 + 1) & 1) << 3;
    puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x88);
    *puVar6 = *puVar6 & 0xffffffef | (*(byte *)((int)param_3 + 2) & 1) << 4;
    puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x88);
    *puVar6 = *puVar6 & 0xfffffc1f | (*(byte *)((int)param_3 + 3) & 0x1f) << 5;
    puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x88);
    *puVar6 = *puVar6 & 0xffff83ff | ((byte)param_3[1] & 0x1f) << 10;
    puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0xa8);
    *puVar6 = ((byte)param_3[1] & 0x3f) >> 5 | *puVar6 & 0xfffffffe;
    puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x88);
    *puVar6 = *puVar6 & 0xfff07fff | (*(byte *)((int)param_3 + 5) & 0x1f) << 0xf;
    puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0xa8);
    *puVar6 = *puVar6 & 0xfffffeff | ((*(byte *)((int)param_3 + 5) & 0x3f) >> 5) << 8;
    puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x88);
    *puVar6 = *puVar6 & 0xffefffff | (*(byte *)((int)param_3 + 6) & 1) << 0x14;
    puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x88);
    *puVar6 = *puVar6 & 0xfc1fffff | (*(byte *)((int)param_3 + 7) & 0x1f) << 0x15;
    puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x88);
    *puVar6 = *puVar6 & 0x83ffffff | ((byte)param_3[2] & 0x1f) << 0x1a;
    puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x88);
    *puVar6 = *puVar6 & 0x7fffffff | (uint)*(byte *)((int)param_3 + 9) << 0x1f;
    return 0;
  }
  if (uVar5 < 0xe) {
    puVar6 = (uint *)(DAT_00425e98 + uVar9 * 0x1000 + 0x88);
    *puVar6 = *puVar6 | 1;
    return 0;
  }
  if (uVar5 == 0x10) {
    if (param_3 == (uint *)0x0) {
      return 6;
    }
    puVar6 = (uint *)(DAT_00425e98 + uVar9 * 0x1000 + 0x84);
    *puVar6 = *puVar6 & 0xfeffffff | ((byte)*param_3 & 1) << 0x18;
    puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x84);
    *puVar6 = *puVar6 & 0xff7fffff | (*(byte *)((int)param_3 + 1) & 1) << 0x17;
    puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x84);
    *puVar6 = *puVar6 & 0xffbfffff | (*(byte *)((int)param_3 + 2) & 1) << 0x16;
    puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x84);
    *puVar6 = *puVar6 & 0xffffc0ff | (*(byte *)((int)param_3 + 5) & 0x3f) << 8;
    puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x90);
    *puVar6 = *puVar6 & 0xfff03fff | (*(byte *)((int)param_3 + 5) & 0x3f) << 0xe;
    puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x88);
    *puVar6 = *puVar6 & 0xfffffc1f | (*(byte *)((int)param_3 + 3) & 0x1f) << 5;
    puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x88);
    *puVar6 = *puVar6 & 0xffff83ff | ((byte)param_3[1] & 0x1f) << 10;
    puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0xa8);
    *puVar6 = ((byte)param_3[1] & 0x3f) >> 5 | *puVar6 & 0xfffffffe;
    return 0;
  }
  if (uVar5 < 0x10) {
    if (param_3 == (uint *)0x0) {
      return 6;
    }
    puVar6 = (uint *)(DAT_00425e98 + uVar9 * 0x1000 + 0x8c);
    *puVar6 = *(byte *)((int)param_3 + 9) & 0xf | *puVar6 & 0xfffffff0;
    puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x8c);
    *puVar6 = *puVar6 & 0xffffffef | ((byte)param_3[2] & 1) << 4;
    puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x8c);
    *puVar6 = *puVar6 & 0xffffffdf | (*(byte *)((int)param_3 + 7) & 1) << 5;
    puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x8c);
    *puVar6 = *puVar6 & 0xffffff7f | (*(byte *)((int)param_3 + 6) & 1) << 7;
    puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x8c);
    *puVar6 = *puVar6 & 0xfffffeff | (*(byte *)((int)param_3 + 5) & 1) << 8;
    puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x8c);
    *puVar6 = *puVar6 & 0xfffff9ff | ((byte)param_3[1] & 3) << 9;
    puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x8c);
    *puVar6 = *puVar6 & 0xfffff7ff | (*(byte *)((int)param_3 + 3) & 1) << 0xb;
    puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x8c);
    *puVar6 = *puVar6 & 0xffffefff | (*(byte *)((int)param_3 + 2) & 1) << 0xc;
    puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x8c);
    *puVar6 = *puVar6 & 0xffffdfff | (*(byte *)((int)param_3 + 1) & 1) << 0xd;
    puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x8c);
    *puVar6 = *puVar6 & 0xfffe3fff | ((byte)*param_3 & 7) << 0xe;
    return 0;
  }
  if (uVar5 == 0x12) {
    if (uVar9 == 0) {
      if (0xfffffff < param_3[2] + 0xa0000000) {
        return 5;
      }
    }
    else if (uVar9 == 2) {
      if (0x3ffffff < param_3[2] + 0x7c000000) {
        return 5;
      }
    }
    else if (uVar9 < 2) {
      if (0x3ffffff < param_3[2] + 0x80000000) {
        return 5;
      }
    }
    else if ((uVar9 == 3) && (0x7ffffff < param_3[2] + 0x78000000)) {
      return 5;
    }
    uVar10 = param_3[2] & DAT_0042644c;
    uVar5 = param_3[3];
    bVar1 = *(byte *)((int)param_3 + 0xd);
    puVar6 = (uint *)(DAT_00425e98 + uVar9 * 0x1000 + 0x9c);
    *puVar6 = (*param_3 & 0x1fffffff) >> 0x10 | *puVar6 & 0xffffe000;
    puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x9c);
    *puVar6 = *puVar6 & 0xe000ffff | param_3[1] & 0x1fff0000;
    *(uint *)(iVar3 + uVar9 * 0x1000 + 0x80) = uVar10 | ((byte)uVar5 & 1) << 4 | bVar1 & 0xf;
    return 0;
  }
  if (uVar5 < 0x12) {
    if (param_3 == (uint *)0x0) {
      return 6;
    }
    *(byte *)param_3 =
         (byte)((uint)*(undefined4 *)(DAT_00425e98 + uVar9 * 0x1000 + 0x84) >> 0x18) & 1;
    *(byte *)((int)param_3 + 1) = (byte)(*(uint *)(iVar3 + uVar9 * 0x1000 + 0x84) >> 0x17) & 1;
    *(byte *)((int)param_3 + 2) = (byte)(*(uint *)(iVar3 + uVar9 * 0x1000 + 0x84) >> 0x16) & 1;
    *(byte *)((int)param_3 + 5) =
         (byte)((uint)*(undefined4 *)(iVar3 + uVar9 * 0x1000 + 0x84) >> 8) & 0x3f;
    *(byte *)((int)param_3 + 5) = (byte)(*(uint *)(iVar3 + uVar9 * 0x1000 + 0x90) >> 0xe) & 0x3f;
    *(byte *)((int)param_3 + 3) = (byte)(*(uint *)(iVar3 + uVar9 * 0x1000 + 0x88) >> 5) & 0x1f;
    *(byte *)(param_3 + 1) = (byte)(*(uint *)(iVar3 + uVar9 * 0x1000 + 0x88) >> 10) & 0x1f;
    *(byte *)(param_3 + 1) =
         ((byte)(*(int *)(iVar3 + uVar9 * 0x1000 + 0xa8) << 5) & 0x20) + (byte)param_3[1];
    return 0;
  }
  local_30 = param_1;
  local_2c = param_2;
  local_28 = param_3;
  local_24 = param_4;
  if (uVar5 == 0x14) {
    delay_us(param_1[0x233]);
    puVar6 = (uint *)(DAT_00425e98 + uVar9 * 0x1000 + 0x90);
    *puVar6 = *puVar6 & 0xfffffffe;
    return 0;
  }
  if (uVar5 < 0x14) {
    if (param_3 == (uint *)0x0) {
      return 6;
    }
    *(uint *)(DAT_00425e98 + uVar9 * 0x1000 + 0xa0) =
         (uint)*(byte *)((int)param_3 + 6) << 0x15 | (uint)*(byte *)((int)param_3 + 7) << 0xe |
         ((byte)param_3[2] & 1) << 0xd | (uint)*(byte *)((int)param_3 + 5) << 0xc | *param_3 & 0xfff
    ;
    return 0;
  }
  if (uVar5 == 0x16) {
    puVar6 = (uint *)(DAT_00425e98 + uVar9 * 0x1000);
    *puVar6 = *puVar6 | 0x100;
    puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x90);
    *puVar6 = *puVar6 | 0x10;
    *(undefined1 *)((int)param_1 + 0xd) = 1;
    return 0;
  }
  if (uVar5 < 0x16) {
    puVar6 = (uint *)(DAT_00425e98 + uVar9 * 0x1000 + 0x90);
    *puVar6 = *puVar6 | 1;
    return 0;
  }
  if (uVar5 == 0x18) {
    if (param_3 != (uint *)0x0) {
      *(byte *)((int)param_1 + 0xb) = (byte)*param_3;
      mspi_piomixed_configure(param_1);
      return 0;
    }
    return 6;
  }
  if (uVar5 < 0x18) {
    puVar6 = (uint *)(DAT_00425e98 + uVar9 * 0x1000);
    *puVar6 = *puVar6 & 0xfffffeff;
    puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x90);
    *puVar6 = *puVar6 & 0xffffffef;
    *(undefined1 *)((int)param_1 + 0xd) = 0;
    return 0;
  }
  if (uVar5 != 0x1a) {
    if (uVar5 < 0x1a) {
      if (param_3 == (uint *)0x0) {
        return 6;
      }
      if (((uVar9 == 1) || (uVar9 == 2)) && ((byte)*param_3 - 10 < 2)) {
        return 5;
      }
      *(byte *)((int)param_1 + 10) = (byte)*param_3;
      mspi_device_configure(param_1);
      return 0;
    }
    if (uVar5 == 0x1c) {
      if ((char)param_1[0x232] == '\0') {
        DataMemoryBarrier(0x1f);
      }
      *(undefined4 *)(DAT_00425e98 + uVar9 * 0x1000 + 0x2b4) = 0x80;
      return 0;
    }
    if (uVar5 < 0x1c) {
      iVar3 = mspi_cq_pause(param_1);
      return iVar3;
    }
    if (uVar5 == 0x1e) {
      uVar5 = 0;
      uVar10 = 0;
      if (param_3 == (uint *)0x0) {
        return 6;
      }
      if ((param_3[1] & 0xe0) != 0) {
        return 6;
      }
      if ((param_3[2] & DAT_00425e9c) != 0) {
        return 6;
      }
      if ((char)param_1[0x20b] != '\x01') {
        return 7;
      }
      if (param_1[0x20e] != 0) {
        param_1[0x20e] = 0;
        if ((char)param_1[0x232] == '\0') {
          DataMemoryBarrier(0x1f);
        }
        *(undefined4 *)(DAT_00425e98 + uVar9 * 0x1000 + 0x2b4) = 0x20;
      }
      if (((byte)*param_3 != 0) && (*(char *)((int)param_1 + 0x82d) == '\0')) {
        iVar3 = cmdq_alloc_block_42790a(param_1[0x20a],1,&local_2c,&local_28);
        if (iVar3 != 0) {
          return iVar3;
        }
        param_1[((uint)local_28 & 0xff) + 10] = DAT_00426800;
        param_1[((uint)local_28 & 0xff) + 0x10a] = (uint)param_1;
        *local_2c = DAT_00425e98 + uVar9 * 0x1000 + 0x2b4;
        local_2c[1] = 0;
        uVar5 = critical_save();
        iVar3 = cmdq_post_block_4279f0(param_1[0x20a],1);
        if (iVar3 != 0) {
          bVar12 = (bool)isCurrentModePrivileged();
          if (bVar12) {
            enableIRQinterrupts((uVar5 & 1) == 1);
          }
          cmdq_release_block_4279be(param_1[0x20a]);
          return iVar3;
        }
        uVar10 = param_1[8];
        param_1[8] = uVar10 + 1;
        bVar12 = (bool)isCurrentModePrivileged();
        if (bVar12) {
          enableIRQinterrupts((uVar5 & 1) == 1);
        }
        if ((uVar10 == 0) && (iVar3 = FUN_00423f8e(param_1), iVar3 != 0)) {
          return iVar3;
        }
        uVar5 = 0x40;
        uVar10 = 0x400000;
      }
      iVar4 = cmdq_alloc_block_42790a(param_1[0x20a],3,&local_2c,&local_28);
      piVar2 = local_2c;
      iVar3 = DAT_00425e98;
      if (iVar4 != 0) {
        return iVar4;
      }
      local_2c[2] = DAT_00425e98 + uVar9 * 0x1000 + 0x2b8;
      *local_2c = local_2c[2];
      local_2c[4] = iVar3 + uVar9 * 0x1000 + 0x2b4;
      iVar3 = stage_two_mode_flags(param_1,uVar5 | param_3[1]);
      piVar2[1] = iVar3;
      piVar2[3] = 0x4000;
      piVar2[5] = uVar10 | param_3[2];
      uVar5 = critical_save();
      if ((byte)*param_3 == 0) {
        iVar3 = cmdq_post_block_4279f0(param_1[0x20a],0);
      }
      else {
        iVar3 = cmdq_post_loop_block_427c12(param_1[0x20a],0);
      }
      if (iVar3 == 0) {
        uVar9 = param_1[8];
        param_1[8] = uVar9 + 1;
        if ((byte)*param_3 == 0) {
          uVar7 = 0;
        }
        else {
          uVar7 = 2;
        }
        *(undefined1 *)(param_1 + 0x20b) = uVar7;
        bVar12 = (bool)isCurrentModePrivileged();
        if (bVar12) {
          enableIRQinterrupts((uVar5 & 1) == 1);
        }
        if (uVar9 == 0) {
          iVar3 = FUN_00423f8e(param_1);
          return iVar3;
        }
        return 0;
      }
      bVar12 = (bool)isCurrentModePrivileged();
      if (bVar12) {
        enableIRQinterrupts((uVar5 & 1) == 1);
      }
      cmdq_release_block_4279be(param_1[0x20a]);
      return iVar3;
    }
    if (uVar5 < 0x1e) {
      if (param_3 == (uint *)0x0) {
        return 6;
      }
      if (param_1[6] == 0) {
        return 7;
      }
      bVar12 = (byte)*param_3 != 0;
      if (bVar12 == (bool)(char)param_1[0x20b]) {
        return 0;
      }
      if ((char)param_1[0x20b] == '\0') {
        if (param_1[8] != 0) {
          return 7;
        }
      }
      else if ((char)param_1[0x20b] == '\x02') {
        iVar8 = mspi_cq_pause(param_1);
      }
      if (iVar8 == 0) {
        cmdq_reset_427baa(param_1[0x20a]);
        param_1[7] = 0;
        param_1[0x20c] = 0;
        param_1[8] = 0;
        *(bool *)(param_1 + 0x20b) = bVar12;
        *(undefined1 *)((int)param_1 + 0x82d) = 1;
        param_1[0x217] = 0;
        return 0;
      }
      return iVar8;
    }
    if (uVar5 == 0x20) {
      *(undefined4 *)(DAT_00426804 + uVar9 * 0x1000 + 0x2b4) = 0x200000;
      param_1[0x20e] = 1;
      param_1[0x211] = 0;
      return 0;
    }
    if (uVar5 < 0x20) {
      if (param_3 == (uint *)0x0) {
        return 6;
      }
      if (param_1[0x215] != 0) {
        return 7;
      }
      param_1[0x214] = 0;
      param_1[0x210] = param_1[0x214];
      param_1[0x213] = param_1[0x214] + 1;
      param_1[0x215] = *param_3;
      param_1[0x212] = param_3[1] / 0x18;
      return 0;
    }
    if (uVar5 == 0x22) {
      if (param_3 == (uint *)0x0) {
        return 6;
      }
      if (param_1[0x20a] == 0) {
        return 7;
      }
      if ((param_1[8] == 0x100) ||
         (iVar4 = cmdq_alloc_block_42790a(param_1[0x20a],param_3[3] + 3,&local_30,&local_24),
         iVar3 = DAT_00426804, iVar4 != 0)) {
        return 5;
      }
      *local_30 = DAT_00426804 + uVar9 * 0x1000 + 0x2b8;
      uVar5 = stage_two_mode_flags(param_1,*param_3);
      local_30[1] = uVar5;
      puVar6 = local_30;
      for (uVar5 = 0; local_30 = puVar6 + 2, uVar5 < param_3[3]; uVar5 = uVar5 + 1) {
        *local_30 = *(uint *)(param_3[2] + uVar5 * 8);
        puVar6[3] = *(uint *)(param_3[2] + uVar5 * 8 + 4);
        puVar6 = local_30;
      }
      if (param_3[6] != 0) {
        *(uint **)param_3[6] = local_30;
      }
      *local_30 = iVar3 + uVar9 * 0x1000 + 0x2b8;
      puVar6[3] = 0x4000;
      local_30 = puVar6 + 4;
      *local_30 = iVar3 + uVar9 * 0x1000 + 0x2b4;
      puVar6[5] = param_3[1];
      uVar5 = param_3[4];
      if ((((uVar5 == 0) && (param_1[0x20e] == 0)) && ((char)param_1[0x20b] == '\0')) &&
         (param_1[0x216] >> 1 <= param_1[0x217])) {
        uVar5 = DAT_00426c00;
      }
      param_1[(local_24 & 0xff) + 10] = uVar5;
      param_1[(local_24 & 0xff) + 0x10a] = param_3[5];
      uVar9 = critical_save();
      iVar3 = cmdq_post_block_4279f0(param_1[0x20a],uVar5 != 0);
      if (iVar3 == 0) {
        uVar10 = param_1[8];
        param_1[8] = uVar10 + 1;
        param_1[0x20c] = param_1[0x20c] + 1;
        if (param_3[4] == 0) {
          if (uVar5 == 0) {
            param_1[0x217] = param_1[0x217] + 1;
          }
          else {
            param_1[0x217] = 0;
          }
        }
        else {
          *(undefined1 *)((int)param_1 + 0x82d) = 0;
          param_1[0x217] = 0;
        }
        bVar12 = (bool)isCurrentModePrivileged();
        if (bVar12) {
          enableIRQinterrupts((uVar9 & 1) == 1);
        }
        if (uVar10 == 0) {
          iVar3 = FUN_00423f8e(param_1);
          return iVar3;
        }
        return 0;
      }
      bVar12 = (bool)isCurrentModePrivileged();
      if (bVar12) {
        enableIRQinterrupts((uVar9 & 1) == 1);
      }
      cmdq_release_block_4279be(param_1[0x20a]);
      return iVar3;
    }
    if (uVar5 < 0x22) {
      if ((char)param_1[0x232] == '\0') {
        DataMemoryBarrier(0x1f);
      }
      *(undefined4 *)(DAT_00426804 + uVar9 * 0x1000 + 0x2b4) = 0x20;
      param_1[0x20e] = 0;
      if (param_1[0x211] == 0) {
        iVar3 = sched_hiprio(param_1,param_1[0x211]);
        if (iVar3 == 0) {
          param_1[0x211] = 0;
          return 0;
        }
        return iVar3;
      }
      return 0;
    }
    if (uVar5 == 0x24) {
      if (param_3 == (uint *)0x0) {
        return 6;
      }
      puVar6 = (uint *)(DAT_00426804 + uVar9 * 0x1000 + 0x84);
      *puVar6 = *puVar6 & 0x3ffffff | (uint)*(byte *)((int)param_3 + 9) << 0x1a;
      puVar6 = (uint *)(iVar4 + uVar9 * 0x1000 + 0x90);
      *puVar6 = *puVar6 & 0xfffff0ff | 0x500;
      puVar6 = (uint *)(iVar4 + uVar9 * 0x1000 + 0x90);
      *puVar6 = *puVar6 & 0xffffdfff | ((byte)param_3[3] & 1) << 0xd;
      return 0;
    }
    if (uVar5 < 0x24) {
      if (param_3 == (uint *)0x0) {
        return 6;
      }
      if (((byte)*param_3 < 4) && (*(byte *)((int)param_3 + 1) < 2)) {
        puVar6 = (uint *)(DAT_00426804 + uVar9 * 0x1000 + 0x84);
        *puVar6 = *puVar6 & 0xffffff7f | (*(byte *)((int)param_3 + 1) & 1) << 7;
        puVar6 = (uint *)(iVar4 + uVar9 * 0x1000 + 0x84);
        *puVar6 = *puVar6 & 0xffffff9f | ((byte)*param_3 & 3) << 5;
        return 0;
      }
      return 6;
    }
    if (uVar5 == 0x26) {
      puVar6 = (uint *)(DAT_00426804 + uVar9 * 0x1000 + 0x90);
      *puVar6 = *puVar6 | 0x40;
      return 0;
    }
    if (uVar5 < 0x26) {
      puVar6 = (uint *)(DAT_00426804 + uVar9 * 0x1000 + 0x90);
      *puVar6 = *puVar6 & 0xffffffbf;
      return 0;
    }
    if (uVar5 != 0x27) {
      return 6;
    }
    if (param_3 == (uint *)0x0) {
      return 6;
    }
    if ((byte)param_3[1] == 0) {
      puVar6 = (uint *)(DAT_00426804 + uVar9 * 0x1000 + 0xa4);
      *puVar6 = *puVar6 & 0xfffffffe;
      return 0;
    }
    puVar6 = (uint *)(DAT_00426804 + uVar9 * 0x1000 + 0xa4);
    *puVar6 = *puVar6 | 1;
    puVar6 = (uint *)(iVar4 + uVar9 * 0x1000 + 0xa4);
    *puVar6 = *puVar6 & 0xfffff9ff | ((byte)*param_3 & 3) << 9;
    puVar6 = (uint *)(iVar4 + uVar9 * 0x1000 + 0xa4);
    *puVar6 = *puVar6 & 0xfffffffd;
    puVar6 = (uint *)(iVar4 + uVar9 * 0x1000 + 0xa4);
    *puVar6 = *puVar6 & 0xfffffffb;
    puVar6 = (uint *)(iVar4 + uVar9 * 0x1000 + 0xa4);
    *puVar6 = *puVar6 & 0xfffffff7 | (*(byte *)((int)param_3 + 1) & 1) << 3;
    puVar6 = (uint *)(iVar4 + uVar9 * 0x1000 + 0xa4);
    *puVar6 = *puVar6 & 0xffffffef | (*(byte *)((int)param_3 + 2) & 1) << 4;
    puVar6 = (uint *)(iVar4 + uVar9 * 0x1000 + 0xa4);
    *puVar6 = *puVar6 & 0xffffffdf | (*(byte *)((int)param_3 + 3) & 1) << 5;
    puVar6 = (uint *)(iVar4 + uVar9 * 0x1000 + 0xa4);
    *puVar6 = *puVar6 & 0xffffffbf;
    puVar6 = (uint *)(iVar4 + uVar9 * 0x1000 + 0xa4);
    *puVar6 = *puVar6 & 0xffffff7f;
    puVar6 = (uint *)(iVar4 + uVar9 * 0x1000 + 0xa4);
    *puVar6 = *puVar6 & 0xfffffeff;
    return 0;
  }
  bVar1 = (byte)*param_3;
  if (((uVar9 == 1) || (uVar9 == 2)) && (bVar1 - 0x15 < 3)) {
    return 5;
  }
  mspi_clkgen_ctrl(param_1[1],0,0,0);
  if ((((bVar1 == 3) || (bVar1 == 5)) ||
      (((bVar1 == 7 || (((bVar1 == 9 || (bVar1 == 0xb)) || (bVar1 == 0xd)))) ||
       ((bVar1 == 0xf || (bVar1 == 0x11)))))) ||
     ((bVar1 == 0x13 || ((bVar1 == 0x15 || (bVar1 == 0x17)))))) {
    cVar11 = '\x05';
  }
  else {
    cVar11 = '\x04';
  }
  if (*(char *)((int)param_1 + 0x8c9) != cVar11) {
    iVar3 = clock_release(*(undefined1 *)((int)param_1 + 0x8c9),param_1[1] + 0x10 & 0xff);
    if (iVar3 != 0) {
      return iVar3;
    }
    iVar3 = clock_request(cVar11,param_1[1] + 0x10 & 0xff);
    if (iVar3 != 0) {
      return iVar3;
    }
  }
  *(char *)((int)param_1 + 0x8c9) = cVar11;
  if (bVar1 == 1) {
    uVar7 = 7;
    goto LAB_004259d6;
  }
  if (bVar1 == 0) {
    return 5;
  }
  if (bVar1 == 3) {
LAB_004259d4:
    uVar7 = 10;
  }
  else {
    if (2 < bVar1) {
      if (bVar1 == 5) goto LAB_004259d4;
      if (4 < bVar1) {
        if (bVar1 == 7) goto LAB_004259d4;
        if (6 < bVar1) {
          if (bVar1 == 9) goto LAB_004259d4;
          if (8 < bVar1) {
            if (bVar1 == 0xb) goto LAB_004259d4;
            if (10 < bVar1) {
              if (bVar1 == 0xd) goto LAB_004259d4;
              if (0xc < bVar1) {
                if (bVar1 == 0xf) goto LAB_004259d4;
                if (0xe < bVar1) {
                  if (bVar1 == 0x11) goto LAB_004259d4;
                  if (0x10 < bVar1) {
                    if (bVar1 == 0x13) goto LAB_004259d4;
                    if (0x12 < bVar1) {
                      if (bVar1 == 0x15) goto LAB_004259d4;
                      if (0x14 < bVar1) {
                        if (bVar1 == 0x17) goto LAB_004259d4;
                        if (0x16 < bVar1) {
                          return 5;
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
    uVar7 = 8;
  }
LAB_004259d6:
  mspi_clkgen_ctrl(param_1[1],1,1,uVar7);
  if ((bVar1 == 0x17) || (bVar1 == 0x16)) {
    puVar6 = (uint *)(DAT_00425e98 + uVar9 * 0x1000 + 0x8c);
    *puVar6 = *puVar6 | 0x40000000;
  }
  else {
    puVar6 = (uint *)(DAT_00425e98 + uVar9 * 0x1000 + 0x8c);
    *puVar6 = *puVar6 & 0xbfffffff;
  }
  uVar5 = (uint)bVar1;
  if (uVar5 - 1 < 3) {
    puVar6 = (uint *)(DAT_00425e98 + uVar9 * 0x1000 + 0x84);
    *puVar6 = *puVar6 & 0xffc0ffff | 0x200000;
  }
  else if (uVar5 - 4 < 2) {
    puVar6 = (uint *)(DAT_00425e98 + uVar9 * 0x1000 + 0x84);
    *puVar6 = *puVar6 & 0xffc0ffff | 0x180000;
  }
  else if (uVar5 - 6 < 2) {
    puVar6 = (uint *)(DAT_00425e98 + uVar9 * 0x1000 + 0x84);
    *puVar6 = *puVar6 & 0xffc0ffff | 0x100000;
  }
  else if (uVar5 - 8 < 2) {
    puVar6 = (uint *)(DAT_00425e98 + uVar9 * 0x1000 + 0x84);
    *puVar6 = *puVar6 & 0xffc0ffff | 0xc0000;
  }
  else if (uVar5 - 10 < 2) {
    puVar6 = (uint *)(DAT_00425e98 + uVar9 * 0x1000 + 0x84);
    *puVar6 = *puVar6 & 0xffc0ffff | 0x80000;
  }
  else if (uVar5 - 0xc < 2) {
    puVar6 = (uint *)(DAT_00425e98 + uVar9 * 0x1000 + 0x84);
    *puVar6 = *puVar6 & 0xffc0ffff | 0x60000;
  }
  else if (uVar5 - 0xe < 2) {
    puVar6 = (uint *)(DAT_00425e98 + uVar9 * 0x1000 + 0x84);
    *puVar6 = *puVar6 & 0xffc0ffff | 0x40000;
  }
  else if (uVar5 - 0x10 < 2) {
    puVar6 = (uint *)(DAT_00425e98 + uVar9 * 0x1000 + 0x84);
    *puVar6 = *puVar6 & 0xffc0ffff | 0x30000;
  }
  else if (uVar5 - 0x12 < 2) {
    puVar6 = (uint *)(DAT_00425e98 + uVar9 * 0x1000 + 0x84);
    *puVar6 = *puVar6 & 0xffc0ffff | 0x20000;
  }
  else {
    if (3 < uVar5 - 0x14) {
      return 5;
    }
    puVar6 = (uint *)(DAT_00425e98 + uVar9 * 0x1000 + 0x84);
    *puVar6 = *puVar6 & 0xffc0ffff | 0x10000;
  }
  iVar3 = DAT_00425e98;
  if (bVar1 - 1 < 0x13) {
    puVar6 = (uint *)(DAT_00425e98 + uVar9 * 0x1000 + 0x84);
    *puVar6 = *puVar6 & 0xfeffffff;
    puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x84);
    *puVar6 = *puVar6 & 0xff7fffff;
    puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x84);
    *puVar6 = *puVar6 & 0xffbfffff;
  }
  else {
    if (3 < bVar1 - 0x14) {
      return 5;
    }
    puVar6 = (uint *)(DAT_00425e98 + uVar9 * 0x1000 + 0x84);
    *puVar6 = *puVar6 | 0x1000000;
    puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x84);
    *puVar6 = *puVar6 & 0xff7fffff;
    puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x84);
    *puVar6 = *puVar6 & 0xffbfffff;
  }
  iVar3 = DAT_00425e98;
  if (param_1[6] != 0) {
    *(undefined4 *)(DAT_00425e98 + uVar9 * 0x1000 + 0x114) = 0x20;
    if (bVar1 - 1 < 0x11) {
      puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x118);
      *puVar6 = *puVar6 & 0xffffffe0 | 8;
      puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x20);
      *puVar6 = *puVar6 & 0xffffc0ff | 0x1e00;
      puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x118);
      *puVar6 = *puVar6 & 0xffffe0ff | 0x800;
    }
    else {
      if (5 < bVar1 - 0x12) {
        return 5;
      }
      puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x118);
      *puVar6 = *puVar6 & 0xffffffe0 | 0xc;
      puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x20);
      *puVar6 = *puVar6 & 0xffffc0ff | 0x1e00;
      puVar6 = (uint *)(iVar3 + uVar9 * 0x1000 + 0x118);
      *puVar6 = *puVar6 & 0xffffe0ff | 0x800;
    }
  }
  *(byte *)(param_1 + 3) = bVar1;
  mspi_get_xip_off_min_delay(param_1);
  return 0;
}

