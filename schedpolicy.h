#ifndef _SCHEDPOLICY_H_
#define _SCHEDPOLICY_H_

#include "queue.h"

void sched_block(int connfd, Queue queue, int max_size)
{
    // Queue already has cond and mutex to handle this
    queueInsert(queue, connfd);
}

void sched_dt(int connfd, Queue queue, int max_size)
{
    if (queueGetSize(queue) >= max_size)
    {
        Close(connfd);
        return;
    }
    else
    {
        queueInsert(queue, connfd);
    }
}

void sched_dh(int connfd, Queue queue, int max_size)
{
    if (queueGetSize(queue) >= max_size)
    {
        queueRemove(queue);
    }

    queueInsert(queue, connfd);
}

void sched_bf(int connfd, Queue queue, int max_size)
{
    if (queueGetSize(queue) >= max_size)
    {
        queueWaitEmpty(queue);
    }

    queueInsert(queue, connfd);
}

void sched_dynamic(int connfd, Queue queue, int max_size)
{
    if (queueGetSize(queue) >= queueGetCapacity(queue))
    {
        Close(connfd);
        if (max_size > queueGetCapacity(queue))
            queueIncrementCapacity(queue);
    }
    else
    {
        queueInsert(queue, connfd);
    }
}

void sched_random(int connfd, Queue queue, int max_size)
{
}

void *decidePolicy(const char *policy)
{

    if (strcmp(policy, "block") == 0)
    {
        return sched_block;
    }
    else if (strcmp(policy, "dt") == 0)
    {
        return sched_dt;
    }
    else if (strcmp(policy, "dh") == 0)
    {
        return sched_dh;
    }
    else if (strcmp(policy, "bf") == 0)
    {
        return sched_bf;
    }
    else if (strcmp(policy, "dynamic") == 0)
    {
        return sched_dynamic;
    }
    else if (strcmp(policy, "random") == 0)
    {
        return sched_random;
    }
    else /* default: */
    {
        return sched_block;
    }
}

#endif // _SCHEDPOLICY_H_