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
        """Konvertiert Date String in ISO 8601 Format mit UTC-Timezone.
        
        Args:
            date_string: Date string from CSV (Format: "YYYY-MM-DD HH:MM:SS" oder ISO)
        
        Returns:
            ISO 8601 formatted date string with UTC timezone
        """
        try:
            # Versuche direktes ISO-Format-Parsing (für synthetische Daten)
            if 'T' in date_string and ('+' in date_string or 'Z' in date_string):
                # Bereits im ISO-Format
                return date_string.strip()
            
            # Parse standard date format (für Original-Daten)
            dt = datetime.strptime(date_string.strip(), "%Y-%m-%d %H:%M:%S")
            dt_utc = dt.replace(tzinfo=timezone.utc)
            return dt_utc.isoformat()
        except Exception:
            # Fallback: Aktuelles Datum bei Parsing-Fehler
            return datetime.now(timezone.utc).isoformat()

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
