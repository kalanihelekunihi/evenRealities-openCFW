
int _rxSyncEventCallback(int param_1,undefined *param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar2 = param_1;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    iVar2 = 0x28;
    param_2 = PTR_s_SyncStatus____d_0048e850;
    param_3 = param_1;
    FUN_0043d574(4,PTR_s_svc_android_notify_0048e85c,PTR_s_D__01_workspace_s200_ap510b_iar__0048e858
                 ,PTR_s__rxSyncEventCallback_0048e854,0x28,PTR_s_SyncStatus____d_0048e850,param_1,
                 param_4);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_0048e4de;
  }
  compress_log_output(0x10400000,PTR_s__svc_android_notify_SyncStatus___0048e860,
                      PTR_s__svc_android_notify_SyncStatus___0048e860,param_1,iVar2,param_2,param_3)
  ;
LAB_0048e4de:
  if (param_1 != 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_svc_android_notify_0048e85c,
                   PTR_s_D__01_workspace_s200_ap510b_iar__0048e858,
                   PTR_s__rxSyncEventCallback_0048e854,0x2a,
                   PTR_s________________Dual_Glasses_Comm_0048e864,param_1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,PTR_s__svc_android_notify______________0048e868,
                          PTR_s__svc_android_notify______________0048e868,param_1);
    }
  }
  return param_1;
}

