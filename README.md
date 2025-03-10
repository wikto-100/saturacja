# Saturacja

 Aplikacja webowa oparta na Django, służąca do zarządzania i wizualizacji danych klientów na mapie, pomiarów wysycenia klientów w dowolnym obszarze.
## Funkcjonalności:
- **Zarządzanie danymi według działów:**  
  Użytkownicy są przypisani do jednego lub wielu działów i mogą przełączać się między nimi, aby przeglądać dane przypisane do wybranego działu.
- **Zarządzanie danymi klientów:**  
  Import, eksport oraz edycja rekordów klientów.
- **Pomiar saturacji:**  
  - Obliczanie i wskaźnika (stosunku aktywnych do nieaktywnych klientów) dla wybranego obszaru geograficznego.
  - Wyświetlanie markerów saturacji na mapie wraz z możliwością ich usuwania.
- **Mapowanie GIS:**  
  Wyświetlanie markerów klientów (zielone dla aktywnych, czerwone dla nieaktywnych) oraz markerów saturacji (pomarańczowe) na mapie Leaflet.
- **Zarządzanie sesją:**  
  - Pasek nawigacyjny pokazuje odliczanie czasu pozostałego do wygaśnięcia sesji.

## Instalacja

### Wymagania

- Python 3.13
- PostgreSQL z włączonym rozszerzeniem PostGIS  
- Virtualenv (zalecane)

### Kroki

1. **Sklonuj repozytorium:**

   ```bash
   git clone <repository-url>
   cd saturacja
   ```

2. **Utwórz i aktywuj wirtualne środowisko:**

   ```bash
   python -m venv venv
   source venv/bin/activate   # Na Windows: venv\Scripts\activate
   ```

3. **Zainstaluj zależności:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Skonfiguruj bazę danych:**

   Zaktualizuj plik `saturacja/settings.py` zgodnie z ustawieniami Twojej bazy danych PostgreSQL. Upewnij się, że PostGIS jest włączony.

5. **Ustaw zmienne środowiskowe dla bezpieczeństwa:**

   W środowisku produkcyjnym ustaw zmienną DJANGO_SECRET_KEY. Na przykład:

   ```bash
   export DJANGO_SECRET_KEY="twoj-produkcjny-klucz"
   ```

6. **Uruchom migracje:**

   ```bash
   python manage.py migrate
   ```

7. **Zbierz statyczne pliki:**

   ```bash
   python manage.py collectstatic
   ```

8. **Utwórz superużytkownika:**

   ```bash
   python manage.py createsuperuser
   ```

## Uruchamianie Aplikacji

Uruchom serwer developerski:

```bash
python manage.py runserver
```

Odwiedź [http://127.0.0.1:8000](http://127.0.0.1:8000) aby zobaczyć aplikację. Zaloguj się przy użyciu utworzonego użytkownika.

## Wdrożenie

Dla wdrożenia produkcyjnego rozważ:

- Ustawienie `DEBUG = False` w pliku ustawień.
- Skonfigurowanie `ALLOWED_HOSTS` dla swojej domeny.
- Użycie serwera WSGI, takiego jak Gunicorn, za reverse proxy (np. Nginx).
- Bezpieczne skonfigurowanie zmiennych środowiskowych (np. DJANGO_SECRET_KEY).

Przykładowa komenda dla Gunicorn:

```bash
gunicorn saturacja.wsgi:application --bind 0.0.0.0:8000
```
