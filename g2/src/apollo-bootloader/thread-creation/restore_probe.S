/* Test-only architectural readback, not stock firmware reconstruction. */
.syntax unified
.thumb
.text
.global opencfw_test_read_psplim
.type opencfw_test_read_psplim,%function
.thumb_func
opencfw_test_read_psplim:
    mrs r0,psplim
    bx lr
.global opencfw_test_set_stack_limits
.type opencfw_test_set_stack_limits,%function
.thumb_func
opencfw_test_set_stack_limits:
    msr psplim,r0
    msr psp,r1
    bx lr
