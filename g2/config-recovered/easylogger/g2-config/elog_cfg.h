/*
 * This file is part of the EasyLogger Library.
 *
 * Copyright (c) 2015-2016, Armink, <armink.ztl@gmail.com>
 *
 * Permission is hereby granted, free of charge, to any person obtaining
 * a copy of this software and associated documentation files (the
 * 'Software'), to deal in the Software without restriction, including
 * without limitation the rights to use, copy, modify, merge, publish,
 * distribute, sublicense, and/or sell copies of the Software, and to
 * permit persons to whom the Software is furnished to do so, subject to
 * the following conditions:
 *
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
 * IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
 * CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
 * TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 *
 * Function: It is the configure head file for this library.
 * Created on: 2015-07-30
 *
 * openCFW: recovered G2 2.2.6.10 Apollo main configuration for EasyLogger
 * a596b264 (third-party/upstream/easylogger). Stock source path
 * D:\01_workspace\s200_ap510b_iar_git\third_party\EasyLogger-master\easylogger\src\elog.c
 * (ROM 0x6e3098). Evidence (Apollo main VAs; image file offset = VA - 0x437fe0):
 *   ELOG_LINE_BUF_SIZE 1024    elog_output 0x43d8e4 `rsbs r1,r4,#1024`, 0x43d8f0 cmp 1025;
 *                              log_buf RAM 0x2006bd30 (pool 0x43dc8c)
 *   ELOG_LINE_NUM_MAX_LEN 5    line_num[6] cleared at 0x43d62c (memset 6)
 *   ELOG_FILTER_TAG_MAX_LEN 30 elog_set_filter_tag 0x43d40a strncpy n=30; tag_lvl
 *                              memset 31 (0x43d462); tag pad buffer 16 (0x43d63a)
 *   ELOG_FILTER_KW_MAX_LEN 16  filter.keyword at elog+0x20, tag_lvl[] at elog+0x31
 *   ELOG_FILTER_TAG_LVL_MAX_NUM 5  loops `cmp #5` at 0x43d4aa and 0x43d526, 33-byte rows
 *   ELOG_NEWLINE_SIGN "\n"     literal 0x43da80 = 0x0a
 *   ELOG_COLOR_ENABLE          text_color_enabled at elog+0xf5, CSI_END "\033[0m" (0x43dcac);
 *                              colour table RAM 0x2000098c = default ELOG_COLOR_* values
 *                              ("35;22m","31;22m","33;22m","36;22m","32;22m","34;22m")
 *   ELOG_FMT_USING_FUNC/DIR/LINE  elog_start passes __FILE__, __FUNCTION__, __LINE__
 *   ELOG_ASSERT_ENABLE         asserting setters 0x43d260..0x43d406
 *   no ELOG_ASYNC_OUTPUT_ENABLE / ELOG_BUF_OUTPUT_ENABLE: elog_init 0x43d144 does not
 *                              call elog_async_init, elog_start 0x43d19a does not enable
 *                              async/buf output (the G2 async back end is product code,
 *                              elog_async_api.c, see g2/src/apollo-main/system/a-03-elog-async).
 * ELOG_OUTPUT_LVL VERBOSE is the upstream default (not discriminated by the image).
 */

#ifndef _ELOG_CFG_H_
#define _ELOG_CFG_H_
/*---------------------------------------------------------------------------*/
/* enable log output. */
#define ELOG_OUTPUT_ENABLE
/* setting static output log level. range: from ELOG_LVL_ASSERT to ELOG_LVL_VERBOSE */
#define ELOG_OUTPUT_LVL                          ELOG_LVL_VERBOSE
/* enable assert check */
#define ELOG_ASSERT_ENABLE
/* buffer size for every line's log */
#define ELOG_LINE_BUF_SIZE                       1024
/* output line number max length */
#define ELOG_LINE_NUM_MAX_LEN                    5
/* output filter's tag max length */
#define ELOG_FILTER_TAG_MAX_LEN                  30
/* output filter's keyword max length */
#define ELOG_FILTER_KW_MAX_LEN                   16
/* output filter's tag level max num */
#define ELOG_FILTER_TAG_LVL_MAX_NUM              5
/* output newline sign */
#define ELOG_NEWLINE_SIGN                        "\n"
/*---------------------------------------------------------------------------*/
/* enable log color */
#define ELOG_COLOR_ENABLE
/* change the some level logs to not default color if you want */
#define ELOG_COLOR_ASSERT                        (F_MAGENTA B_NULL S_NORMAL)
#define ELOG_COLOR_ERROR                         (F_RED B_NULL S_NORMAL)
#define ELOG_COLOR_WARN                          (F_YELLOW B_NULL S_NORMAL)
#define ELOG_COLOR_INFO                          (F_CYAN B_NULL S_NORMAL)
#define ELOG_COLOR_DEBUG                         (F_GREEN B_NULL S_NORMAL)
#define ELOG_COLOR_VERBOSE                       (F_BLUE B_NULL S_NORMAL)
/*---------------------------------------------------------------------------*/
/* enable log fmt */
/* comment it if you don't want to output them at all */
#define ELOG_FMT_USING_FUNC
#define ELOG_FMT_USING_DIR
#define ELOG_FMT_USING_LINE
/*---------------------------------------------------------------------------*/
/* asynchronous and buffered output modes: off in stock (see above) */

#endif /* _ELOG_CFG_H_ */
