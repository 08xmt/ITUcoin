
class LoadBlockchain:
    folder_name = "blocks/"
    blocks_pr_file = 1000

    def _get_filename(self, block_number):
        block_multiplier = int(block_number/self.blocks_pr_file)
        from_block = self.blocks_pr_file*block_multiplier
        return "blocks" + str(from_block) + "to" + str(from_block+self.blocks_pr_file)


    def open_file(self, block_number):
        file_path = self.folder_name + self._get_filename(block_number)
#        with open(file_path) as f:


#        return file_path