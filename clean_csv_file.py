import re
import pandas as pd
from datetime import datetime, timezone


class CSVloader:
    """
    Lädt und bereinigt eine CSV-Datei mit Feedback-Daten.
    Erwartete Spalten: NPS, Market, Date, Verbatim
    """

    def __init__(self, path, encoding) -> None:
        """
        Initialisiert den CSVloader mit dem Pfad zur CSV-Datei und der Kodierung.
        """
        self.path = path
        self.encoding = encoding

    @staticmethod
    def clean_csv_line(line) -> str:
        """
        Cleans a line from a CSV file by removing BOM, outer quotes/semicolons, and double quotes.

        Args:
            line (str): A line from a CSV file.

        Returns:
            str: The cleaned line.
        """
        # Removes BOM, outer quotes/semicolons, and double quotes
        pattern = r'^\ufeff?[";]*|[";]*$|""([^"]*)""|"([^"]*)"'

        def replace_func(match) -> str:
            if match.group(1):  # Double quotes
                return match.group(1)
            elif match.group(2):  # Single quotes
                return match.group(2)
            else:  # BOM or end character
                return ""

        return re.sub(pattern, replace_func, line).strip()

    @staticmethod
    def to_iso_format(date_string: str) -> str:
        """Konvertiert Spalte Date in ISO 8601 Format: 2022-09-09T00:00:00Z."""
        date_string = "2022-09-09 00:00:00"
        dt = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        dt_utc = dt.replace(tzinfo=timezone.utc)
        iso_format = dt_utc.isoformat()
        return iso_format

    @staticmethod
    def remove_null_values(df: pd.DataFrame) -> pd.DataFrame:
        """
        Entfernt Zeilen und Spalten mit Nullwerten aus dem DataFrame.
        """
        df = df.dropna(axis=1)  # Entfernt Spalten mit Nullwerten
        df = df.dropna(axis=0)  # Entfernt Zeilen mit Nullwerten
        return df

    def load_csv(self) -> pd.DataFrame:
        """Load a CSV file and return a DataFrame.

        Args:
            path (str): The path to the CSV file.
            encoding (str, optional): The encoding of the CSV file. Defaults to 'utf-8'.

        Returns:
            pd.DataFrame: A DataFrame containing the cleaned CSV data.
        """
        with open(self.path, encoding=self.encoding) as file:
            data = {"NPS": [], "Market": [], "Date": [], "Verbatim": []}

            for line_num, line in enumerate(file):
                if line_num == 0:
                    continue
                cleaned_line = CSVloader.clean_csv_line(line).split(",")
                data["NPS"].append(cleaned_line[0])
                data["Market"].append(cleaned_line[1])
                data["Date"].append(CSVloader.to_iso_format(cleaned_line[2]))
                data["Verbatim"].append(cleaned_line[3])

            # Remove null values
            data = CSVloader.remove_null_values(pd.DataFrame(data))

        return data
