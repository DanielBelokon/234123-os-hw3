#ifndef __REQUEST_H__
#define __REQUEST_H__

typedef struct thread_statistics_t
{
    int dispatchInterval;
    int responseInterval;

    int thread_num;

    int requests;
    int dynamic_requests;
    int static_requests;
} *thread_statistics;

void requestHandle(int fd, thread_statistics thread_stats);

#endif
