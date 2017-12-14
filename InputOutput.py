from Block import Block
import os
import glob
import linecache
import json
from collections import defaultdict

dir_path = os.path.dirname(os.path.realpath(__file__))

class Input_Output:
    folder_name = dir_path + "/blocks/"
    blocks_pr_file = 1000
    file_ending = ".json"
    
    def __init__(self, path_extension=""):
        self.folder_name = self.folder_name + path_extension
    
    #public methods
    def insert_blocks(self, blocks):
        file_names = self._get_file_names(blocks)

        for file, blocks_list in file_names.items():
            final_URI = self.folder_name + str(file)
            self._write_blocks_to_file(blocks_list, final_URI)


    # Uses linecache. It takes the filelocation using folder_name and appending the filename. Then, using the _get_block_line finds which line in the text the block number exists in
    def get_block(self, block_number):
        try:
            block_string = linecache.getline(self.folder_name + self._get_filename(block_number),
                                             self._get_block_line(block_number)).strip()
            return self.json_block_to_block_object(block_string)
        except:
            return self.get_newest_block()

    #baj = block as jsonn
    def json_block_to_block_object(self, block_string):
        b_json = json.loads(block_string)
        keys = list(b_json.keys())
        baj = b_json[str(keys[0])]
        block = Block(nonce=baj['nonce'], block_header_hash=baj['block_header_hash'],
                      previous_block_header_hash=baj['previous_block_header_hash'],
                      transactions=baj['transactions'], block_height=baj['block_height'], time=baj['time'])
        return block

    def get_newest_block(self):
        json_strings = self.folder_name + "blocks*to*.json"
        string_list = glob.glob(json_strings)
        newest_json_file = string_list[0]

        for jstring in string_list:
            block_height_to = self._get_block_to_value(jstring)
            if block_height_to > self._get_block_to_value(newest_json_file):
                newest_json_file = jstring

        with open(newest_json_file) as file:
            block_json = file.readlines()[-1]
        block = self.json_block_to_block_object(block_json)
        print(block)
        return block

    def _get_block_to_value(self, block_location):
        polished_string = block_location.replace(self.folder_name + "blocks", "")
        polished_string = polished_string.replace(".json", "")
        string_l = polished_string.split("to")
        return int(string_l[1])

    #Private methods
    def _get_filename(self, block_number):
        block_multiplier = int(block_number/self.blocks_pr_file)
        from_block = self.blocks_pr_file*block_multiplier+1
        to_block = from_block + self.blocks_pr_file-1
        return "blocks" + str(from_block) + "to" + str(to_block) + str(self.file_ending)

    def _write_blocks_to_file(self, block_list, file_name):
        file = open(file_name, "a")
        for block in block_list:
            writeable_block_dict = json.dumps({block.block_height: block.to_dict()})
            file.write(str(writeable_block_dict)+"\n")
        file.close()

    def _get_file_names(self, blocks):
        file_names = defaultdict(list)

        for block in blocks:
            file_names[self._get_filename(block.block_height)].append(block)

        return file_names

    def _get_block_line(self, block_number):
        if block_number > 1000:
            block_line = block_number - 1000
        else:
            block_line = block_number

        return block_line


if __name__ == '__main__':
    block = Block(1, "heeej", "heeejsa", [], 1500, 123456)
    blockchaon = Input_Output()
    blockchaon.insert_blocks([block])
    blockchaon.get_newest_block()
