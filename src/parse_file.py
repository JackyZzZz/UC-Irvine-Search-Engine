import json
from config import FINAL_INDEX_DIR, TOKEN_RETRIEVAL_OFFSET_FILE
import os


def tokens_load_for_read(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)

    output_file = json_file[:-4] + "txt"
    with open(output_file, 'w') as file:
        for term, postings in data.items():
            file.write(f"${term}$\n")
            for posting in postings:
                positions = ""
                for position in posting[2]:
                    positions += f" {position}"
                write_in = f"{posting[0]},{posting[1]},{positions}"
                file.write(f"{write_in}\n")


def track_token_retreival_offset(text_file, token_retrieval_offset_map):
    token = None
    posting_len = 0
    position = None
    with open(text_file, 'r') as file:
        while True:
            line = file.readline()
            if not line:
                break
            if line.startswith('$') and line.endswith('$\n'):
                if token:
                    token_retrieval_offset_map[token] = [position, posting_len]
                token = line[1:-2]
                position = file.tell()
                posting_len = 0
            else:
                posting_len += 1
    if not token:
        token_retrieval_offset_map[token] = [position, posting_len]

def load_token_data(file, location_info):
    file.seek(location_info[0])
    length = location_info[1]
    data_fetched = []
    count = 0
    while count < length:
        count += 1
        line = file.readline()
        parts = line.split(",")
        id = int(parts[0])
        score = float(parts[1])
        numbers = list(map(int, parts[2].strip().split()))
        data_fetched.append([id, score, numbers])
    file.seek(0)
    return data_fetched

def processing_final_tokens():
    token_retrieval_offset_map = {}
    for letter in range(ord('a'), ord('z') + 1):
        tokens_load_for_read(f'{FINAL_INDEX_DIR}/{chr(letter)}_tokens.json')
        track_token_retreival_offset(f'{FINAL_INDEX_DIR}/{chr(letter)}_tokens.txt', token_retrieval_offset_map)
        print(f"Finish processing {FINAL_INDEX_DIR}/{chr(letter)}_tokens.json")
    for letter in range(ord('0'), ord('9') + 1):
        tokens_load_for_read(f'{FINAL_INDEX_DIR}/{chr(letter)}_tokens.json')
        track_token_retreival_offset(f'{FINAL_INDEX_DIR}/{chr(letter)}_tokens.txt', token_retrieval_offset_map)
        print(f"Finish processing {FINAL_INDEX_DIR}/{chr(letter)}_tokens.json")
    with open(TOKEN_RETRIEVAL_OFFSET_FILE, 'w') as file:
        json.dump(token_retrieval_offset_map, file)
        print("Finish writing token retrieval offset file")
