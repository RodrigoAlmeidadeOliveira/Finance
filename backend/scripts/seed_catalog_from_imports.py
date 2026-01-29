"""
Popula cadastros base (categorias, instituições) a partir dos dados já importados.

Uso:
    python -m backend.scripts.seed_catalog_from_imports
ou
    python backend/scripts/seed_catalog_from_imports.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Garante que backend/ está no PYTHONPATH ao rodar diretamente este arquivo
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config import Config
from app.database import get_session, init_engine
from app.services.catalog_seed import CatalogSeeder


def main() -> None:
    database_url = os.getenv("DATABASE_URL", Config.SQLALCHEMY_DATABASE_URI)
    init_engine(database_url)

    seeder = CatalogSeeder(get_session)
    result = seeder.seed_from_imports()

    print("✅ Seed concluído")
    print(f"  Instituições criadas: {result['institutions_created']}")
    print(f"  Categorias criadas: {result['categories_created']}")


if __name__ == "__main__":
    main()
