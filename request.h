#ifndef __REQUEST_H__
#define __REQUEST_H__

#include "segel.h"

typedef struct thread_statistics_t
{
    struct timeval arrival_time;
    struct timeval dispatch_interval;

    int handler_thread_id;

    int request_count;
    int dynamic_requests_count;
    int static_requests_count;
} *thread_statistics;

void requestHandle(int fd, thread_statistics thread_stats);

#endif
