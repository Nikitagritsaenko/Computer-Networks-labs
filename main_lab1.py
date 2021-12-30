import time
import numpy as np
from multiprocessing.pool import ThreadPool
import matplotlib.pyplot as plt

from lab1.gbn import gbn_sender, gbn_receiver
from lab1.srp import srp_sender, srp_receiver
from lab1.message_utils import MsgQueue, Protocol


def loss_probability_research():
    window_size = 3
    timeout = 0.2
    max_number = 100
    loss_probability_arr = np.linspace(0, 0.9, 10)

    print("p    | GBN             |SRP")
    print("     | t     |k        |t    |  k")

    gbn_time = []
    srp_time = []
    gbn_k = []
    srp_k = []

    for p in loss_probability_arr:

        table_row = f"{p:.1f}\t"

        for protocol in Protocol:
            send_queue = MsgQueue(p)
            receive_queue = MsgQueue(p)
            pool_sender = ThreadPool(processes=1)
            pool_receiver = ThreadPool(processes=1)

            if protocol == Protocol.GBN:
                async_result_sender = pool_sender.apply_async(gbn_sender, (
                    window_size, max_number, timeout, send_queue, receive_queue))
                async_result_receiver = pool_receiver.apply_async(gbn_receiver,
                                                                  (window_size, send_queue, receive_queue))
            elif protocol == Protocol.SRP:
                async_result_sender = pool_sender.apply_async(srp_sender, (
                    window_size, max_number, timeout, send_queue, receive_queue))
                async_result_receiver = pool_receiver.apply_async(srp_receiver, (send_queue, receive_queue))
            else:
                raise Exception("Protocol is not supported")

            timer_start = time.time()

            posted_msgs = async_result_sender.get()
            # print("sender")
            received_msgs = async_result_receiver.get()
            # print("receiver")
            timer_end = time.time()

            k = len(received_msgs) / len(posted_msgs)
            elapsed = timer_end - timer_start

            table_row += f" | {elapsed:2.2f}  | {k:.2f}   "
            if protocol == Protocol.GBN:
                gbn_time.append(elapsed)
                gbn_k.append(k)
            else:
                srp_time.append(elapsed)
                srp_k.append(k)

        print(table_row)

    fig, ax = plt.subplots()
    ax.plot(loss_probability_arr, gbn_k, label="Go-Back-N")
    ax.plot(loss_probability_arr, srp_k, label="Selective repeat")
    ax.set_xlabel('loss probability')
    ax.set_ylabel('efficiency')
    ax.legend()
    plt.show()

    fig, ax = plt.subplots()
    ax.plot(loss_probability_arr, gbn_time, label="Go-Back-N")
    ax.plot(loss_probability_arr, srp_time, label="Selective repeat")
    ax.set_xlabel('loss probability')
    ax.set_ylabel('time (sec)')
    ax.legend()
    plt.show()


def window_size_research():
    window_sizes = range(2, 15)
    timeout = 0.2
    max_number = 100

    print("w    | GBN             |SRP")
    print("     | t     |k        |t    |  k")

    gbn_time = []
    srp_time = []
    gbn_k = []
    srp_k = []

    p = 0.3

    for w in window_sizes:

        table_row = f"{w}\t"

        for protocol in Protocol:
            send_queue = MsgQueue(p)
            receive_queue = MsgQueue(p)
            pool_sender = ThreadPool(processes=1)
            pool_receiver = ThreadPool(processes=1)

            if protocol == Protocol.GBN:
                async_result_sender = pool_sender.apply_async(gbn_sender,
                                                              (w, max_number, timeout, send_queue, receive_queue))
                async_result_receiver = pool_receiver.apply_async(gbn_receiver, (w, send_queue, receive_queue))
            elif protocol == Protocol.SRP:
                async_result_sender = pool_sender.apply_async(srp_sender,
                                                              (w, max_number, timeout, send_queue, receive_queue))
                async_result_receiver = pool_receiver.apply_async(srp_receiver, (send_queue, receive_queue))
            else:
                raise Exception("Protocol is not supported")

            timer_start = time.time()

            posted_msgs = async_result_sender.get()
            received_msgs = async_result_receiver.get()
            timer_end = time.time()

            k = len(received_msgs) / len(posted_msgs)
            elapsed = timer_end - timer_start

            table_row += f" | {elapsed:2.2f}  | {k:.2f}   "
            if protocol == Protocol.GBN:
                gbn_time.append(elapsed)
                gbn_k.append(k)
            else:
                srp_time.append(elapsed)
                srp_k.append(k)

        print(table_row)

    fig, ax = plt.subplots()
    ax.plot(window_sizes, gbn_k, label="Go-Back-N")
    ax.plot(window_sizes, srp_k, label="Selective repeat")
    ax.set_xlabel('window size')
    ax.set_ylabel('efficiency')
    ax.legend()
    plt.show()

    fig, ax = plt.subplots()
    ax.plot(window_sizes, gbn_time, label="Go-Back-N")
    ax.plot(window_sizes, srp_time, label="Selective repeat")
    ax.set_xlabel('window size')
    ax.set_ylabel('time (sec)')
    ax.legend()
    plt.show()


if __name__ == '__main__':
    # loss_probability_research()
    window_size_research()
