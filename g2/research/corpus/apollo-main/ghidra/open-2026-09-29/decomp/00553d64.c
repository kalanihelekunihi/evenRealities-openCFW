
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00553d64(byte param_1,uint param_2)

{
  bool bVar1;
  char cVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  char *pcVar6;
  
  iVar3 = DAT_00553ff0;
  if ((*_DAT_00554048 == '\0') || (3 < param_1)) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(2,DAT_00554000,DAT_00553ffc,PTR_s_even_ai_animation_apply_sync_00554050,0x23c,
                   PTR_s_Animation_sync_failed__not_initi_0055404c,param_1);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8400000,PTR_s__even_ai_animation_Animation_syn_00554054,
                          PTR_s__even_ai_animation_Animation_syn_00554054,param_1);
    }
  }
  else if (*(int *)(DAT_00553ff0 + (uint)param_1 * 4) == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(2,DAT_00554000,DAT_00553ffc,PTR_s_even_ai_animation_apply_sync_00554050,0x241,
                   PTR_s_Animation_sync_failed__phase__d_a_00554058,param_1);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8400000,PTR_s__even_ai_animation_Animation_syn_0055405c,
                          PTR_s__even_ai_animation_Animation_syn_0055405c,param_1);
    }
  }
  else {
    cVar2 = FUN_0045a568();
    if (cVar2 == '\x02') {
      pcVar6 = (char *)(DAT_00553fec + (uint)param_1 * 0x10);
      uVar4 = FUN_00463fa4(*(undefined4 *)(iVar3 + (uint)param_1 * 4));
      cVar2 = *(char *)(*(int *)(iVar3 + (uint)param_1 * 4) + 0x19);
      bVar1 = false;
      if (cVar2 == '\0') {
        if ((param_2 < uVar4) &&
           (*(uint *)(*(int *)(iVar3 + (uint)param_1 * 4) + 8) >> 1 < uVar4 - param_2)) {
          pcVar6[8] = '\0';
          pcVar6[9] = '\0';
          pcVar6[10] = '\0';
          pcVar6[0xb] = '\0';
          *pcVar6 = '\0';
          bVar1 = true;
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            FUN_0043d574(4,DAT_00554000,DAT_00553ffc,PTR_s_even_ai_animation_apply_sync_00554050,
                         0x25d,PTR_s_Slave_LOOP__detected_master_loop_00554060,uVar4,param_2);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x10800000,PTR_s__even_ai_animation_Slave_LOOP__d_00554064,
                                PTR_s__even_ai_animation_Slave_LOOP__d_00554064,uVar4,param_2);
          }
        }
        else if (uVar4 < param_2) {
          bVar1 = true;
        }
      }
      else if (cVar2 == '\x01') {
        if (uVar4 < param_2) {
          bVar1 = true;
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            FUN_0043d574(4,DAT_00554000,DAT_00553ffc,PTR_s_even_ai_animation_apply_sync_00554050,
                         0x266,PTR_s_Slave_ONCE__catching_up_from__lu_00554068,uVar4,param_2);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x10800000,PTR_s__even_ai_animation_Slave_ONCE__c_0055406c,
                                PTR_s__even_ai_animation_Slave_ONCE__c_0055406c,uVar4,param_2);
          }
        }
      }
      else if ((cVar2 == '\x02') && (uVar4 != param_2)) {
        bVar1 = true;
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(4,DAT_00554000,DAT_00553ffc,PTR_s_even_ai_animation_apply_sync_00554050,0x26e
                       ,PTR_s_Slave_PING_PONG__syncing_from__l_00554070,uVar4,param_2);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x10800000,PTR_s__even_ai_animation_Slave_PING_PO_00554074,
                              PTR_s__even_ai_animation_Slave_PING_PO_00554074,uVar4,param_2);
        }
      }
      *(uint *)(pcVar6 + 8) = param_2 / 6;
      if (bVar1) {
        FUN_00463f5c(*(undefined4 *)(iVar3 + (uint)param_1 * 4),param_2);
      }
      if (*pcVar6 != '\0') {
        *pcVar6 = '\0';
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,DAT_00554000,DAT_00553ffc,PTR_s_even_ai_animation_apply_sync_00554050,0x27e
                       ,PTR_s_Slave_animation_resumed_from_syn_00554078,param_2);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10400000,PTR_s__even_ai_animation_Slave_animati_0055407c,
                              PTR_s__even_ai_animation_Slave_animati_0055407c,param_2);
        }
      }
    }
  }
  return;
}

