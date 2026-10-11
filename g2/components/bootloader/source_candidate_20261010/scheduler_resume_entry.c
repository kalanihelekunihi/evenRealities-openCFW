/* SPDX-License-Identifier: MIT
 * Idle-loop resume call maps to the selected scheduler-resume body, as in
 * the accepted startup integration linker. Idle ignores its returned value.
 */
__attribute__((naked)) void resume_scheduler(void)
{
    __asm__ volatile("b.w opencfw_bl_scheduler_resume");
}
