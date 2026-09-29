
void _bleSlaveProcMsg(undefined2 *param_1)

{
  undefined2 uVar1;
  undefined4 *puVar2;
  int *piVar3;
  char *pcVar4;
  undefined4 uVar5;
  undefined1 uVar6;
  char cVar7;
  undefined1 *puVar8;
  int iVar9;
  char cVar10;
  
  piVar3 = DAT_0046eb8c;
  cVar10 = '\0';
  cVar7 = *(char *)(param_1 + 1);
  if (cVar7 != '\x05') {
    if ((cVar7 == '\t') || (cVar7 == '\n')) {
      iVar9 = DmConnRole((char)*param_1);
      if (iVar9 == 1) {
        iVar9 = FUN_0043d0ce();
        if (iVar9 << 0x1e < 0) {
          FUN_0043d574(4,DAT_0046ed68,DAT_0046ed64,DAT_0046ed60,0x170,DAT_0046ed5c);
        }
        iVar9 = FUN_0043d0ce();
        if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_0046ed6c,DAT_0046ed6c);
        }
      }
      goto LAB_0046ece6;
    }
    if ((cVar7 != '\r') && (cVar7 != '\x0e')) {
      if (cVar7 == '\x15') {
        _bleAdvInit(param_1);
      }
      else if (cVar7 == '\x16') {
        iVar9 = DmConnRole((char)*param_1);
        piVar3 = DAT_0046ed88;
        if (iVar9 == 1) {
          *(undefined2 *)(*DAT_0046ed88 + 0x22) = param_1[7];
          iVar9 = FUN_0043d0ce();
          if (iVar9 << 0x1e < 0) {
            FUN_0043d574(3,DAT_0046ed68,DAT_0046ed64,DAT_0046ed60,0x193,DAT_0046ed8c,
                         *(undefined2 *)(*piVar3 + 0x22));
          }
          iVar9 = FUN_0043d0ce();
          if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
            compress_log_output(0xc400000,DAT_0046ed90,DAT_0046ed90,*(undefined2 *)(*piVar3 + 0x22))
            ;
          }
        }
      }
      else if (cVar7 == '!') {
        cVar10 = '\x03';
        iVar9 = FUN_0043d0ce();
        if (iVar9 << 0x1e < 0) {
          FUN_0043d574(3,DAT_0046ed68,DAT_0046ed64,DAT_0046ed60,0x183,DAT_0046ed78);
        }
        iVar9 = FUN_0043d0ce();
        if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_0046ecfc,DAT_0046ecfc);
        }
      }
      else if (cVar7 == '\"') {
        cVar10 = '\x04';
        iVar9 = FUN_0043d0ce();
        if (iVar9 << 0x1e < 0) {
          FUN_0043d574(3,DAT_0046ed68,DAT_0046ed64,DAT_0046ed60,0x188,DAT_0046ed00);
        }
        iVar9 = FUN_0043d0ce();
        if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_0046ed04,DAT_0046ed04);
        }
        pcVar4 = DAT_0046ed7c;
        if (*DAT_0046ed7c != '\0') {
          iVar9 = FUN_0043d0ce();
          if (iVar9 << 0x1e < 0) {
            FUN_0043d574(3,DAT_0046ed68,DAT_0046ed64,DAT_0046ed60,0x18b,DAT_0046ed80);
          }
          iVar9 = FUN_0043d0ce();
          if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
            compress_log_output(0xc000000,DAT_0046ed84,DAT_0046ed84);
          }
          *pcVar4 = '\0';
        }
      }
      else if (cVar7 == '\'') {
        iVar9 = DmConnRole((char)*param_1);
        if (iVar9 == 1) {
          *DAT_0046ee58 = '\0';
          *(undefined1 *)(*DAT_0046ed88 + 0x20) = 0;
          appSlaveConnOpen(param_1);
          _bleSlaveRequestMtuExchange(param_1);
          uVar5 = DAT_0046ee5c;
          fw_event_loop_remove_delayed(DAT_0046ee5c);
          iVar9 = productModeGet();
          if (iVar9 == 0) {
            fw_event_loop_push_delayed(uVar5,0,30000);
          }
          uVar5 = DAT_0046ee60;
          fw_event_loop_remove_delayed(DAT_0046ee60);
          fw_event_loop_push_delayed(uVar5,1,3000);
          iVar9 = FUN_0043d0ce();
          if (iVar9 << 0x1e < 0) {
            FUN_0043d574(3,DAT_0046ed68,DAT_0046ed64,DAT_0046ed60,0x1a2,DAT_0046ee64,*param_1);
          }
          iVar9 = FUN_0043d0ce();
          if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
            compress_log_output(0xc400000,DAT_0046ee68,DAT_0046ee68,*param_1);
          }
          uVar6 = FUN_0047a676(0);
          iVar9 = FUN_0043d0ce();
          if (iVar9 << 0x1e < 0) {
            FUN_0043d574(3,DAT_0046ed68,DAT_0046ed64,DAT_0046ed60,0x1ab,DAT_0046ee6c,uVar6);
          }
          iVar9 = FUN_0043d0ce();
          if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
            compress_log_output(0xc400000,DAT_0046eedc,DAT_0046eedc,uVar6);
          }
        }
      }
      else if (cVar7 == '(') {
        iVar9 = DmConnRole((char)*param_1);
        if (iVar9 == 1) {
          fw_event_loop_remove_delayed(DAT_0046ee5c);
          fw_event_loop_remove_delayed(DAT_0046ee60);
          *(undefined1 *)(*DAT_0046ed88 + 0x20) = 0;
          *DAT_0046ef5c = *DAT_0046ef5c & 0x80;
          iVar9 = FUN_0043d0ce(*param_1);
          if (iVar9 << 0x1e < 0) {
            FUN_0043d574(3,DAT_0046ed68,DAT_0046ed64,DAT_0046ed60,0x1c0,DAT_0046ef6c,
                         *(undefined1 *)(*DAT_0046eb8c + 0x54),*(undefined1 *)(param_1 + 4));
          }
          iVar9 = FUN_0043d0ce();
          if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
            compress_log_output(0xc800000,DAT_0046ef70,DAT_0046ef70,
                                *(undefined1 *)(*DAT_0046eb8c + 0x54),*(undefined1 *)(param_1 + 4));
          }
          fw_event_loop_remove_delayed(DAT_0046efd4);
          FUN_004b82e8(0);
          *(undefined1 *)(*DAT_0046eb8c + 0x54) = 0;
          tpl_reset_receive_contexts_004b9984();
          Thread_BleMsgtxQueueClear();
          Thread_BleMsgrxQueueClear();
          pcVar4 = DAT_0046ee58;
          puVar2 = DAT_0046eb18;
          if (*DAT_0046ee58 == '\0') {
            *DAT_0046ee58 = '\0';
            fw_event_loop_remove_delayed(0x46ee71);
            fw_event_loop_push_delayed(0x46ee71,0,1000);
            iVar9 = FUN_0043d0ce();
            if (iVar9 << 0x1e < 0) {
              FUN_0043d574(3,DAT_0046ed68,DAT_0046ed64,DAT_0046ed60,0x1d7,DAT_0046f090,*pcVar4);
            }
            iVar9 = FUN_0043d0ce();
            if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
              compress_log_output(0xc400000,DAT_0046f094,DAT_0046f094,*pcVar4);
            }
          }
          else {
            puVar8 = (undefined1 *)FUN_0047aec0(*(undefined4 *)*DAT_0046eb18);
            uVar6 = FUN_0047aec8(*(undefined4 *)*puVar2);
            FUN_0047b59c(uVar6,puVar8);
            *pcVar4 = '\0';
            iVar9 = FUN_0043d0ce();
            if (iVar9 << 0x1e < 0) {
              FUN_0043d574(3,DAT_0046ed68,DAT_0046ed64,DAT_0046ed60,0x1cd,DAT_0046eff4,uVar6,
                           puVar8[5],puVar8[4],puVar8[3],puVar8[2],puVar8[1],*puVar8);
            }
            iVar9 = FUN_0043d0ce();
            if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
              compress_log_output(0xdc00000,DAT_0046eff8,DAT_0046eff8,uVar6,puVar8[5],puVar8[4],
                                  puVar8[3],puVar8[2],puVar8[1],*puVar8);
            }
            fw_event_loop_remove_delayed(0x46ee71);
            fw_event_loop_push_delayed(0x46ee71,0,5000);
          }
        }
      }
      else if (cVar7 == '7') {
        iVar9 = FUN_0043d0ce();
        if (iVar9 << 0x1e < 0) {
          FUN_0043d574(4,DAT_0046ed68,DAT_0046ed64,DAT_0046ed60,0x1b0,DAT_0046eee0);
        }
        iVar9 = FUN_0043d0ce();
        if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_0046eee4,DAT_0046eee4);
        }
        piVar3 = DAT_0046ed88;
        *(undefined4 *)(*DAT_0046ed88 + 4) = *(undefined4 *)*DAT_0046eb18;
        iVar9 = FUN_0043d0ce();
        if (iVar9 << 0x1e < 0) {
          FUN_0043d574(3,DAT_0046ed68,DAT_0046ed64,DAT_0046ed60,0x1b3,DAT_0046eee8,
                       *(undefined4 *)(*piVar3 + 4));
        }
        iVar9 = FUN_0043d0ce();
        if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
          compress_log_output(0xc400000,DAT_0046ef58,DAT_0046ef58,*(undefined4 *)(*piVar3 + 4));
        }
      }
      else if (cVar7 == 'G') {
        cVar10 = '\x15';
      }
      else if (cVar7 == 'H') {
        cVar10 = '\x16';
        iVar9 = FUN_0043d0ce();
        if (iVar9 << 0x1e < 0) {
          FUN_0043d574(3,DAT_0046ed68,DAT_0046ed64,DAT_0046ed60,0x17e,DAT_0046ed70);
        }
        iVar9 = FUN_0043d0ce();
        if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_0046ed74);
        }
      }
      else if (cVar7 == -0x53) {
        iVar9 = FUN_0043d0ce();
        if (iVar9 << 0x1e < 0) {
          FUN_0043d574(4,DAT_0046ed68,DAT_0046ed64,DAT_0046ed60,0x218,DAT_0046f3ac);
        }
        iVar9 = FUN_0043d0ce();
        if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_0046f3b0,DAT_0046f3b0);
        }
        if ((*DAT_0046eb8c == 0) || (*(char *)(*DAT_0046eb8c + 0x54) == '\0')) {
          iVar9 = FUN_0043d0ce();
          if (iVar9 << 0x1e < 0) {
            FUN_0043d574(2,DAT_0046ed68,DAT_0046ed64,DAT_0046ed60,0x21a,DAT_0046f3b4);
          }
          iVar9 = FUN_0043d0ce();
          if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
            compress_log_output(0x8000000,DAT_0046f3b8,DAT_0046f3b8);
          }
        }
        else {
          FUN_004bb04a(*(undefined1 *)(*DAT_0046eb8c + 0x54));
        }
      }
      else if (cVar7 == -0x4b) {
        if ((*DAT_0046eb8c == 0) || (*(char *)(*DAT_0046eb8c + 0x54) == '\0')) {
          iVar9 = FUN_0043d0ce();
          if (iVar9 << 0x1e < 0) {
            FUN_0043d574(2,DAT_0046ed68,DAT_0046ed64,DAT_0046ed60,0x20a,DAT_0046f348);
          }
          iVar9 = FUN_0043d0ce();
          if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
            compress_log_output(0x8000000,DAT_0046f34c,DAT_0046f34c);
          }
        }
        else {
          uVar1 = param_1[4];
          iVar9 = FUN_0043d0ce();
          cVar7 = (char)uVar1;
          if (iVar9 << 0x1e < 0) {
            FUN_0043d574(4,DAT_0046ed68,DAT_0046ed64,DAT_0046ed60,0x20e,DAT_0046f3a4,cVar7);
          }
          iVar9 = FUN_0043d0ce();
          if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
            compress_log_output(0x10400000,DAT_0046f3a8,DAT_0046f3a8,cVar7);
          }
          if (cVar7 != '\0') {
            _bleSlaveSecReq(*(undefined1 *)(*piVar3 + 0x54));
            FUN_004b82e8(1);
          }
        }
      }
      else if (cVar7 == -0x4a) {
        uVar6 = FUN_004b46a8();
        cVar7 = FUN_004bac4e(0);
        *DAT_0046ee58 = '\0';
        iVar9 = FUN_0043d0ce();
        if (iVar9 << 0x1e < 0) {
          FUN_0043d574(3,DAT_0046ed68,DAT_0046ed64,DAT_0046ed60,0x1df,DAT_0046f0e0,uVar6,cVar7);
        }
        iVar9 = FUN_0043d0ce();
        if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
          compress_log_output(0xc800000,DAT_0046f0e4,DAT_0046f0e4,uVar6,cVar7);
        }
        *DAT_0046ed7c = '\0';
        if (cVar7 == '\0') {
          if ((*(char *)(DAT_0046f0e8 + 0x57) == '\0') || (2 < *(byte *)(DAT_0046f0e8 + 0x57))) {
            *(undefined1 *)(DAT_0046f0e8 + 0x57) = 0;
            iVar9 = FUN_0043d0ce();
            if (iVar9 << 0x1e < 0) {
              FUN_0043d574(3,DAT_0046ed68,DAT_0046ed64,DAT_0046ed60,0x1e9,DAT_0046f158);
            }
            iVar9 = FUN_0043d0ce();
            if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
              compress_log_output(0xc000000,DAT_0046f15c,DAT_0046f15c);
            }
          }
          FUN_004b467c(1);
          AppSetAdvType(0);
          AppAdvStart(1);
          iVar9 = FUN_0043d0ce();
          if (iVar9 << 0x1e < 0) {
            FUN_0043d574(3,DAT_0046ed68,DAT_0046ed64,DAT_0046ed60,0x1ee,DAT_0046f160);
          }
          iVar9 = FUN_0043d0ce();
          if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
            compress_log_output(0xc000000,DAT_0046f1c4,DAT_0046f1c4);
          }
        }
        else if (cVar7 == '\x05') {
          iVar9 = FUN_0043d0ce();
          if (iVar9 << 0x1e < 0) {
            FUN_0043d574(2,DAT_0046ed68,DAT_0046ed64,DAT_0046ed60,0x1f0,DAT_0046f1c8,5);
          }
          iVar9 = FUN_0043d0ce();
          if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
            compress_log_output(0x8400000,DAT_0046f1cc,DAT_0046f1cc,5);
          }
          fw_event_loop_remove_delayed(0x46ee71);
          fw_event_loop_push_delayed(0x46ee71,0,200);
        }
        else if ((cVar7 == '\x01') || (cVar7 == '\x03')) {
          iVar9 = FUN_0043d0ce();
          if (iVar9 << 0x1e < 0) {
            FUN_0043d574(3,DAT_0046ed68,DAT_0046ed64,DAT_0046ed60,500,DAT_0046f248,cVar7);
          }
          iVar9 = FUN_0043d0ce();
          if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
            compress_log_output(0xc400000,DAT_0046f24c,DAT_0046f24c,cVar7);
          }
        }
        else {
          iVar9 = FUN_0043d0ce();
          if (iVar9 << 0x1e < 0) {
            FUN_0043d574(2,DAT_0046ed68,DAT_0046ed64,DAT_0046ed60,0x1f7,DAT_0046f250,cVar7);
          }
          iVar9 = FUN_0043d0ce();
          if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
            compress_log_output(0x8400000,DAT_0046f254,DAT_0046f254,cVar7);
          }
          fw_event_loop_remove_delayed(0x46ee71);
          fw_event_loop_push_delayed(0x46ee71,0,200);
        }
      }
      else if (cVar7 == -0x49) {
        cVar7 = FUN_004b46a8();
        iVar9 = FUN_0043d0ce();
        if (iVar9 << 0x1e < 0) {
          FUN_0043d574(3,DAT_0046ed68,DAT_0046ed64,DAT_0046ed60,0x200,DAT_0046f2d0,cVar7);
        }
        iVar9 = FUN_0043d0ce();
        if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
          compress_log_output(0xc400000,DAT_0046f2d4,DAT_0046f2d4,cVar7);
        }
        if (cVar7 != '\0') {
          iVar9 = FUN_0043d0ce();
          if (iVar9 << 0x1e < 0) {
            FUN_0043d574(4,DAT_0046ed68,DAT_0046ed64,DAT_0046ed60,0x202,DAT_0046f2d8);
          }
          iVar9 = FUN_0043d0ce();
          if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
            compress_log_output(0x10000000,DAT_0046f328,DAT_0046f328);
          }
          AppAdvStop();
        }
      }
      else if (cVar7 == -0x48) {
        if ((*(int *)(param_1 + 2) == 0) || (param_1[4] != 3)) {
          iVar9 = FUN_0043d0ce();
          if (iVar9 << 0x1e < 0) {
            FUN_0043d574(1,DAT_0046ed68,DAT_0046ed64,DAT_0046ed60,0x22a,DAT_0046f3bc,
                         *(undefined4 *)(param_1 + 2),param_1[4]);
          }
          iVar9 = FUN_0043d0ce();
          if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
            compress_log_output(0x4800000,DAT_0046f3c0,DAT_0046f3c0,*(undefined4 *)(param_1 + 2),
                                param_1[4]);
          }
        }
        else {
          TPL_RxPacketTimeoutHandler(*(undefined4 *)(param_1 + 2));
        }
      }
      else if (cVar7 == -0x46) {
        if ((*DAT_0046f3c4 == 0) || (*(char *)(*DAT_0046f3c4 + 0x54) == '\0')) {
          iVar9 = FUN_0043d0ce();
          if (iVar9 << 0x1e < 0) {
            FUN_0043d574(2,DAT_0046ed68,DAT_0046ed64,DAT_0046ed60,0x231,DAT_0046f3c8);
          }
          iVar9 = FUN_0043d0ce();
          if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
            compress_log_output(0x8000000,DAT_0046f3cc,DAT_0046f3cc);
          }
        }
        else {
          uVar1 = param_1[4];
          iVar9 = FUN_0043d0ce();
          uVar6 = (undefined1)uVar1;
          if (iVar9 << 0x1e < 0) {
            FUN_0043d574(4,DAT_0046ed68,DAT_0046ed64,DAT_0046ed60,0x235,DAT_0046f3d0,uVar6);
          }
          iVar9 = FUN_0043d0ce();
          if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
            compress_log_output(0x10400000,DAT_0046f3d4,DAT_0046f3d4,uVar6);
          }
          FUN_004b82e8(1);
          PB_TxEncodeNotifySecAuthImpl(uVar6);
        }
      }
      else if (cVar7 == -0x45) {
        if ((*DAT_0046f3c4 == 0) || (*(char *)(*DAT_0046f3c4 + 0x54) == '\0')) {
          iVar9 = FUN_0043d0ce();
          if (iVar9 << 0x1e < 0) {
            FUN_0043d574(2,DAT_0046ed68,DAT_0046ed64,DAT_0046ed60,0x23d,DAT_0046f3d8);
          }
          iVar9 = FUN_0043d0ce();
          if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
            compress_log_output(0x8000000,DAT_0046f3dc,DAT_0046f3dc);
          }
        }
        else {
          uVar1 = param_1[4];
          iVar9 = FUN_0043d0ce();
          uVar6 = (undefined1)uVar1;
          if (iVar9 << 0x1e < 0) {
            FUN_0043d574(4,DAT_0046ed68,DAT_0046ed64,DAT_0046ed60,0x241,DAT_0046f3e0,uVar6);
          }
          iVar9 = FUN_0043d0ce();
          if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
            compress_log_output(0x10400000,DAT_0046f3e4,DAT_0046f3e4,uVar6);
          }
          PB_TxEncodeNotifyRingConnectInfoImpl(uVar6);
        }
      }
      goto LAB_0046ece6;
    }
  }
  iVar9 = DmConnRole((char)*param_1);
  if (iVar9 == 1) {
    dmSlaveAdvStopOnDisconnect(param_1);
  }
LAB_0046ece6:
  if (cVar10 != '\0') {
    FUN_004bd054(cVar10);
  }
  return;
}

