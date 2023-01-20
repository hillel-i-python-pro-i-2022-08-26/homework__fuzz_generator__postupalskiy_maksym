import logging
import multiprocessing
import pathlib
import uuid
from itertools import product
from logging import Logger
from multiprocessing import Pool
from string import ascii_lowercase, digits
from typing import Iterable

STORAGE = pathlib.Path(__file__).parent.joinpath("storage")


def init_logger() -> Logger:
    logger = logging.getLogger()
    logging.basicConfig(level=logging.INFO)
    return logger


class Combinator:
    def __init__(
        self,
        alphabet: Iterable,
        str_len: int,
        purge_after: bool = True,
        logger: Logger = init_logger(),
    ):
        self.alphabet = alphabet
        self.str_len = str_len
        self.purge_after = purge_after
        self.logger = logger

    def product(self):
        self.logger.info("STATUS--> STARTING... Combining started!")
        self.pre_clean()
        with Pool(processes=multiprocessing.cpu_count() - 1) as pool:
            result = pool.map(self._get_for_char, self.alphabet)
            self.logger.info("Filenames received.")
            for name in result:
                self.logger.info(f"Extracting combinations from {name} in process")
                with open(STORAGE.joinpath("words/words_generation.txt"), mode="a") as file_result:
                    with open(name) as producer:
                        file_result.write(producer.read())
        if self.purge_after:
            self.logger.info("Creating .txt files...")
            Combinator.purge_files()
        self.logger.info("STATUS--> CREATED! words.generation.txt successfully generated.")

    def combinations_generator(self, char):
        for starter_combination in product(self.alphabet, repeat=self.str_len - 1):
            combination = [char]
            combination.extend(starter_combination)
            yield combination

    def _get_for_char(self, char) -> pathlib.Path:
        self.logger.info(f"{char} in process")
        file_name = STORAGE.joinpath(f"{uuid.uuid4()}.txt")
        result = self.combinations_generator(char)
        with open(file_name, mode="w") as file:
            file.write(Combinator.writer("".join(combination) for combination in result))
        return file_name

    def pre_clean(self):
        try:
            STORAGE.joinpath("words/words_generation.txt").unlink()
            self.logger.info("STATUS--> CLEANED!")
        except FileNotFoundError:
            self.logger.info("STATUS--> CLEANED!")

    @staticmethod
    def writer(result_list: Iterable[str]) -> str:
        return "\n".join(result_list)

    @staticmethod
    def purge_files():
        for file in STORAGE.glob("*.txt"):
            STORAGE.joinpath(file).unlink()


if __name__ == "__main__":
    repeats = 5
    alphabet_for_combinations = ascii_lowercase + digits
    combinator = Combinator(alphabet_for_combinations, repeats, purge_after=True)
    combinator.product()
