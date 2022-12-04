import logging
import logging.handlers
import multiprocessing
import os

class Logger:
    """
    ロギング用のクラスです。シングルトンで定義しているため、
    利用者はget_instance()メソッドを呼んでください。

    出力方式: コンソール出力とファイル出力です。
    ファイル出力: log_file.txt/err_file.txtに分かれており、前者は全レベルを対象とします。
    　err_file.txtはエラーレベル以上のみです。
    出力先: トップフォルダとなります。
    """

    __instance = None

    @classmethod
    def get_instance(
        cls,
        output_path:str=None,
        do_multiproc:bool=False
    ):
        """シングルトンでloggerを取得します。

        Args:
            output_path (str, optional): 設定ファイルパス。デフォルトはNone。Noneの場合はプロジェクト規定のファイルをinitで読み込む。

        Returns:
            Logger
        """
        if not cls.__instance:
            Logger(output_path, do_multiproc)
        return cls.__instance
    
    def __init__(
        self,
        output_path:str,
        do_multiproc:bool
    ):
        """初期化処理をおこないます。
           設定ファイルの読み込みが完了した後、
           formatter, handlerを読み込みます。

        Args:
            output_path (str, optional): get_instanceと同様。
        """

        log_dirpath:str = output_path
        if not os.path.exists(log_dirpath):
            os.makedirs(log_dirpath, exist_ok=True)

        Logger.__instance = logging.getLogger()
        Logger.__instance.setLevel(logging.DEBUG)
        Logger.__instance.handlers.clear()

        # que
        Logger.log_queue = multiprocessing.Manager().Queue(-1)

        # stdout
        formatter_console = logging.Formatter(
            '%(asctime)s,%(processName)s,%(levelname)s,%(message)s'
        )
        formatter_console.default_msec_format = '%s.%03d'
        std_handler = logging.StreamHandler()
        std_handler.setLevel(logging.DEBUG)
        std_handler.setFormatter(formatter_console)
        Logger.__instance.addHandler(std_handler)

        formatter_file = logging.Formatter(
            '%(asctime)s,%(processName)s,%(thread)d,%(levelname)s,%(module)s,%(funcName)s,L%(lineno)d,%(message)s'
        )
        formatter_file.default_msec_format = '%s.%03d'
        # file - all

        file_handler_all = self._create_file_handler(
            "log_file.txt",
            logging.DEBUG,
            formatter_file
        )
        Logger.__instance.addHandler(file_handler_all)
        
        file_handler_err = self._create_file_handler(
            "err_file.txt",
            logging.ERROR,
            formatter_file
        )
        Logger.__instance.addHandler(file_handler_err)

        # multi processing listener
        if not do_multiproc:
            Logger.listener = logging.handlers.QueueListener(
                Logger.log_queue,
                std_handler,
                file_handler_all,
                file_handler_err,
                respect_handler_level=True
            )
            Logger.listener.start()
        
    @classmethod
    def end(cls):
        try:
            Logger.listener.stop()
        except Exception:
            pass
        
    @classmethod
    def get_q(cls):
        return Logger.log_queue


    def _create_file_handler(self, filename:str, level:str, formatter:logging.Formatter)-> logging.FileHandler:
        """logging用のFileHandlerを作成します

        Args:
            filepath (str): 出力するログファイルパス
            level (str): ログレベル
            formatter (logging.Formatter): 出力フォーマット

        Returns:
            logging.FileHandler: 作成したFileHandler
        """
        handler = logging.FileHandler(
            filename=filename, encoding='utf-8'
        )
        handler.setLevel(level)
        handler.setFormatter(formatter)
        return handler
