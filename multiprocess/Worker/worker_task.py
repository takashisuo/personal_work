#import sys
import time
import logging
from random import random
import logging.handlers
import multiprocessing
import logging
import logging.handlers
import multiprocessing


class WorkerTask():
    
    def __init__(self, unique_val:str):
        self.unique_value = unique_val
        
    def wrapper_main(self, value:str, log_queue: multiprocessing.Queue) -> str:
        try:
            self.logger = logging.getLogger()
            handler = logging.handlers.QueueHandler(log_queue)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.DEBUG)
            name = multiprocessing.current_process().name
            self.logger.info(f"started.. : proc_name={name}, value={value}, unique_value={self.unique_value}")
            for j in range(10):
                time.sleep(random())
                self.logger.info(f"running.. : proc_name={name}, value={value}, number={j}")
            self.logger.info(f"end...... : proc_name={name}, unique_value={self.unique_value}")
            return_val = "end_" + value
        finally:
            # これがないとプロセスとしてhandlerを追加したままで2回キックされる
            self.logger.error(f"end wrapper main.")
            self.logger.handlers.clear()
        
        return return_val