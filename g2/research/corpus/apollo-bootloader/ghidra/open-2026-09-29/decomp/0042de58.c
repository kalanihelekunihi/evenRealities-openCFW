
void dfu_service_task_42de58(void)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  uint *puVar4;
  undefined4 uVar5;
  int *piVar6;
  char cVar7;
  int iVar8;
  undefined4 uVar9;
  uint local_48 [10];
  
  FUN_0041560c(local_48,0x28,0);
  do {
    while( true ) {
      while( true ) {
        iVar8 = FUN_00416920(*(undefined4 *)(DAT_0042e158 + 0xc),local_48,0,0);
        uVar5 = DAT_0042e190;
        puVar4 = DAT_0042e12c;
        uVar3 = DAT_0042e118;
        uVar2 = DAT_0042e114;
        if (iVar8 != 0) {
          return;
        }
        if (local_48[0] == 1) break;
        if ((local_48[0] == DAT_0042e12c[5]) &&
           (DAT_0042e12c[5] = (uint)&DAT_00438000, uVar5 = DAT_0042e190, uVar3 = DAT_0042e118,
           uVar2 = DAT_0042e114, *(int *)puVar4[5] << 2 < 0)) {
          elog_output(4,DAT_0042e118,DAT_0042e114,DAT_0042e190,0x237,DAT_0042e1bc,
                      *(undefined4 *)puVar4[5]);
          elog_output(4,uVar3,uVar2,uVar5,0x238,DAT_0042e1c0,puVar4[5],
                      *(undefined4 *)(puVar4[5] + 4));
          runtime_enable_sequence_42ddf2();
          vector_handoff_42dc90(puVar4[5]);
        }
      }
      elog_output(4,DAT_0042e118,DAT_0042e114,DAT_0042e190,0x20b,DAT_0042e194);
      uVar9 = stream_mode_42d84c(1);
      piVar6 = DAT_0042e198;
      uVar1 = DAT_0042e108;
      iVar8 = FUN_004153a4(DAT_0042e108,uVar9);
      *piVar6 = iVar8;
      puVar4 = DAT_0042e12c;
      if (*piVar6 != 0) break;
      elog_output(1,uVar3,uVar2,uVar5,0x20e,DAT_0042e10c,uVar1);
      critical_dispatch_transaction_42de0e();
LAB_0042e00e:
      puVar4 = DAT_0042e12c;
      if ((undefined1 *)DAT_0042e12c[5] != &DAT_00438000) {
        elog_output(1,uVar3,uVar2,uVar5,0x229,DAT_0042e1b0,DAT_0042e12c[5],&DAT_00438000);
        puVar4[5] = (uint)&DAT_00438000;
      }
      if (*(int *)puVar4[5] << 2 < 0) {
        elog_output(4,uVar3,uVar2,uVar5,0x22e,DAT_0042e1b4,*(undefined4 *)puVar4[5]);
        elog_output(4,uVar3,uVar2,uVar5,0x22f,DAT_0042e1b8,puVar4[5],*(undefined4 *)(puVar4[5] + 4))
        ;
        runtime_enable_sequence_42ddf2();
        vector_handoff_42dc90(puVar4[5]);
      }
    }
    iVar8 = FUN_00415484(DAT_0042e12c,1,0x20,*piVar6);
    if (iVar8 == 0x20) {
      if (*piVar6 != 0) {
        FUN_00415446(*piVar6);
        *piVar6 = 0;
      }
      elog_output(4,uVar3,uVar2,uVar5,0x21a,DAT_0042e19c,*puVar4 & 0xffffff,*puVar4 & 0xffffff);
      elog_output(4,uVar3,uVar2,uVar5,0x21b,DAT_0042e1a0,(*puVar4 & 0x7ffffff) >> 0x1a);
      elog_output(4,uVar3,uVar2,uVar5,0x21c,DAT_0042e1a4,puVar4[1]);
      elog_output(4,uVar3,uVar2,uVar5,0x21d,DAT_0042e1a8,(char)puVar4[4],(char)puVar4[4]);
      elog_output(4,uVar3,uVar2,uVar5,0x21e,DAT_0042e1ac,puVar4[5]);
      if ((int)(*puVar4 << 5) < 0) {
        cVar7 = dfu_image_crc_check_42d890(piVar6,puVar4);
        if (cVar7 == '\0') {
          critical_dispatch_transaction_42de0e();
        }
        else {
          dfu_payload_program_42dae8(piVar6,puVar4);
        }
      }
      goto LAB_0042e00e;
    }
    if (*piVar6 != 0) {
      FUN_00415446(*piVar6);
      *piVar6 = 0;
    }
    elog_output(1,uVar3,uVar2,uVar5,0x214,DAT_0042e18c,uVar1,iVar8);
    critical_dispatch_transaction_42de0e();
  } while( true );
}

