#ifndef R1_NATIVE_APPLICATION_LAUNCH_H
#define R1_NATIVE_APPLICATION_LAUNCH_H
#include <stdint.h>
struct r1_application_lifecycle {
    void (*volatile start)(void);
    void (*volatile stop)(void);
    void *volatile thread;
};
extern struct r1_application_lifecycle r1_application_lifecycle;
void r1_application_launch(void);
void r1_application_manager_stop(void);
void r1_application_startup_thread(void *argument);
#endif
