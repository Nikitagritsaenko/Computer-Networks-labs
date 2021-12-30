import time

from lab1.message_utils import Message, MessageStatus


def gbn_sender(window_size, max_number, timeout, send_queue, receive_queue):
    posted_msgs = []
    curr_number = 0
    last_ans_number = -1
    start_time = time.time()
    while last_ans_number < max_number:
        expected_number = (last_ans_number + 1) % window_size

        if not receive_queue.is_empty():
            ans = receive_queue.get_next_message()
            if ans.number == expected_number:
                last_ans_number += 1
                start_time = time.time()
            else:
                curr_number = last_ans_number + 1

        if time.time() - start_time > timeout:
            curr_number = last_ans_number + 1
            start_time = time.time()

        if (curr_number < last_ans_number + window_size) and (curr_number <= max_number):
            k = curr_number % window_size
            msg = Message()
            msg.number = k
            msg.real_number = curr_number
            send_queue.send_message(msg)
            posted_msgs.append(f"{curr_number}({k})")
            curr_number += 1
        pass

    msg = Message()
    msg.data = "STOP"
    send_queue.send_message(msg)
    return posted_msgs


def gbn_receiver(window_size, send_queue, receive_queue):
    received_msgs = []
    expected_number = 0
    while True:
        if not send_queue.is_empty():
            curr_msg = send_queue.get_next_message()
            if curr_msg.data == "STOP":
                break

            if curr_msg.status == MessageStatus.LOST:
                continue

            if curr_msg.number == expected_number:
                ans = Message()
                ans.number = curr_msg.number
                receive_queue.send_message(ans)

                received_msgs.append(f"{curr_msg.real_number}({curr_msg.number})")
                expected_number = (expected_number + 1) % window_size

            else:
                continue
    return received_msgs
