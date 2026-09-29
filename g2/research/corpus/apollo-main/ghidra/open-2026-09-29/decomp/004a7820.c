
void kvdbOnboardingConfigUpdateAndPersist(undefined1 param_1)

{
  int iVar1;
  
  iVar1 = SVC_SetKvdbOnboardingConfig(param_1);
  if (iVar1 == 0) {
    SVC_KvdbBlobWriteOnboardingConfig();
  }
  return;
}

