import sys
import sqlite3
import json
import csv
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog, QComboBox
)
from PySide6.QtCore import Qt, Signal
from reportlab.pdfgen import canvas


class MainWindow(QMainWindow):
    logout_success = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Movies Checker")
        self.setGeometry(100, 100, 1000, 600)
        self.setStyleSheet(open("style.qss", "r").read())

        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)

        # --- Lewy panel (Nawigacja) ---
        self.left_panel = QWidget()
        self.left_panel.setFixedWidth(200)
        left_layout = QVBoxLayout(self.left_panel)

        # Przyciski do obsługi danych
        self.btn_save_json = QPushButton("Save to JSON")
        self.btn_load_json = QPushButton("Load from JSON")
        self.btn_save_csv = QPushButton("Save to CSV")
        self.btn_load_csv = QPushButton("Load from CSV")

        left_layout.addWidget(self.btn_save_json)
        left_layout.addWidget(self.btn_load_json)
        left_layout.addWidget(self.btn_save_csv)
        left_layout.addWidget(self.btn_load_csv)
        left_layout.addStretch()


        self.btn_logout = QPushButton("Logout")


        left_layout.addWidget(self.btn_logout)

        # --- Centralna część (Tabela) ---
        self.center_panel = QWidget()
        center_layout = QVBoxLayout(self.center_panel)

        # --- Filtry ---
        self.filter_panel = QWidget()
        filter_layout = QHBoxLayout(self.filter_panel)

        # Filtrowanie po gatunku
        self.filter_genre = QComboBox()
        self.filter_genre.addItem("All Genres")
        self.filter_genre.addItems([
            "Action", "Adventure", "Comedy", "Drama", "Horror", "Thriller",
            "Science Fiction (Sci-Fi)", "Fantasy", "Romance", "Mystery", "Crime",
            "Superhero", "Musical", "Western", "War", "Animation", "Documentary"
        ])

        # Filtrowanie po roku
        self.filter_year = QLineEdit()
        self.filter_year.setPlaceholderText("Year (e.g. 2020 or 2010-2020)")

        # Przyciski filtrowania
        self.btn_apply_filter = QPushButton("Apply Filters")
        self.btn_apply_filter.clicked.connect(self.load_movies)
        self.btn_reset_filter = QPushButton("Reset")
        self.btn_reset_filter.clicked.connect(self.reset_filters)

        filter_layout.addWidget(QLabel("Filter by:"))
        filter_layout.addWidget(self.filter_genre)
        filter_layout.addWidget(self.filter_year)
        filter_layout.addWidget(self.btn_apply_filter)
        filter_layout.addWidget(self.btn_reset_filter)

        self.label_title = QLabel("Movies List")
        self.label_title.setStyleSheet("font-size: 20px; font-weight: bold;")

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Title", "Year", "Genre"])
        self.load_movies()

        center_layout.addWidget(self.label_title)
        center_layout.addWidget(self.filter_panel)
        center_layout.addWidget(self.table)

        # --- Prawy panel (Formularz) ---
        self.right_panel = QWidget()
        self.right_panel.setFixedWidth(250)
        right_layout = QVBoxLayout(self.right_panel)

        self.label_add_movie = QLabel("Add Movie")
        self.label_add_movie.setAlignment(Qt.AlignCenter)

        self.input_title = QLineEdit()
        self.input_title.setPlaceholderText("Title")
        self.input_year = QLineEdit()
        self.input_year.setPlaceholderText("Year")

        self.input_genre = QComboBox()
        self.input_genre.setPlaceholderText("Genre")
        self.input_genre.addItems([
            "Action", "Adventure", "Comedy", "Drama", "Horror", "Thriller",
            "Science Fiction (Sci-Fi)", "Fantasy", "Romance", "Mystery", "Crime",
            "Superhero", "Musical", "Western", "War", "Animation", "Documentary"
        ])

        self.btn_add_movie = QPushButton("Add Movie")
        self.btn_add_movie.clicked.connect(self.add_movie)

        self.btn_delete_movie = QPushButton("Delete Selected")
        self.btn_delete_movie.clicked.connect(self.delete_movie)

        self.btn_export_pdf = QPushButton("Export to PDF")
        self.btn_export_pdf.clicked.connect(self.export_to_pdf)

        right_layout.addWidget(self.label_add_movie)
        right_layout.addWidget(self.input_title)
        right_layout.addWidget(self.input_year)
        right_layout.addWidget(self.input_genre)
        right_layout.addWidget(self.btn_add_movie)
        right_layout.addWidget(self.btn_delete_movie)
        right_layout.addWidget(self.btn_export_pdf)

        main_layout.addWidget(self.left_panel)
        main_layout.addWidget(self.center_panel, 1)
        main_layout.addWidget(self.right_panel)

        self.setCentralWidget(central_widget)

        # Podłączenie przycisków do metod
        self.btn_logout.clicked.connect(self.logout)
        self.btn_save_json.clicked.connect(self.save_to_json)
        self.btn_load_json.clicked.connect(self.load_from_json)
        self.btn_save_csv.clicked.connect(self.save_to_csv)
        self.btn_load_csv.clicked.connect(self.load_from_csv)

    def load_movies(self):
        self.table.setRowCount(0)
        conn = sqlite3.connect("movies.db")
        cursor = conn.cursor()

        # Pobierz wartości filtrów
        genre_filter = self.filter_genre.currentText()
        year_filter = self.filter_year.text()

        # Buduj zapytanie SQL
        query = "SELECT title, year, genre FROM movies"
        params = []

        conditions = []
        if genre_filter != "All Genres":
            conditions.append("genre = ?")
            params.append(genre_filter)

        if year_filter:
            if "-" in year_filter:
                try:
                    start_year, end_year = map(int, year_filter.split("-"))
                    conditions.append("year BETWEEN ? AND ?")
                    params.extend([start_year, end_year])
                except:
                    QMessageBox.warning(self, "Error", "Invalid year range format! Use YYYY-YYYY")
                    return
            else:
                try:
                    year = int(year_filter)
                    conditions.append("year = ?")
                    params.append(year)
                except:
                    QMessageBox.warning(self, "Error", "Invalid year format!")
                    return

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        cursor.execute(query, params)
        movies = cursor.fetchall()
        conn.close()

        for row, (title, year, genre) in enumerate(movies):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(title))
            self.table.setItem(row, 1, QTableWidgetItem(str(year)))
            self.table.setItem(row, 2, QTableWidgetItem(genre))

    def reset_filters(self):
        self.filter_genre.setCurrentIndex(0)
        self.filter_year.clear()
        self.load_movies()

    def add_movie(self):
        title = self.input_title.text()
        year = self.input_year.text()
        genre = self.input_genre.currentText()

        if not title or not year or not genre:
            QMessageBox.warning(self, "Error", "All fields must be filled!")
            return

        conn = sqlite3.connect("movies.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO movies (title, year, genre) VALUES (?, ?, ?)", (title, year, genre))
        conn.commit()
        conn.close()

        self.load_movies()
        self.input_title.clear()
        self.input_year.clear()
        self.input_genre.setCurrentIndex(0)

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

        pdf = canvas.Canvas(file_name)
        pdf.setFont("Helvetica", 12)
        pdf.drawString(200, 800, "Movies List")

        y = 750
        for row in range(self.table.rowCount()):
            title = self.table.item(row, 0).text()
            year = self.table.item(row, 1).text()
            genre = self.table.item(row, 2).text()
            pdf.drawString(100, y, f"{title} ({year}) - {genre}")
            y -= 20

        pdf.save()
        QMessageBox.information(self, "Success", "PDF Exported Successfully!")

    def logout(self):
        self.close()
        self.logout_success.emit()

    def save_to_json(self):
        """Zapisuje listę filmów do pliku JSON"""
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
        """Wczytuje filmy z pliku JSON"""
        file_name, _ = QFileDialog.getOpenFileName(self, "Load from JSON", "", "JSON Files (*.json)")
        if not file_name:
            return

        try:
            with open(file_name, 'r') as f:
                movies_list = json.load(f)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading JSON: {str(e)}")
            return

        conn = sqlite3.connect("movies.db")
        cursor = conn.cursor()

        added = 0
        duplicates = 0
        for movie in movies_list:
            # Sprawdź czy film już istnieje
            cursor.execute("SELECT * FROM movies WHERE title=? AND year=?",
                         (movie["title"], movie["year"]))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO movies (title, year, genre) VALUES (?, ?, ?)",
                              (movie["title"], movie["year"], movie["genre"]))
                added += 1
            else:
                duplicates += 1

        conn.commit()
        conn.close()
        self.load_movies()
        QMessageBox.information(self, "Import Complete",
                               f"Added {added} new movies. Skipped {duplicates} duplicates.")

    def save_to_csv(self):
        """Zapisuje listę filmów do pliku CSV"""
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
        """Wczytuje filmy z pliku CSV"""
        file_name, _ = QFileDialog.getOpenFileName(self, "Load from CSV", "", "CSV Files (*.csv)")
        if not file_name:
            return

        try:
            with open(file_name, 'r', newline='') as f:
                reader = csv.DictReader(f)
                movies_list = list(reader)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading CSV: {str(e)}")
            return

        conn = sqlite3.connect("movies.db")
        cursor = conn.cursor()

        added = 0
        duplicates = 0
        for row in movies_list:
            try:
                year = int(row["year"])
            except ValueError:
                continue  # Pomijaj nieprawidłowe lata

            cursor.execute("SELECT * FROM movies WHERE title=? AND year=?",
                         (row["title"], year))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO movies (title, year, genre) VALUES (?, ?, ?)",
                              (row["title"], year, row["genre"]))
                added += 1
            else:
                duplicates += 1

        conn.commit()
        conn.close()
        self.load_movies()
        QMessageBox.information(self, "Import Complete",
                               f"Added {added} new movies. Skipped {duplicates} duplicates.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())