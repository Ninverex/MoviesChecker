import sys
import sqlite3
import json
import csv
import requests
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog, QComboBox,
    QDialog, QTextEdit, QSplitter, QFrame
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QImage
from reportlab.pdfgen import canvas
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QHeaderView, QSizePolicy
from io import BytesIO

# Klucz API do OMDB API
OMDB_API_KEY = "x"


class MovieDetailsDialog(QDialog):
    def __init__(self, movie_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Szczegóły filmu: {movie_data['title']}")
        self.setMinimumSize(800, 500)

        # Główny layout
        main_layout = QHBoxLayout(self)

        # Lewy panel na plakat
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Plakat filmu
        self.poster_label = QLabel()
        self.poster_label.setFixedSize(300, 450)
        self.poster_label.setAlignment(Qt.AlignCenter)
        self.poster_label.setStyleSheet("border: 1px solid #ccc; background-color: #f5f5f5;")
        left_layout.addWidget(self.poster_label)
        left_layout.addWidget(QLabel("Źródło: OMDb API"))

        # Prawy panel na informacje
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Podstawowe informacje
        self.title_label = QLabel(f"<h1>{movie_data['title']}</h1>")
        if movie_data.get('year'):
            self.title_label.setText(f"<h1>{movie_data['title']} ({movie_data['year']})</h1>")
        self.year_label = QLabel("")
        genre_label = QLabel(f"<h3>Gatunek: {movie_data['genre']}</h3>")
        added_by_label = QLabel(f"<b>Dodane przez:</b> {movie_data['added_by']}")

        # Informacje z API
        self.info_container = QWidget()
        info_layout = QVBoxLayout(self.info_container)

        self.plot_label = QLabel("<b>Opis:</b>")
        self.plot_text = QTextEdit()
        self.plot_text.setReadOnly(True)
        self.plot_text.setMaximumHeight(150)

        self.director_label = QLabel("<b>Reżyser:</b> Ładowanie...")
        self.actors_label = QLabel("<b>Obsada:</b> Ładowanie...")
        self.ratings_label = QLabel("<b>Oceny:</b> Ładowanie...")


        info_layout.addWidget(self.plot_label)
        info_layout.addWidget(self.plot_text)
        info_layout.addWidget(self.director_label)
        info_layout.addWidget(self.actors_label)
        info_layout.addWidget(self.ratings_label)


        right_layout.addWidget(self.title_label)
        right_layout.addWidget(self.year_label)
        right_layout.addWidget(genre_label)
        right_layout.addWidget(added_by_label)

        # Linia oddzielająca
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        right_layout.addWidget(separator)

        right_layout.addWidget(QLabel("<h3>Szczegóły z OMDb:</h3>"))
        right_layout.addWidget(self.info_container)
        right_layout.addStretch()

        # Przycisk zamknięcia
        close_button = QPushButton("Zamknij")
        close_button.clicked.connect(self.accept)
        right_layout.addWidget(close_button)

        # Dodanie paneli do głównego layoutu
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, 1)

        # Pobierz dane z OMDB API
        self.fetch_movie_data(movie_data['title'])

    def fetch_movie_data(self, title):
        try:
            url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={title}"
            response = requests.get(url)
            data = response.json()

            if data.get('Response') == 'True':

                year = data.get('Year', 'N/A')
                self.title_label.setText(f"<h1>{title} ({year})</h1>")

                self.plot_text.setText(data.get('Plot', 'Brak opisu'))
                self.director_label.setText(f"<b>Reżyser:</b> {data.get('Director', 'Nieznany')}")
                self.actors_label.setText(f"<b>Obsada:</b> {data.get('Actors', 'Nieznana')}")

                # Formatowanie ocen
                ratings_text = "<b>Oceny:</b><br>"
                for rating in data.get('Ratings', []):
                    ratings_text += f"• {rating['Source']}: {rating['Value']}<br>"
                if not data.get('Ratings'):
                    ratings_text += "Brak ocen"
                self.ratings_label.setText(ratings_text)

                # Pobieranie plakatu
                poster_url = data.get('Poster')
                if poster_url and poster_url != 'N/A':
                    self.load_poster(poster_url)
                else:
                    self.poster_label.setText("Brak plakatu")
                return year
            else:
                self.plot_text.setText("Nie znaleziono informacji o filmie w bazie OMDB.")
                self.director_label.setText("<b>Reżyser:</b> Brak danych")
                self.actors_label.setText("<b>Obsada:</b> Brak danych")
                self.ratings_label.setText("<b>Oceny:</b> Brak danych")
                self.poster_label.setText("Brak plakatu")
                return None

        except Exception as e:
            self.plot_text.setText(f"Błąd podczas pobierania danych: {str(e)}")
            self.director_label.setText("<b>Reżyser:</b> Błąd pobierania")
            self.actors_label.setText("<b>Obsada:</b> Błąd pobierania")
            self.ratings_label.setText("<b>Oceny:</b> Błąd pobierania")
            self.poster_label.setText("Błąd pobierania plakatu")
            return None

    def load_poster(self, url):
        """Pobiera i wyświetla plakat filmu"""
        try:
            response = requests.get(url)
            image_data = BytesIO(response.content)
            pixmap = QPixmap()
            pixmap.loadFromData(image_data.getvalue())
            scaled_pixmap = pixmap.scaled(
                self.poster_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.poster_label.setPixmap(scaled_pixmap)

        except Exception as e:
            self.poster_label.setText(f"Błąd ładowania plakatu:\n{str(e)}")


class MainWindow(QMainWindow):
    logout_success = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Movies Checker")
        self.setGeometry(100, 100, 1000, 600)

        self.logged_in_user_id = None

        try:
            self.setStyleSheet(open("style.qss", "r").read())
        except:
            print("Nie można znaleźć pliku style.qss - używam domyślnego stylu")

        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)

        self.left_panel = QWidget()
        self.left_panel.setFixedWidth(200)
        left_layout = QVBoxLayout(self.left_panel)

        self.btn_save_json = QPushButton("💾 Save to JSON")
        self.btn_load_json = QPushButton("📂 Load from JSON")
        self.btn_save_csv = QPushButton("💾 Save to CSV")
        self.btn_load_csv = QPushButton("📂 Load from CSV")

        left_layout.addWidget(self.btn_save_json)
        left_layout.addWidget(self.btn_load_json)
        left_layout.addWidget(self.btn_save_csv)
        left_layout.addWidget(self.btn_load_csv)
        left_layout.addStretch()

        self.btn_logout = QPushButton("🚪 Logout")
        left_layout.addWidget(self.btn_logout)

        self.center_panel = QWidget()
        center_layout = QVBoxLayout(self.center_panel)

        self.label_title = QLabel("🎬 Movies List")
        self.label_title.setObjectName("label_title")
        self.label_title.setStyleSheet("font-size: 30px; font-weight: bold;")

        self.table = QTableWidget(0, 4)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Title", "Year", "Genre", "Added by"])

        # Dynamiczna zmiana rozmiaru tabeli
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Automatyczna zmiana szerokości kolumn
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Automatyczna zmiana wysokości wierszy
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        # Zmiana proporcji przestrzeni w układzie
        center_layout.setStretch(0, 1)
        center_layout.setStretch(1, 5)

        self.table.setHorizontalHeaderLabels(["Title", "Year", "Genre", "Added by"])

        # Dwuklik dla wyświetlenia szczegółów
        self.table.cellDoubleClicked.connect(self.show_movie_details)

        center_layout.addWidget(self.label_title)
        center_layout.addWidget(self.table)

        # Informacja dla użytkownika
        info_label = QLabel("Kliknij dwukrotnie na film, aby zobaczyć szczegóły i plakat")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: #666; font-style: italic;")
        center_layout.addWidget(info_label)


        self.right_panel = QWidget()
        self.right_panel.setFixedWidth(250)
        right_layout = QVBoxLayout(self.right_panel)


        self.filter_panel = QWidget()
        filter_layout = QVBoxLayout(self.filter_panel)

        # Filtrowanie po gatunku
        self.filter_genre = QComboBox()
        self.filter_genre.addItem("All Genres")
        self.filter_genre.addItems([
            "Action", "Adventure", "Comedy", "Drama", "Horror", "Thriller",
            "Science Fiction", "Fantasy", "Romance", "Mystery", "Crime",
            "Superhero", "Musical", "Western", "War", "Animation", "Documentary"
        ])

        # Dodanie filtra sortowania
        self.filter_sort = QComboBox()
        self.filter_sort.addItem("Sort by Year: Ascending")
        self.filter_sort.addItem("Sort by Year: Descending")

        # Filtrowanie po roku
        self.filter_year = QLineEdit()
        self.filter_year.setPlaceholderText("Year (e.g. 2020 or 2010-2020)")

        # Przyciski filtrowania
        self.btn_apply_filter = QPushButton("🔍 Apply Filters")
        self.btn_apply_filter.clicked.connect(self.load_movies)
        self.btn_reset_filter = QPushButton("🔄 Reset")
        self.btn_reset_filter.clicked.connect(self.reset_filters)


        filter_layout.addWidget(QLabel("Filter by Genre:"))
        filter_layout.addWidget(self.filter_genre)
        filter_layout.addWidget(QLabel("Sort by Year:"))
        filter_layout.addWidget(self.filter_sort)
        filter_layout.addWidget(QLabel("Filter by Year:"))
        filter_layout.addWidget(self.filter_year)
        filter_layout.addWidget(self.btn_apply_filter)
        filter_layout.addWidget(self.btn_reset_filter)

        right_layout.addWidget(self.filter_panel)

        self.label_add_movie = QLabel("➕ Add Movie")
        self.label_add_movie.setAlignment(Qt.AlignCenter)

        self.input_title = QLineEdit()
        self.input_title.setPlaceholderText("Title")

        self.btn_add_movie = QPushButton("✅ Add Movie")
        self.btn_add_movie.clicked.connect(self.add_movie)
        self.btn_add_movie.setObjectName("btn_add_movie")

        self.btn_delete_movie = QPushButton("🗑️ Delete Selected")
        self.btn_delete_movie.clicked.connect(self.delete_movie)

        self.btn_export_pdf = QPushButton("📄 Export to PDF")
        self.btn_export_pdf.clicked.connect(self.export_to_pdf)

        right_layout.addWidget(self.label_add_movie)
        right_layout.addWidget(self.input_title)
        right_layout.addWidget(self.btn_add_movie)
        right_layout.addWidget(self.btn_delete_movie)
        right_layout.addWidget(self.btn_export_pdf)

        main_layout.addWidget(self.left_panel)
        main_layout.addWidget(self.center_panel, 1)
        main_layout.addWidget(self.right_panel)

        self.setCentralWidget(central_widget)

        QTimer.singleShot(0, self.load_movies)  # Wywołaj load_movies po załadowaniu GUI

        # Podłączenie przycisków do metod
        self.btn_logout.clicked.connect(self.logout)
        self.btn_save_json.clicked.connect(self.save_to_json)
        self.btn_load_json.clicked.connect(self.load_from_json)
        self.btn_save_csv.clicked.connect(self.save_to_csv)
        self.btn_load_csv.clicked.connect(self.load_from_csv)

    def get_movie_info_from_api(self, title):
        try:
            url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={title}"
            response = requests.get(url)
            data = response.json()

            if data.get('Response') == 'True':
                year = data.get('Year', 'N/A')
                genre = data.get('Genre', 'N/A')
                # kilka gatunków - brany jest pierwszy
                if ',' in genre:
                    genre = genre.split(',')[0].strip()

                return {'year': year, 'genre': genre}
            return {'year': 'N/A', 'genre': 'N/A'}
        except:
            return {'year': 'N/A', 'genre': 'N/A'}

    def show_movie_details(self, row, column):
        if row < 0:
            return

        title = self.table.item(row, 0).text()
        year = self.table.item(row, 1).text()
        genre = self.table.item(row, 2).text()
        added_by = self.table.item(row, 3).text()

        movie_data = {
            'title': title,
            'year': year,
            'genre': genre,
            'added_by': added_by
        }

        dialog = MovieDetailsDialog(movie_data, self)
        dialog.exec()

    def load_movies(self):
        self.table.setRowCount(0)
        conn = sqlite3.connect("movies.db")
        cursor = conn.cursor()

        # Pobierz wartości filtrów
        genre_filter = self.filter_genre.currentText()
        year_filter = self.filter_year.text()
        sort_order = self.filter_sort.currentText()

        print(f"Filtr gatunku: {genre_filter}")
        print(f"Filtr roku: {year_filter}")
        print(f"Porządek sortowania: {sort_order}")

        # Budowanie zapytania SQL
        query = "SELECT movies.title, movies.year, movies.genre, users.login FROM movies JOIN users ON movies.user_id = users.id"
        params = []

        conditions = []
        if genre_filter != "All Genres":
            conditions.append("movies.genre = ?")
            params.append(genre_filter)

        if year_filter:
            if "-" in year_filter:
                try:
                    start_year, end_year = map(int, year_filter.split("-"))
                    conditions.append("movies.year BETWEEN ? AND ?")
                    params.extend([start_year, end_year])
                except ValueError:
                    QMessageBox.warning(self, "Błąd", "Nieprawidłowy format zakresu lat! Użyj formatu YYYY-YYYY")
                    return
            else:
                try:
                    year = int(year_filter)
                    conditions.append("movies.year = ?")
                    params.append(year)
                except ValueError:
                    QMessageBox.warning(self, "Błąd", "Nieprawidłowy format roku!")
                    return

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # Dodajemy sortowanie
        if "Ascending" in sort_order:
            query += " ORDER BY movies.year ASC"
        elif "Descending" in sort_order:
            query += " ORDER BY movies.year DESC"

        print(f"Zapytanie SQL: {query}")
        cursor.execute(query, tuple(params))
        movies = cursor.fetchall()
        conn.close()

        if not movies:
            QMessageBox.information(self, "Brak wyników", "Brak filmów spełniających kryteria!")

        for row, (title, year, genre, added_by) in enumerate(movies):
            self.table.insertRow(row)

            for col, data in enumerate([title, str(year), genre, added_by]):
                item = QTableWidgetItem(data)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

    def reset_filters(self):
        self.filter_genre.setCurrentIndex(0)  # Ustawienie domyślnego filtra gatunku (All Genres)
        self.filter_year.clear()  # Czyszczenie pola roku
        self.filter_sort.setCurrentIndex(0)  # Ustawienie domyślnego porządku sortowania (Ascending)
        self.load_movies()

    def add_movie(self):
        title = self.input_title.text()

        if not title:
            QMessageBox.warning(self, "Error", "Title must be filled!")
            return

        movie_info = self.get_movie_info_from_api(title)
        year = movie_info['year']
        genre = movie_info['genre']

        if year == 'N/A' or genre == 'N/A':
            response = QMessageBox.question(self, "Brak informacji o filmie",
                                            "Nie udało się automatycznie pobrać informacji o tym filmie. Czy chcesz dodać film bez tych informacji?",
                                            QMessageBox.Yes | QMessageBox.No)

            if response == QMessageBox.No:
                return

            if year == 'N/A':
                year = 0
            if genre == 'N/A':
                genre = "Unknown"

        # Pobierz ID zalogowanego użytkownika
        logged_in_user_id = self.logged_in_user_id

        conn = sqlite3.connect("movies.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO movies (title, year, genre, user_id) VALUES (?, ?, ?, ?)",
                       (title, year, genre, logged_in_user_id))
        conn.commit()
        conn.close()

        self.load_movies()
        self.input_title.clear()

        QMessageBox.information(self, "Film dodany",
                                f"Film '{title}' został dodany do bazy danych.\n\nRok: {year}\nGatunek: {genre}")

        self.check_movie_poster(title)

    def check_movie_poster(self, title):
        try:
            url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={title}"
            response = requests.get(url)
            data = response.json()

            if data.get('Response') == 'True' and data.get('Poster') != 'N/A':
                QMessageBox.information(self, "Plakat dostępny",
                                        f"Plakat dla filmu '{title}' został znaleziony w bazie OMDB. "
                                        f"Możesz zobaczyć go klikając dwukrotnie na film w tabeli.")
        except:
            pass

    def delete_movie(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "No movie selected!")
            return

        title = self.table.item(selected_row, 0).text()
        conn = sqlite3.connect("movies.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM movies WHERE title = ?", (title,))
        conn.commit()
        conn.close()

        self.load_movies()

    def export_to_pdf(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
        if not file_name:
            return

        # Pobierz aktywne filtry
        genre_filter = self.filter_genre.currentText()
        year_filter = self.filter_year.text()
        sort_order = self.filter_sort.currentText()

        # Utwórz tytuł raportu na podstawie zastosowanych filtrów
        report_title = "Movies List"
        filter_details = []

        if genre_filter != "All Genres":
            filter_details.append(f"Genre: {genre_filter}")
        if year_filter:
            filter_details.append(f"Year: {year_filter}")
        if sort_order:
            filter_details.append(f"Sorted: {sort_order}")

        if filter_details:
            report_subtitle = " | ".join(filter_details)
        else:
            report_subtitle = "All Movies"

        pdf = canvas.Canvas(file_name)
        pdf.setTitle(f"Movies Report - {report_subtitle}")

        # Czcionki i nagłówek
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(100, 800, report_title)

        pdf.setFont("Helvetica", 12)
        pdf.drawString(100, 780, report_subtitle)

        # Data raportu
        from datetime import datetime
        now = datetime.now()
        pdf.drawString(100, 750, f"Generated: {now.strftime('%Y-%m-%d %H:%M')}")

        # Linia oddzielająca
        pdf.line(100, 740, 500, 740)

        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(100, 720, "Title")
        pdf.drawString(300, 720, "Year")
        pdf.drawString(350, 720, "Genre")
        pdf.drawString(450, 720, "Added by")

        pdf.line(100, 710, 500, 710)

        pdf.setFont("Helvetica", 10)
        y = 690

        total_movies = self.table.rowCount()

        if total_movies == 0:
            pdf.drawString(100, y, "No movies found matching the filter criteria.")
            y -= 20
        else:
            for row in range(total_movies):
                if y < 100:
                    pdf.showPage()
                    pdf.setFont("Helvetica-Bold", 12)
                    pdf.drawString(100, 800, f"{report_title} (continued)")
                    pdf.setFont("Helvetica", 10)
                    y = 780

                title = self.table.item(row, 0).text()
                year = self.table.item(row, 1).text()
                genre = self.table.item(row, 2).text()
                added_by = self.table.item(row, 3).text()

                # Skrócenie za długich tytułów
                if len(title) > 25:
                    title = title[:22] + "..."

                pdf.drawString(100, y, title)
                pdf.drawString(300, y, year)
                pdf.drawString(350, y, genre)
                pdf.drawString(450, y, added_by)

                y -= 20

        pdf.line(100, y, 500, y)
        y -= 20
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(100, y, f"Total movies: {total_movies}")

        # Zapisz PDF
        pdf.save()
        QMessageBox.information(self, "Success",
                                f"PDF Exported Successfully!\nSaved {total_movies} movies to {file_name}")

    def logout(self):
        self.close()
        self.logout_success.emit()

    def save_to_json(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save to JSON", "", "JSON Files (*.json)")
        if not file_name:
            return

        conn = sqlite3.connect("movies.db")
        cursor = conn.cursor()
        cursor.execute("SELECT title, year, genre FROM movies")
        movies = cursor.fetchall()
        conn.close()

        movies_list = [{"title": title, "year": year, "genre": genre} for title, year, genre in movies]

        try:
            with open(file_name, 'w') as f:
                json.dump(movies_list, f, indent=4)
            QMessageBox.information(self, "Success", "Data saved to JSON successfully.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error saving JSON: {str(e)}")

    def load_from_json(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Load from JSON", "", "JSON Files (*.json)")
        if not file_name:
            return

        try:
            with open(file_name, 'r') as f:
                movies_list = json.load(f)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading JSON: {str(e)}")
            return

        if not movies_list or not isinstance(movies_list, list):
            QMessageBox.warning(self, "Error", "Invalid JSON file format. Expected a list of movies.")
            return

        # Okno postępu
        progress = QMessageBox(self)
        progress.setWindowTitle("Importing movies")
        progress.setText("Fetching movie details from OMDb API...\nThis may take a moment.")
        progress.setStandardButtons(QMessageBox.NoButton)
        progress.show()
        QApplication.processEvents()

        conn = sqlite3.connect("movies.db")
        cursor = conn.cursor()

        added = 0
        skipped = 0
        errors = 0

        for i, movie in enumerate(movies_list):
            # Informację o postępie co 5 filmów
            if i % 5 == 0:
                progress.setText(f"Fetching movie details from OMDb API...\nProcessed {i}/{len(movies_list)} movies")
                QApplication.processEvents()

            if isinstance(movie, dict):
                title = movie.get("title", None)
            elif isinstance(movie, str):
                title = movie
            else:
                errors += 1
                continue

            if not title:
                errors += 1
                continue

            movie_info = self.get_movie_info_from_api(title)
            year = movie_info['year']
            genre = movie_info['genre']

            try:
                if year != 'N/A':
                    year = int(year)
                else:
                    year = 0
            except ValueError:
                year = 0

            if genre == 'N/A':
                genre = "Unknown"

            # Sprawdzanie czy film już nie istnieje
            cursor.execute("SELECT * FROM movies WHERE title=? AND year=?", (title, year))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO movies (title, year, genre, user_id) VALUES (?, ?, ?, ?)",
                               (title, year, genre, self.logged_in_user_id or 1))
                added += 1
            else:
                skipped += 1

        conn.commit()
        conn.close()

        progress.close()

        self.load_movies()
        QMessageBox.information(self, "Import Complete",
                                f"Added {added} new movies.\nSkipped {skipped} duplicates.\nErrors: {errors}")

    def save_to_csv(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save to CSV", "", "CSV Files (*.csv)")
        if not file_name:
            return

        conn = sqlite3.connect("movies.db")
        cursor = conn.cursor()
        cursor.execute("SELECT title, year, genre FROM movies")
        movies = cursor.fetchall()
        conn.close()

        try:
            with open(file_name, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["title", "year", "genre"])
                writer.writerows(movies)
            QMessageBox.information(self, "Success", "Data saved to CSV successfully.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error saving CSV: {str(e)}")

    def load_from_csv(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Load from CSV", "", "CSV Files (*.csv)")
        if not file_name:
            return

        try:
            with open(file_name, 'r', newline='') as f:
                sample = f.read(1024)
                f.seek(0)

                dialect = csv.Sniffer().sniff(sample)
                has_header = csv.Sniffer().has_header(sample)

                reader = csv.reader(f, dialect)

                if has_header:
                    headers = next(reader)
                    title_index = 0

                    for i, header in enumerate(headers):
                        if header.lower() in ['title', 'tytuł', 'nazwa']:
                            title_index = i
                            break
                else:
                    title_index = 0

                movies_list = []
                for row in reader:
                    if len(row) > title_index:
                        movies_list.append(row[title_index].strip())
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading CSV: {str(e)}")
            return

        if not movies_list:
            QMessageBox.warning(self, "Error", "No movies found in the CSV file.")
            return

        progress = QMessageBox(self)
        progress.setWindowTitle("Importing movies")
        progress.setText("Fetching movie details from OMDb API...\nThis may take a moment.")
        progress.setStandardButtons(QMessageBox.NoButton)
        progress.show()
        QApplication.processEvents()

        conn = sqlite3.connect("movies.db")
        cursor = conn.cursor()

        added = 0
        skipped = 0
        errors = 0

        for i, title in enumerate(movies_list):
            if i % 5 == 0:
                progress.setText(f"Fetching movie details from OMDb API...\nProcessed {i}/{len(movies_list)} movies")
                QApplication.processEvents()

            if not title:
                errors += 1
                continue

            movie_info = self.get_movie_info_from_api(title)
            year = movie_info['year']
            genre = movie_info['genre']

            try:
                if year != 'N/A':
                    year = int(year)
                else:
                    year = 0
            except ValueError:
                year = 0

            if genre == 'N/A':
                genre = "Unknown"

            cursor.execute("SELECT * FROM movies WHERE title=? AND year=?", (title, year))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO movies (title, year, genre, user_id) VALUES (?, ?, ?, ?)",
                               (title, year, genre, self.logged_in_user_id or 1))
                added += 1
            else:
                skipped += 1

        conn.commit()
        conn.close()

        progress.close()

        self.load_movies()
        QMessageBox.information(self, "Import Complete",
                                f"Added {added} new movies.\nSkipped {skipped} duplicates.\nErrors: {errors}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())