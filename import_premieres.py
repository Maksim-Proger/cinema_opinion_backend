import logging

from app.core.database import init_db_pool
from app.usecases.import_premieres import import_premieres

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    init_db_pool()
    print(import_premieres())

