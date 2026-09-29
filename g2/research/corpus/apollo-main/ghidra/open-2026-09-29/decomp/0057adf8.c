
void SVC_PcmAppProcessData(byte param_1,int param_2,int param_3,undefined4 param_4)

{
  byte *pbVar1;
  int iVar2;
  int iVar3;
  short local_f8;
  undefined2 local_f6;
  int local_f4;
  undefined4 local_f0;
  undefined4 local_ec;
  undefined1 auStack_e8 [204];
  byte local_1c;
  undefined4 uStack_18;
  
  if (((param_1 < 2) && (param_2 != 0)) && (param_3 != 0)) {
    uStack_18 = param_4;
    if ((*(int *)((uint)param_1 * 0xc + DAT_0057b3b4 + 8) == 0) ||
       (*(byte *)((uint)param_1 * 0xc + DAT_0057b3b4 + 4) != param_1)) {
      if (param_1 == 0) {
        FUN_0043c0e4(auStack_e8,0xcd,0);
        local_f4 = 0;
        local_f6 = 0;
        local_f8 = 0;
        local_ec = 0;
        local_f0 = 0;
        iVar2 = osKernelGetTickCount();
        service_algo_process(param_2,param_3,&local_f6,&local_f8);
        service_algo_front_buffer_get(&local_ec,&local_f0);
        SVC_Lc3EncodeMono(local_ec,local_f0,auStack_e8,&local_f4,DAT_0057b3e4);
        FUN_00439be4(auStack_e8 + local_f4,&local_f6,2);
        FUN_00439be4(auStack_e8 + local_f4 + 2,&local_f8,2);
        pbVar1 = DAT_0057b3e8;
        local_1c = *DAT_0057b3e8;
        *DAT_0057b3e8 = *DAT_0057b3e8 + 1;
        if ((int)(*pbVar1 - 1) % 0x28 == 0) {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            iVar3 = osKernelGetTickCount();
            FUN_0043d574(3,DAT_0057b388,DAT_0057b384,DAT_0057b3f0,0x112,DAT_0057b3ec,*pbVar1 - 1,
                         param_3,local_f4,local_f6,(int)local_f8,iVar3 - iVar2);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            iVar3 = osKernelGetTickCount();
            compress_log_output(0xd800000,DAT_0057b3f4,DAT_0057b3f4,*pbVar1 - 1,param_3,local_f4,
                                local_f6,(int)local_f8,iVar3 - iVar2);
          }
          FUN_0043dacc(DAT_0057b3f8,8,auStack_e8,8);
        }
        Thread_MsgStreamingNotifyByBle(auStack_e8,0xcd);
      }
    }
    else {
      (**(code **)((uint)param_1 * 0xc + DAT_0057b3b4 + 8))(param_1,param_2,param_3);
    }
  }
  return;
}

