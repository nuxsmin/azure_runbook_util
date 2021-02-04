from abc import ABC, abstractmethod

from azure_runbook_util import util


class OpsBase(ABC):
    def __init__(self,
                 dry_run: bool = False,
                 debug: bool = False,
                 wait_for_action: bool = False) -> None:
        """
        :param dry_run: Perform a trial run with no changes made
        :param debug: Set logging level to DEBUG
        :param wait_for_action: Set to True to perform synchronous API actions
        """
        self.now = util.get_now_for_timezone()

        self.dry_run = dry_run
        self.debug = debug
        self.wait_for_action = wait_for_action

    @abstractmethod
    def run(self) -> None:
        pass
