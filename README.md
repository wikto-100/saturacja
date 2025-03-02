# Saturacja

**Saturacja** to aplikacja webowa oparta na Django, służąca do zarządzania i wizualizacji danych klientów na mapie. Aplikacja wykorzystuje PostGIS do obsługi danych przestrzennych i oferuje następujące funkcje:

- **Zarządzanie danymi według działów:**  
  Użytkownicy są przypisani do jednego lub wielu działów i mogą przełączać się między nimi, aby przeglądać dane przypisane do wybranego działu.
- **Zarządzanie danymi klientów:**  
  Import, eksport oraz edycja rekordów klientów bezpośrednio na interaktywnej mapie.
- **Pomiar saturacji:**  
  Obliczanie i wyświetlanie wskaźnika (stosunku aktywnych do nieaktywnych klientów) dla wybranego obszaru geograficznego.
- **Mapowanie GIS:**  
  Wyświetlanie markerów klientów (zielone dla aktywnych, czerwone dla nieaktywnych) oraz markerów saturacji (pomarańczowe) na mapie Leaflet, z pełną polską lokalizacją interfejsu.
- **Zarządzanie sesją:**  
  Pasek nawigacyjny wyświetla odliczanie czasu pozostałego do wygaśnięcia sesji.

## Funkcje

- **Zarządzanie użytkownikami i działami:**  
  - Użytkownicy są przypisani do jednego lub wielu działów.
  - Przełącznik działów w pasku nawigacyjnym pozwala użytkownikom wybrać dział, w którym chcą przeglądać dane.
- **Obsługa danych klientów:**  
  - Import danych klientów z plików CSV.
  - Edycja danych klientów bezpośrednio za pomocą popupów na mapie.
  - Eksport danych klientów do pliku CSV.
- **Pomiar saturacji:**  
  - Pomiar saturacji (stosunek aktywnych do wszystkich klientów) w obrębie wybranego obszaru za pomocą narysowanego wielokąta.
  - Wyświetlanie markerów saturacji na mapie wraz z możliwością ich usuwania.
- **Funkcje GIS:**  
  - Wykorzystanie PostGIS do przechowywania danych przestrzennych.
  - Interaktywne mapowanie z użyciem Leaflet.
  - Pełna lokalizacja interfejsu Leaflet na język polski.
- **Zarządzanie sesją:**  
  - Pasek nawigacyjny pokazuje odliczanie czasu pozostałego do wygaśnięcia sesji.

## Instalacja

### Wymagania

- Python 3.8+ (testowane na 3.13)
- PostgreSQL z włączonym rozszerzeniem PostGIS  
- Virtualenv (zalecane)
- Node.js i npm (jeśli używasz zarządzania front-endem)

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

Odwiedź [http://127.0.0.1:8000](http://127.0.0.1:8000) aby zobaczyć aplikację. Zaloguj się przy użyciu utworzonego użytkownika i korzystaj z przełącznika działów w pasku nawigacyjnym, aby zmieniać kontekst danych.

## Testowanie

Uruchom zestaw testów za pomocą:

```bash
python manage.py test
```

*Uwaga:* Upewnij się, że Twoje ustawienia testowej bazy danych pozwalają na tworzenie rozszerzeń PostGIS. Może być konieczne dostosowanie uprawnień PostgreSQL do celów testowych.

## Wdrożenie

Dla wdrożenia produkcyjnego rozważ:

- Ustawienie `DEBUG = False` w pliku ustawień.
- Skonfigurowanie `ALLOWED_HOSTS` dla swojej domeny.
- Użycie serwera WSGI, takiego jak Gunicorn, za reverse proxy (np. Nginx).
- Serwowanie plików statycznych przy użyciu dedykowanego serwera lub CDN.
- Bezpieczne skonfigurowanie zmiennych środowiskowych (np. DJANGO_SECRET_KEY).
- Opcjonalne użycie Whitenoise do serwowania plików statycznych.

Przykładowa komenda dla Gunicorn:

```bash
gunicorn saturacja.wsgi:application --bind 0.0.0.0:8000
```

## Dodatkowe Informacje

- **Integracja Użytkowników i Działów:**  
  Użytkownicy są przypisani do jednego lub wielu działów poprzez profil użytkownika. Aktualny wybór działu (przechowywany w profilu lub sesji) decyduje o tym, które dane klientów i saturacji są wyświetlane.

- **Import/Eksport CSV:**  
  - Pliki CSV do importu powinny być kodowane w cp1250 i używać średnika (`;`) jako separatora.
  - Przy eksporcie dane są filtrowane na podstawie wybranego działu oraz parametrów określonych przez użytkownika.

- **Pomiar Saturacji:**  
  - Narysuj wielokąt na mapie i użyj przycisku "Pomiar", aby zmierzyć saturację (stosunek aktywnych do wszystkich klientów) w obrębie tego obszaru.
  - Markery saturacji są zapisywane w bazie danych i mogą być zarządzane (usuwane) za pomocą interfejsu mapy.

- **Lokalizacja Leaflet:**  
  Wszystkie elementy interfejsu Leaflet (tooltipy, przyciski narzędzi, itp.) są zlokalizowane na język polski dla spójności.

## Licencja

[Podaj tutaj swoją licencję]
[zrob to mniej gpt-owe]
