from Block import Block
import os
import linecache
import json
from collections import defaultdict

dir_path = os.path.dirname(os.path.realpath(__file__))

class LoadBlockchain:
    folder_name = dir_path + "/blocks/"
    blocks_pr_file = 1000
    file_ending = ".json"


    def _get_filename(self, block_number):
        block_multiplier = int(block_number/self.blocks_pr_file)
        from_block = self.blocks_pr_file*block_multiplier+1
        to_block = from_block + self.blocks_pr_file-1
        return "blocks" + str(from_block) + "to" + str(to_block) + str(self.file_ending)

    def insert_blocks(self, blocks):
        file_names = self.get_file_names(blocks)

        for file, blocks_list in file_names.items():
            final_URI = self.folder_name + str(file)
            self.write_blocks_to_file(blocks_list, final_URI)



    def write_blocks_to_file(self, block_list, file_name):
        file = open(file_name, "a")
        for block in block_list:
            writeable_block_dict = json.dumps({block.block_height: block.to_json()})
            print(writeable_block_dict)
            file.write(str(writeable_block_dict)+"\n")
        file.close()


    def get_file_names(self, blocks):
        file_names = defaultdict(list)

        for block in blocks:
            file_names[self._get_filename(block.block_height)].append(block)

        return file_names


    #Uses linecache. It takes the filelocation using folder_name and appending the filename. Then, using the _get_block_line finds which line in the text the block number exists in
    def get_block(self, block_number):
        block_string = linecache.getline( self.folder_name + self._get_filename(block_number), self._get_block_line(block_number)).strip()
        b_json = json.loads(block_string)
        baj = b_json[str(block_number)]
        block = Block(nonce=baj['nonce'], block_header_hash=baj['block_header_hash'], previous_block_header_hash=baj['previous_block_header_hash'], transactions=baj['transactions'], block_height=baj['block_height'])
        return block



    def _get_block_line(self, block_number):
        block_line = 0
        if block_number > 1000:
            block_line = block_number - 1000
        else:
            block_line = block_number

        return block_line