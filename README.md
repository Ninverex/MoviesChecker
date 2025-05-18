# Movies Checker - Aplikacja do zarządzania kolekcją filmów

Aplikacja **Movies Checker** umożliwia zarządzanie kolekcją filmów z integracją danych z OMDb API. Obsługuje system rejestracji/logowania użytkowników oraz przechowuje dane w lokalnej bazie SQLite. Interfejs graficzny został zbudowany przy użyciu biblioteki PySide6.

---

## 📋 Spis treści
- [Funkcjonalności](#-funkcjonalności)
- [Podział obowiązków](#-podział-obowiązków)
- [Dokumentacja kodu](#-dokumentacja-kodu)
- [Wymagania systemowe](#-wymagania-systemowe)
- [Instalacja i konfiguracja](#-instalacja-i-konfiguracja)
- [Uruchomienie](#-uruchomienie)
- [Jak korzystać?](#-jak-korzystać)
- [Struktura projektu oraz bazy danych](#-struktura-bazy-danych)
- [Uwagi](#-uwagi)

---

## 🚀 Funkcjonalności
- **Rejestracja i logowanie**:  
  - Bezpieczne haszowanie haseł (biblioteka `werkzeug.security`).  
  - Walidacja formatu e-maila (max 10 znaków przed `@`, np. `user@domain.com`).  
- **Dodawanie filmów**: Automatyczne pobieranie informacji o filmie (rok, gatunek) z OMDb API na podstawie tytułu.  
- **Przeglądanie listy filmów**: Tabela z tytułami, rokiem produkcji, gatunkiem i informacją o dodającym.  
- **Filtrowanie i sortowanie**:  
  - Filtrowanie po gatunku i roku (lub zakresie lat).  
  - Sortowanie po roku (rosnąco/malejąco).  
- **Szczegóły filmu**: Okno dialogowe z plakatem, opisem, obsadą, reżyserem i ocenami (dane z OMDb API).  
- **Eksport danych**:  
  - Do plików PDF, JSON i CSV.  
- **Import danych**: Wczytywanie filmów z plików JSON i CSV z automatycznym pobieraniem danych z API.  
- **Usuwanie filmów**: Możliwość usunięcia wybranego filmu z bazy.  

---
## Podział obowiązków
- Mateusz Ostrowski (50%):
  - Implementacja GUI (klasa MainWindow, layouty, przyciski, tabela).
  - Integracja z OMDB API (pobieranie danych, wyświetlanie plakatów).
  - Obsługa eksportu do PDF i formatów tekstowych (JSON/CSV).
- Maciej Pintal (50%):
  - Logika biznesowa (połączenie z bazą danych SQLite, zapisywanie i wczytywanie filmów).
  - Filtrowanie i sortowanie danych (mechanizm zapytań SQL).
  - Implementacja okien dialogowych (np. MovieDetailsDialog).
  - Obsługa operacji CRUD (dodawanie, usuwanie filmów).

---
## 🧩 Dokumentacja kodu
### Klasa `mainWindow`
#### Opis:
Główne okno aplikacji z tabelą filmów, systemem filtrów i funkcjami zarządzania danymi.

### Kluczowe metody:
1. **`__init__(self)`**  
   - Inicjalizuje UI:  
     - **Lewy panel**: Przyciski eksportu/importu danych i wylogowania.  
     - **Centralny panel**: Tabela `QTableWidget` z listą filmów (tytuł, rok, gatunek, dodający).  
     - **Prawy panel**: Filtry (gatunek, rok, sortowanie), formularz dodawania filmów, przyciski usuwania i eksportu do PDF.  
   - Łączy sygnały (np. podwójne kliknięcie wiersza → `show_movie_details()`).

2. **`load_movies(self)`**  
   - Ładuje filmy z bazy danych `movies.db` z uwzględnieniem aktywnych filtrów:  
     - **SQL Query**: Dynamicznie buduje zapytanie z warunkami `WHERE` i `ORDER BY`.  
     - **Przykład zapytania**:  
       ```sql
       SELECT movies.title, movies.year, movies.genre, users.login 
       FROM movies 
       JOIN users ON movies.user_id = users.id 
       WHERE genre = 'Action' AND year BETWEEN 2000 AND 2020 
       ORDER BY year DESC
       ```  
   - Wyświetla komunikaty o braku wyników.

3. **`add_movie(self)`**  
   - Dodaje film do bazy danych:  
     1. Pobiera tytuł z pola `input_title`.  
     2. Wysyła zapytanie do OMDB API (`get_movie_info_from_api()`), aby uzyskać rok i gatunek.  
     3. Jeśli API nie zwróci danych, pyta użytkownika o kontynuację.  
     4. Wstawia rekord do tabeli `movies` z przypisanym `user_id` (ID zalogowanego użytkownika).  

4. **`show_movie_details(self, row, column)`**  
   - Pobiera dane filmu z wybranego wiersza tabeli.  
   - Otwiera `MovieDetailsDialog` z przekazanymi danymi.  

5. **`export_to_pdf(self)`**  
   - Generuje raport PDF za pomocą `reportlab`:  
     - Nagłówek z datą i filtrami.  
     - Tabela z danymi (tytuł, rok, gatunek, dodający).  
     - Automatyczne łamanie stron i podsumowanie.  

6. **`save_to_json(self)` / `load_from_json(self)`**  
   - **Eksport**: Zapisuje wszystkie filmy z bazy do pliku JSON.  
   - **Import**: Wczytuje filmy z JSON, pobiera brakujące dane z API, unika duplikatów.  

### Integracja z API:
- **`get_movie_info_from_api(self, title)`**  
  Wysyła zapytanie do OMDB API i zwraca podstawowe dane (rok, gatunek).  
  - **Przykład odpowiedzi**:  
    ```python
    {'year': '2023', 'genre': 'Action'}
    ```  

### Obsługa błędów:
- **Brak połączenia z API**: Wyświetla komunikaty w UI (np. "Błąd pobierania danych").  
- **Nieprawidłowe filtry**: Waliduje format roku (np. `2020` lub `2010-2020`).  
- **Duplikaty filmów**: Ignoruje duplikaty podczas importu z JSON/CSV.  

---

## 🎨 Stylizacja UI
- **CSS**: Elementy stylizowane za pomocą `setStyleSheet` (np. kolory, zaokrąglenia).  
- **Ikony**: Używa ikon z folderu `icons/` (np. `login.png`, `register.png`).  
- **Responsywność**: Tabela automatycznie dostosowuje szerokość kolumn (`QHeaderView.Stretch`).  

---

## 🔗 Zależności
- **PySide6**: Biblioteka do budowy interfejsu.  
- **SQLite3**: Przechowywanie danych użytkowników i filmów.  
- **OMDB API**: Źródło danych o filmach (wymagany klucz API).  
- **ReportLab**: Generowanie plików PDF.  

--- 

### Klasa `LoginScreen`
#### Opis:
Okno logowania z walidacją danych użytkownika i integracją z bazą danych.

### Kluczowe metody:
1. **`__init__(self)`**  
   - Inicjalizuje interfejs:  
     - Pola `input_login` i `input_password` do wprowadzenia danych.  
     - Przycisk **"Log In"** wywołujący `attempt_login()`.  
     - Przycisk **"Create an Account"** otwierający `RegisterDialog`.  
   - Stylizacja CSS dla pól wejściowych i przycisków.

2. **`attempt_login(self)`**  
   - **Logika**:  
     1. Pobiera login i hasło z pól wejściowych.  
     2. Wykonuje zapytanie SQL:  
        ```sql
        SELECT id, password FROM users WHERE login = ?
        ```  
     3. Sprawdza poprawność hasła za pomocą `check_password_hash`.  
     4. Emituje sygnał `login_success` po udanej autentykacji.  
   - **Bezpieczeństwo**:  
     - Użycie `sqlite3` z parametrami zapytań (`?`) do uniknięcia SQL injection.  
     - Hasła porównywane są poprzez bezpieczne hashowanie (PBKDF2).

3. **`open_register_dialog(self)`**  
   - Otwiera okno rejestracji (`RegisterDialog`) jako modalne okno dialogowe.

---

### Klasa `RegisterDialog`
#### Opis:
Okno rejestracji z walidacją formatu e-maila i unikalności danych.

### Kluczowe metody:
1. **`__init__(self, parent)`**  
   - Inicjalizuje interfejs:  
     - Pola `input_email`, `input_login`, `input_password`.  
     - Przycisk **"Sign Up"** wywołujący `complete_registration()`.  
   - Stylizacja CSS w ciemnym motywie.

2. **`complete_registration(self)`**  
   - **Logika**:  
     1. Sprawdza, czy wszystkie pola są wypełnione.  
     2. Wykonuje walidację e-maila przez `validate_email()`.  
     3. Wywołuje `register_user()` z `database.py`, aby dodać użytkownika.  
   - **Zapytanie SQL**:  
     ```sql
     INSERT INTO users (email, login, password) VALUES (?, ?, ?)
     ```  
   - **Bezpieczeństwo**:  
     - Hasła są haszowane przez `generate_password_hash`.  
     - Sprawdzenie unikalności e-maila i loginu w bazie.

3. **`validate_email(self, email)`**  
   - Weryfikuje format e-maila za pomocą regex:  
     ```python
     r"^[a-zA-Z0-9]{1,10}@[a-zA-Z0-9]+\.[a-zA-Z]{2,}$"
     ```  
   - **Wymagania**:  
     - Max 10 znaków przed `@`.  
     - Domena z kropką (np. `@domain.com`).

---


## 💻 Wymagania systemowe
- Python 3.9 lub nowszy  
- Biblioteki: `PySide6`, `requests`, `reportlab`, `sqlite3`, `werkzeug`  
- Klucz API OMDb (bezpłatny na [omdbapi.com](https://www.omdbapi.com/apikey.aspx))  
### Technologie i narzędzia
- Język programowania: Python
- GUI: PySide6 (framework Qt dla Pythona)
- Baza danych: SQLite
- Integracja z API: OMDB API (pobieranie danych o filmach)
- Eksport danych:
    - PDF: biblioteka ReportLab
    - JSON/CSV: standardowe moduły Pythona (json, csv)
---

## 🔧 Instalacja i konfiguracja
1. Sklonuj repozytorium lub pobierz pliki.  
2. Zainstaluj wymagane biblioteki:  
   ```bash
   pip install PySide6 requests reportlab werkzeug
3. Zdobądź klucz API OMDb i zastąp wartość OMDB_API_KEY = "x" w pliku MainWindow.py swoim kluczem. 
4. Utwórz bazę danych SQLite (automatycznie przy pierwszym uruchomieniu).

---

## 🖥️ Uruchomienie
1. **Uruchom aplikację**:  
   Wykonaj komendę w terminalu:  
   ```bash
   python MainWindow.py
2. Aplikacja automatycznie utworzy bazę danych movies.db w folderze projektu (jeśli nie istnieje).

---

## 📖 Jak korzystać?
### Rejestracja  
1. Kliknij "Create an Account" na ekranie logowania.  
2. Wpisz e-mail (np. user@domain.com), unikalny login i hasło.
3. Kliknij "Sign Up".  
![image](https://github.com/user-attachments/assets/df4c44ca-6f58-4e05-9864-09b794632022)  

### Logowanie
1. Wpisz login i hasło.
2. Kliknij "Log In".  
![image](https://github.com/user-attachments/assets/c6f2c7ca-e12d-495a-948c-1e7948a15c7e)  

### Dodawanie filmu 
1. Dodawanie filmu
2. Wpisz tytuł filmu w polu "Title" w prawym panelu głównego okna.
3. Kliknij "Add Movie". Aplikacja automatycznie pobierze dane z OMDb API.  
![image](https://github.com/user-attachments/assets/cd9ebc86-86a8-4aa1-a563-4f59abc51a5a)  

### Filtrowanie i sortowanie
- Gatunek: Wybierz z listy rozwijanej.
- Rok: Wpisz pojedynczy rok (np. 2020) lub zakres (np. 2010-2020).
- Sortowanie: Wybierz "Ascending" (rosnąco) lub "Descending" (malejąco).
- Kliknij "Apply Filters", aby zastosować zmiany.  
![image](https://github.com/user-attachments/assets/e94ea929-7d57-4f4e-a2ff-2a043b2eb691)  

### Eksport danych
- PDF: Kliknij "Export to PDF" i wybierz lokalizację pliku.
- JSON/CSV: Użyj przycisków "Save to JSON" lub "Save to CSV".  
![image](https://github.com/user-attachments/assets/961151fc-b08d-46c4-8463-58127e94e0d9)  

### Szczegóły filmu
Kliknij dwukrotnie na wybrany wiersz w tabeli, aby otworzyć okno z pełnymi informacjami i plakatem.  
![image](https://github.com/user-attachments/assets/b4e0e9ca-b8ca-480f-823c-b27d16363a25)  


---
## 🗃️ Struktura projektu oraz bazy danych
### Struktura projektu
![image](https://github.com/user-attachments/assets/d0b33609-ff8a-496e-af93-ba6ea1cd8818)  
### Struktura bazy danych
Baza danych movies.db zawiera dwie tabele:
1. users:
- id (INTEGER, PRIMARY KEY)
- email (TEXT, UNIQUE)
- login (TEXT, UNIQUE)
- password (TEXT)
2. movies:
- id (INTEGER, PRIMARY KEY)
- title (TEXT)
- year (INTEGER)
- genre (TEXT)
- user_id (INTEGER, FOREIGN KEY REFERENCES users(id))

---

##  📌 Uwagi
- Bezpieczeństwo haseł: Hasła są przechowywane w formie zahaszowanej (algorytm PBKDF2).
- Format e-maila: Wymagany format: nazwa@domena.rozszerzenie (max 10 znaków przed @).
- OMDb API: Plakaty i szczegóły filmów są dostępne tylko dla tytułów istniejących w bazie OMDb.

