#include "segel.h"
#include "request.h"
#include "queue.h"
#include "schedpolicy.h"

// 
// server.c: A very, very simple web server
//
// To run:
//  ./server <portnum (above 2000)>
//
// Repeatedly handles HTTP requests sent to this port number.
// Most of the work is done within routines written in request.c
//

typedef struct server_args_t
{
    int port;
    int threads;
    int queue_size;
    void (*schedalg)(int connfd, Queue queue, int max_size, time_t arrival_time);
    int max_size;
} server_args;

Queue queue;

// HW3: Parse the new arguments too
void getargs(server_args *sa, int argc, char *argv[])
{
    if (argc < 4)
    {
        fprintf(stderr, "Usage: %s <port>\n", argv[0]);
        exit(1);
    }
    sa->port = atoi(argv[1]);
    sa->threads = atoi(argv[2]);
    sa->queue_size = atoi(argv[3]);
    sa->schedalg = decidePolicy(argv[4]);

    if (argc > 5)
        sa->max_size = atoi(argv[5]);
    else
        sa->max_size = sa->queue_size;
}
// "block", "dt", "dh", "bf", "dynamic", or "random"

void thread(int thread_num)
{
    pthread_detach(pthread_self());
    thread_statistics threadstats = malloc(sizeof(struct thread_statistics_t));
    threadstats->thread_num = thread_num;
    threadstats->requests = 0;
    threadstats->static_requests = 0;
    threadstats->dynamic_requests = 0;

    while (1)
    {
        time_t arrival_time;
        int connfd = queueRemove(queue, &arrival_time);
        // TODO change to getT
        threadstats->dispatchInterval = time(NULL) - arrival_time;
        requestHandle(connfd, threadstats);
        Close(connfd);
    }
}

int main(int argc, char *argv[])
{
    int listenfd, connfd, clientlen;
    server_args sa;

    struct sockaddr_in clientaddr;
    pthread_t tid;

    // setup fd queue
    queue = queueCreate(sa.queue_size);

    getargs(&sa, argc, argv);

    for (size_t i = 0; i < sa.threads; i++)
    {
        pthread_create(&tid, NULL, thread, i);
        pthread_detach(tid);
    }

    listenfd = Open_listenfd(sa.port);
    while (1) {
        clientlen = sizeof(clientaddr);
        connfd = Accept(listenfd, (SA *)&clientaddr, (socklen_t *)&clientlen);
        sa.schedalg(connfd, queue, sa.max_size, time(NULL));
    }

}


    


 
