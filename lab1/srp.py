import time

from lab1.message_utils import MessageStatus, Message, WindowNode, WindowMessageStatus


def srp_sender(window_size, max_number, timeout, send_queue, receive_queue):
    posted_msgs = []

    wnd_nodes = [WindowNode(i) for i in range(window_size)]

    ans_count = 0

    while ans_count < max_number:

        if not receive_queue.is_empty():
            ans = receive_queue.get_next_message()
            ans_count += 1
            wnd_nodes[ans.number].status = WindowMessageStatus.CAN_BE_USED

        curr_time = time.time()
        for i in range(window_size):
            if wnd_nodes[i].number > max_number:
                continue

            send_time = wnd_nodes[i].time
            if curr_time - send_time > timeout:
                wnd_nodes[i].status = WindowMessageStatus.NEED_REPEAT

        for i in range(window_size):
            if wnd_nodes[i].number > max_number:
                continue

            if wnd_nodes[i].status == WindowMessageStatus.BUSY:
                continue

            elif wnd_nodes[i].status == WindowMessageStatus.NEED_REPEAT:

                wnd_nodes[i].status = WindowMessageStatus.BUSY
                wnd_nodes[i].time = time.time()

                msg = Message()
                msg.number = i
                msg.real_number = wnd_nodes[i].number
                send_queue.send_message(msg)
                posted_msgs.append(f"{msg.real_number}({msg.number})")

            elif wnd_nodes[i].status == WindowMessageStatus.CAN_BE_USED:
                wnd_nodes[i].status = WindowMessageStatus.BUSY
                wnd_nodes[i].time = time.time()
                wnd_nodes[i].number = wnd_nodes[i].number + window_size

                if wnd_nodes[i].number > max_number:
                    continue

                msg = Message()
                msg.number = i
                msg.real_number = wnd_nodes[i].number
                send_queue.send_message(msg)
                posted_msgs.append(f"{msg.real_number}({msg.number})")

    msg = Message()
    msg.data = "STOP"
    send_queue.send_message(msg)

    return posted_msgs


def srp_receiver(send_queue, receive_queue):
    received_msgs = []
    while True:
        if not send_queue.is_empty():
            curr_msg = send_queue.get_next_message()

            if curr_msg.data == "STOP":
                break

            if curr_msg.status == MessageStatus.LOST:
                continue

            ans = Message()
            ans.number = curr_msg.number
            receive_queue.send_message(ans)
            received_msgs.append(f"{curr_msg.real_number}({curr_msg.number})")
    return received_msgs
