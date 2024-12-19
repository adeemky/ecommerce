import time
from psycopg2 import (
    OperationalError as Psycopg2OpError,
)  # PostgreSQL veritabanı ile ilgili bir işlem sırasında oluşan bir hata durumunu temsil eder.

from django.db.utils import (
    OperationalError,
)  # Django'nun veritabanı ile ilgili bir işlem sırasında karşılaşılan bir hatayı temsil eder
from django.core.management.base import (
    BaseCommand,
)  # Kendi django komutlarimizi olusturmamizi saglar. Bir class'in parametresi olarak kullanilir.


class Command(BaseCommand):
    """Django command to wait for database."""

    def handle(
        self, *args, **options
    ):  # BaseCommand class'inin icine handle adinda bir func olusturulur.
        self.stdout.write(
            "Waiting for database..."
        )  # Django'nun yönetim komutlarında konsola çıktı vermek için kullanılır.
        db_up = False
        while db_up is False:  # db_up'in degeri false iken:
            try:
                self.check(
                    databases=["default"]
                )  # BaseCommand sınıfının bir yöntemini çağırır. veritabanının erişilebilir olup olmadığını kontrol etmek için kullanılır.
                db_up = True  # DB erisilir ise db_up'in degerini True yapar
            except (Psycopg2OpError, OperationalError):
                self.stdout.write("Database unavailable, waiting 1 second...")
                time.sleep(1)
            self.stdout.write(
                self.style.SUCCESS("Database available!")
            )  # try except blogu tamalandiktan sonra yani DB erisilebilir oldugunda burayi yazdirir. style.SUCCESS yesil renkte basarili anlamina gelen bir cikti verir.
