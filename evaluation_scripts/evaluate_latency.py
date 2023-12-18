import re
import sys
from datetime import timedelta
signature_pattern = r'signature: \\"([^\\]+)'
delay_pattern = r'delay=([^ ]+)'
slot_pattern = r'slot: (\d+)'
delayslotsignature = r'delay=([^ ]+).+slot: (\d+).+signature: \\"([^\\]+)'

def dur_to_delta( log_dur):
    pattern = r'(-?)((\d+)s)?((\d+)ms)?((\d+)us)?((\d+)ns)?'
    match = re.match(pattern, log_dur)
    seconds = millis = micros = nanos = 0
    td = timedelta()
    if match:
        sign = -1 if match.group(1) == "-" else 1
        if match.group(2) is not None:
            seconds = int(match.group(3))
        if match.group(4) is not None:
            millis = int(match.group(5))
        if match.group(6) is not None: 
            micros = int(match.group(7))
        if match.group(8) is not None:    
            nanos = int(match.group(9))

        total_milli_secs = sign * ( seconds * 1000 + millis + micros / 1000 + nanos / 1000000)
        td = timedelta(milliseconds=total_milli_secs)
    return td

        
# Function to parse sent.txt and extract signature, delay, and slot
def parse_sent_log(sent_file):
    sent_entries = {}
    with open(sent_file, 'r') as file:
        lines = file.readlines()
        for line in lines:
            signature_match = re.search(signature_pattern, line)
            delay_match = re.search(delay_pattern, line)
            slot_match = re.search(slot_pattern, line)
            # Check if matches were found and extract the data
            if signature_match and delay_match and slot_match:
                signature = signature_match.group(1).strip()
                delay = delay_match.group(1).strip()
                slot = slot_match.group(1).strip()
                #print(f"Signature: {signature}, Delay: {delay}, Slot: {slot}")
                sent_entries[signature] = [delay,  slot]
    return sent_entries

# Function to parse recv.txt, extract delay and slot based on sent_entries, and filter by sent_entries
def parse_recv_log(recv_file, sent_entries):
    recv_entries = {}
    with open(recv_file, 'r') as file:
        lines = file.readlines()
        for line in lines:
            match = re.search(delayslotsignature, line)
            if match:
                signature = match.group(3).strip()
                delay = match.group(1).strip()
                slot = match.group(2).strip()
                for (sent_signature, sent_data) in sent_entries.items():
                    #print(signature, sent_data)
                    if signature == sent_signature:
                        print(f"Recv Signature: {signature}, Delay: {delay}, Slot: {slot}")
                        print(f"Send Signature: {sent_signature}, {sent_data}")
                        recv_entries[signature] = [delay, slot]
                        #sent_data.append(delay)
                        #sent_data.append(slot)
                        break    # Stop searching for this signature once found
    return recv_entries

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py sent.txt recv.txt")
        sys.exit(1)

    sent_file = sys.argv[1]
    recv_file = sys.argv[2]

    # Parse sent.txt and recv.txt
    sent_entries = parse_sent_log(sent_file)
    print  ("Done sent", len(sent_entries))
    recv_entries = parse_recv_log(recv_file, sent_entries)

    # Print the joined information with delay, slot, and delay difference
    print("Signature, Recv Delay, Recv Slot, Sent Delay, Sent Slot, Rdelay-Sdelay ")
    for (signature, rdata) in recv_entries.items():
        sdata = sent_entries[signature]
        print(f"{signature}, {rdata[0]} , {rdata[1]} , {sdata[0]} , {sdata[1]}, \
                {(dur_to_delta(rdata[0])- dur_to_delta(sdata[0])).total_seconds()*1000} ")
