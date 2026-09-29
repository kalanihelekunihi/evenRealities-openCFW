
void threadBleWsfTask(void)

{
  threadBleWsfEnter();
  _thread_resource_init();
  threadBleWsfStart();
  threadBleWsfLoopInit();
  threadBleWsfReady();
  do {
    wsfOsDispatcher();
  } while( true );
}

