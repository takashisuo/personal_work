import sys
from random import random
from concurrent import futures
import multiprocessing
import os
import sys
import ast
import multiprocessing
from typing import Any
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from Logger.logger import Logger
from Worker.worker_task import WorkerTask


def wrapper_main(obj1, obj2, obj3):
    return obj1.wrapper_main(obj2, obj3)

def main():

    # main logging
    logger = Logger.get_instance(output_path=".\\")
    name = multiprocessing.current_process().name
    
    # process pool executor
    with futures.ProcessPoolExecutor(3) as executor:
        results = []
        multi_pipelines = [WorkerTask("a"), WorkerTask("b"), WorkerTask("c"), WorkerTask("d"), WorkerTask("e")]

        # child_process
        for i, light_pr in enumerate(multi_pipelines, 1):
            results.append(executor.submit(wrapper_main, light_pr, str(i), Logger.get_q()))

        for pipeline in futures.as_completed(results):
            try:
                res = pipeline.result()
                logger.info(f"return... : proc={name}, res={res}")
            except Exception as e:
                logger.exception(f"unexpected error")
        Logger.end()
    

if __name__ == '__main__':
    main()