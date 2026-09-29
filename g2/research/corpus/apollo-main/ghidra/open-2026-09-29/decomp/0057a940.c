
undefined4 SVC_Lc3EncodeMono(int param_1,uint param_2,int param_3,int *param_4,undefined1 *param_5)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  int *piVar7;
  
  if ((((param_1 == 0) || (param_3 == 0)) || (param_4 == (int *)0x0)) ||
     (param_5 == (undefined1 *)0x0)) {
    piVar7 = param_4;
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0057b388,DAT_0057b384,DAT_0057b380,0x7c,DAT_0057b37c,param_1,param_3,
                   param_4,param_5,piVar7);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x5000000,DAT_0057b38c,DAT_0057b38c,param_1,param_3,param_4,param_5);
    }
    uVar2 = 0xffffffff;
  }
  else {
    iVar1 = FUN_00590e64(*(undefined4 *)(param_5 + 4),*(undefined4 *)(param_5 + 8));
    iVar3 = FUN_00590f78(*(undefined4 *)(param_5 + 4),*(undefined4 *)(param_5 + 0x14));
    if ((iVar1 < 1) || (iVar3 < 0x14)) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(1,DAT_0057b388,DAT_0057b384,DAT_0057b380,0x84,DAT_0057b390,iVar1,iVar3);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x4800000,DAT_0057b394,DAT_0057b394,iVar1,iVar3);
      }
      uVar2 = 0xffffffff;
    }
    else {
      iVar4 = service_audio_pcm_sample_bytes(*param_5);
      if (iVar4 == 0) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(1,DAT_0057b388,DAT_0057b384,DAT_0057b380,0x8b,DAT_0057b398,*param_5);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_0057b39c,DAT_0057b39c,*param_5);
        }
        uVar2 = 0xffffffff;
      }
      else {
        if (*(int *)(param_5 + 0x18) == 0) {
          uVar2 = FUN_00591374(*(undefined4 *)(param_5 + 4),*(undefined4 *)(param_5 + 8),0,
                               param_5 + 0x1c);
          *(undefined4 *)(param_5 + 0x18) = uVar2;
        }
        uVar6 = iVar4 * *(int *)(param_5 + 0xc) * iVar1;
        if (param_2 == uVar6 * (param_2 / uVar6)) {
          param_2 = param_2 / uVar6;
          *param_4 = 0;
          for (iVar1 = 0; iVar1 < (int)param_2; iVar1 = iVar1 + 1) {
            if (*(int *)(param_5 + 0xc) == 1) {
              uVar2 = 1;
              iVar5 = param_1;
            }
            else {
              iVar5 = param_1 + iVar4 * *(int *)(param_5 + 0x10);
              uVar2 = *(undefined4 *)(param_5 + 0xc);
            }
            iVar5 = FUN_0059138a(*(undefined4 *)(param_5 + 0x18),*param_5,iVar5,uVar2,iVar3,param_3)
            ;
            if (iVar5 != 0) {
              iVar3 = FUN_0043d0ce();
              if (iVar3 << 0x1e < 0) {
                FUN_0043d574(1,DAT_0057b388,DAT_0057b384,DAT_0057b380,0xb0,DAT_0057b3a0,iVar1,iVar5)
                ;
              }
              iVar3 = FUN_0043d0ce();
              if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
                compress_log_output(0x4800000,DAT_0057b3a4,DAT_0057b3a4,iVar1,iVar5);
              }
              return 0xffffffff;
            }
            param_1 = param_1 + uVar6;
            param_3 = param_3 + iVar3;
            *param_4 = iVar3 + *param_4;
          }
          uVar2 = 0;
        }
        else {
          uVar2 = 0xffffffff;
        }
      }
    }
  }
  return uVar2;
}

