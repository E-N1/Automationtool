import re
import os
import sys
import random
import string
import threading
import webbrowser
import time
import datetime as dt
from threading import Event


from Configurations.machines import Machines
from Configurations.networkshare import NetworkShare
from Configurations.read_fault import ReadFault
from Configurations.read_counted_testcase import ReadCountedTestcase
from Configurations.read_categories_qtp_test import ReadCategories
from Configurations.read_timecontroll import ReadTimecontroll

from Logic.tc_analyzer import TestCaseAnalyzer
from Logic.file_watcher import FileWatcher
from Logic.access_db_reader import AccessDBReader

from bs4 import BeautifulSoup # HTML div id parsen

class HTMLData:

    def __init__(self):
        self.stop_event = Event()
        self.reportTemplatePath = "./Resources/Logfiles_Template/html_reportertemplate.html"
        self.logfileTemplatePath = "./Resources/Logfiles_Template/html_logfiletemplate.html"
        self.reporterHTML = "_reporter.html"
      
        # Configurations
        self.machines = Machines()
        self.networkShare = NetworkShare()
        self.readCountedTestcase = ReadCountedTestcase()
        self.readCategoriesQTP = ReadCategories()
        self.readTimeControll = ReadTimecontroll()

        # Logic
        self.readFault = ReadFault()
        self.accesDBReader = AccessDBReader()
        self.tcAnalyzer = TestCaseAnalyzer()
        self.machineErrorStar = self.readFault.errorList[0] # .*. 
        self.machineErrorPlus = self.readFault.errorList[1] # .+.
        self.machineErrorF = self.readFault.errorList[2] # .F.
        self.machineRightH = self.readFault.errorList[3] # .H.

        self.progressBarIDMachines = {} 
        self.randomStrings = {}
        self.currentTCCategure = {}
        self.file_watchers = {}
        self.found_categories = set()
        self.current_file_watcher = None


    def getProgressBar(self,progress_bar_id):
        """
        Generates HTML for a progress bar with the specified ID.

        Args:
            progress_bar_id (str): The ID to assign to the progress bar element.

        Returns:
            str: A string containing the HTML for the progress bar.
        """
        progress_bar_html_body = ( 
            "<div class='progress-container'>\n"
            "<span class='progress-bar-digit'>0%</span>\n"
            "<div class='progress-bar-container'>\n"
            f"<div class='progress-bar' id={progress_bar_id} style='width: 0%;'>0%</div></div>\n"
            "<span class='progress-bar-digit'>100%</span></div>\n"
        )
        return progress_bar_html_body


    def generateHTMLFilesforMachine(self, machine, category=None, currentStateTC=None):
        """
        Generates HTML files for a given machine, including error charts and progress bars.
        Args:
            machine (str): The name of the machine for which the HTML files are generated.
            category (str, optional): The category of errors to be included. Defaults to None.
            currentStateTC (int, optional): The current state test case number. Defaults to None.
        This method performs the following steps:
            1. Reads the overview of the machine's faults.
            2. Initializes internal data structures and variables.
            3. Retrieves the current version of the machine's module.
            4. Fetches categories and errors for the machine.
            5. Collects data and creates HTML error files for each category.
            6. Reads the HTML template content.
            7. Generates JavaScript code for Google Charts based on the collected data.
            8. Constructs HTML table rows for each category.
            9. Replaces placeholders in the template with generated content.
            10. Writes the final HTML content to a file.
        The generated HTML files include interactive pie charts for error visualization and progress bars indicating the current state.
        """
        
        self.readFault.readOverview(machine)
        self.dictOfMachines = {machine: {}}
        all_internal_script = ""
        all_internal_table = "<tr>"
        all_internal_script_prozessbar = ""
        internal_counter = 0
        if currentStateTC is None:
            currentStateTC = 0

        modul = self.readFault.getCurrentVersionMachine(machine, modulOption=True)
        self.readCategoriesQTP.getCategories(machine, modul)
        print(self.readCategoriesQTP.getCategories(machine, modul))
        for category in self.readCategoriesQTP.categories[machine][modul]:
            for pattern in self.readFault.errorList:
                self.readFault.getErrorsForPattern(machine, category, pattern)
                self.collectDataForHTML(machine, category)
                self.createHTMLErrorFiles(machine, category)

        with open(self.reportTemplatePath, "r") as f:
            template_content = f.read()

        for category in self.dictOfMachines[machine]:
            data_dict = self.dictOfMachines[machine][category]
            internal_stardata = data_dict.get(".*.", 0)
            internal_plusdata = data_dict.get(".+.", 0)
            internal_fdata = data_dict.get(".F.", 0)
            internal_hdata = data_dict.get(".H.", 0)

            if category not in self.randomStrings or not self.randomStrings[category]:
                randomStringFunction = "XYZ" + self.getRandom(10)
                randomStringChartdiagram = self.getRandom(10)
                randomStringProgressbar = self.getRandom(10)
                self.randomStrings[category] = {
                    "randomStringFunction": randomStringFunction,
                    "randomStringChartdiagram": randomStringChartdiagram,
                    "randomStringProgressbar": randomStringProgressbar,
                }
            else:
                randomStringFunction = self.getRandomStringForCategory(category, "randomStringFunction")
                randomStringChartdiagram = self.getRandomStringForCategory(category, "randomStringChartdiagram")
                randomStringProgressbar = self.getRandomStringForCategory(category, "randomStringProgressbar")

            internal_script = (
                f"<!-- START DATA BLOCK FOR: {machine}_{category}-->\n"
                f"google.charts.setOnLoadCallback({randomStringFunction});\n"
                f"function {randomStringFunction}() {{\n"
                "var data = new google.visualization.DataTable();\n"
                "data.addColumn('string', 'Fehlercode');\n"
                "data.addColumn('number', 'Anzahl');\n"
                "data.addRows([\n"
                f"['.*.', {internal_stardata}],\n"
                f"['.+.', {internal_plusdata}],\n"
                f"['.F.', {internal_fdata}],\n"
                f"['.H.', {internal_hdata}],\n"
                "]);\n"
                "var options = {\n"
                f"title: '{machine} - {category} Auszug',\n"
                "colors: ['#FF0000', '#0000FF', '#DA70D6', '#32CD32'],\n"
                "titleTextStyle: { fontSize: 18, bold: true },\n"
                "legend: { position: 'right', textStyle: { fontSize: 16, bold: true } },\n"
                "chartArea: { width: '80%', height: '70%' },\n"
                "pieSliceTextStyle: { fontSize: 14 },\n"
                "};\n"
                f"var chart = new google.visualization.PieChart(document.getElementById('{randomStringChartdiagram}'));\n"
                "chart.draw(data, options);\n"
                "google.visualization.events.addListener(chart, 'select', function() {\n"
                "var selectedItem = chart.getSelection()[0];\n"
                "if (selectedItem) {\n"
                "var topping = data.getValue(selectedItem.row, 0);\n"
                "var url;\n"
                f"if (topping === '.*.') {{ url = './Logfiles_Errors/{machine}_{category}_star.html'; }}\n"
                f"else if (topping === '.+.') {{ url = './Logfiles_Errors/{machine}_{category}_plus.html'; }}\n"
                f"else if (topping === '.F.') {{ url = './Logfiles_Errors/{machine}_{category}_f.html'; }}\n"
                f"else if (topping === '.H.') {{ url = './Logfiles_Errors/{machine}_{category}_h.html'; }}\n"
                "window.open(url, '_blank');\n"
                "}\n"
                "});\n"
                "}\n"
                f"<!-- END DATA BLOCK FOR: {machine}_{category}-->\n"
            )
            all_internal_script += internal_script
            all_internal_script_prozessbar += "{id:"+f"'{randomStringProgressbar}'"+", progress: "f"{currentStateTC}"" },\n"
        
            if internal_counter == 4:
                all_internal_table += "</tr>\n<tr>"
                internal_counter = 1
            else:
                internal_counter += 1

            all_internal_table += (
                f"\n<!-- START DATA SPAN CLASS: {machine}_{category}-->\n"
                "<td style='border: 1px solid #00772c;'>\n"
                f"<div id={randomStringChartdiagram} style='width: 400px; height: 300px;'></div>\n"
                f"<div class='current-state'>\n"
                f"<span class = 'current-state-digit'>Testfall: </span>\n"
                f"</div>\n"
                f"{self.getProgressBar(randomStringProgressbar)}</td>\n"
                f"<!-- END DATA SPAN CLASS: {machine}_{category}-->\n"
            )

        all_internal_table += "</tr>"

        template_content = template_content.replace("[!!SCRIPTHERE!!]", all_internal_script)
        template_content = template_content.replace("[!!INFOPFAD!!]", self.readFault.getVersionPath(machine))
        template_content = template_content.replace("[!!TABLEHERE!!]", all_internal_table)
        template_content = template_content.replace("[!!NameOfMasch!!]", machine)
        template_content = template_content.replace("[!!PROGRESSBARDATA!!]", all_internal_script_prozessbar)

        with open(f"{os.getenv("REPORTER_PATH")}" + "\\" + f"{machine + self.reporterHTML}", "w") as f:
            f.write(template_content)


    def getRandomStringForCategory(self, category, key):
        """
        Retrieve a random string for a given category and key.
        Args:
            category (str): The category to look up.
            key (str): The key within the category to look up.
        Returns:
            str or None: The random string associated with the given category and key,
                         or None if the category or key does not exist.
        """
        return self.randomStrings.get(category, {}).get(key, None)


    def collectDataForHTML(self, machine, category):
        """
        Collects error data for a specified machine and category and stores it in the dictOfMachines attribute.

        Args:
            machine (str): The name or identifier of the machine.
            category (str): The category of errors to collect data for.

        The method updates the dictOfMachines attribute with the count of errors for different patterns:
            - ".*.": Errors matching the machineErrorStar pattern.
            - ".+.": Errors matching the machineErrorPlus pattern.
            - ".F.": Errors matching the machineErrorF pattern.
            - ".H.": Errors matching the machineRightH pattern.

        If the machine is not already in dictOfMachines, it initializes an empty dictionary for that machine.
        """
        if machine not in self.dictOfMachines:
            self.dictOfMachines[machine] = {}
        self.dictOfMachines[machine][category] = {
            ".*.": len(self.readFault.getErrorsForPattern(machine, category, pattern=self.machineErrorStar)),
            ".+.": len(self.readFault.getErrorsForPattern(machine, category, pattern=self.machineErrorPlus)),
            ".F.": len(self.readFault.getErrorsForPattern(machine, category, pattern=self.machineErrorF)),
            ".H.": len(self.readFault.getErrorsForPattern(machine, category, pattern=self.machineRightH))
        }


    def createHTMLErrorFiles(self, machine, category):
        """
        Generates HTML error files for a specified machine and error category.
        This method reads error messages from a predefined dictionary and uses a template
        to create HTML files for different types of errors (star, plus, f, h). The generated
        HTML files are saved in the specified error reporter path.
        Args:
            machine (str): The name of the machine for which the error files are being created.
            category (str): The category of errors to be processed.
        Raises:
            FileNotFoundError: If the template file specified by `self.logfileTemplatePath` does not exist.
            IOError: If there is an error reading the template file or writing the HTML files.
        """

        path = "./Resources/Logfiles_Errors/"
        os.makedirs(path, exist_ok=True)

        machine_errors = self.readFault.dictMachineErrors.get(machine, {})
        starFilePath = f"{os.getenv("ERROR_REPORTER_PATH")}\\{machine.lower()}_{category}_star.html"
        plusFilePath = f"{os.getenv("ERROR_REPORTER_PATH")}\\{machine.lower()}_{category}_plus.html"
        fFilePath = f"{os.getenv("ERROR_REPORTER_PATH")}\\{machine.lower()}_{category}_f.html"
        hFilePath = f"{os.getenv("ERROR_REPORTER_PATH")}\\{machine.lower()}_{category}_h.html"

        
        with open(self.logfileTemplatePath, "r") as f:
            template_content = f.read()

        logsHereScript = "[!!LOGS-HERE!!]"
        nameOfMaschScript = "[!!NameOfMasch!!]"
        errorScript = "[!!Error!!]"
        categoryScript = "[[!!Category!!]]"
        content_star = template_content
        content_plus = template_content
        content_f = template_content
        content_h = template_content

        if category in machine_errors:
            category_errors = machine_errors[category]

            if self.machineErrorStar in category_errors:
                error_messages = category_errors[self.machineErrorStar]
                cleaned_messages = [msg.replace("'", "").replace("[", "").replace("]", "") for msg in error_messages]
                internal_skript_star = f"{''.join(cleaned_messages)}"
                content_star = template_content.replace(logsHereScript, internal_skript_star)
                content_star = content_star.replace(nameOfMaschScript, machine)
                content_star = content_star.replace(errorScript, self.machineErrorStar)
                content_star = content_star.replace(categoryScript, category)

            if self.machineErrorPlus in category_errors:
                error_messages = category_errors[self.machineErrorPlus]
                cleaned_messages = [msg.replace("'", "").replace("[", "").replace("]", "") for msg in error_messages]
                internal_skript_plus = f"{''.join(cleaned_messages)}"
                content_plus = template_content.replace(logsHereScript, internal_skript_plus)
                content_plus = content_plus.replace(nameOfMaschScript, machine)
                content_plus = content_plus.replace(errorScript, self.machineErrorPlus)
                content_plus = content_plus.replace(categoryScript, category)

            if self.machineErrorF in category_errors:
                error_messages = category_errors[self.machineErrorF]
                cleaned_messages = [msg.replace("'", "").replace("[", "").replace("]", "") for msg in error_messages]
                internal_skript_f = f"{''.join(cleaned_messages)}"
                content_f = template_content.replace(logsHereScript, internal_skript_f)
                content_f = content_f.replace(nameOfMaschScript, machine)
                content_f = content_f.replace(errorScript, self.machineErrorF)
                content_f = content_f.replace(categoryScript, category)

            if self.machineRightH in category_errors:
                error_messages = category_errors[self.machineRightH]
                cleaned_messages = [msg.replace("'", "").replace("[", "").replace("]", "") for msg in error_messages]
                internal_skript_h = f"{''.join(cleaned_messages)}"
                content_h = template_content.replace(logsHereScript, internal_skript_h)
                content_h = content_h.replace(nameOfMaschScript, machine)
                content_h = content_h.replace(errorScript, self.machineRightH)
                content_h = content_h.replace(categoryScript, category)

            # Write the content to the respective files
            with open(starFilePath, "w") as f:
                f.write(content_star)

            with open(plusFilePath, "w") as f:
                f.write(content_plus)

            with open(fFilePath, "w") as f:
                f.write(content_f)

            with open(hFilePath, "w") as f:
                f.write(content_h)


    def overwriteHTMLErrorFiles(self, machine, category):
        """
        Overwrites specific HTML error files for a given machine and category with updated error logs.
        Args:
            machine (str): The name of the machine for which the error files are being overwritten.
            category (str): The category of errors to be updated in the HTML files.
        Raises:
            IOError: If the HTML file cannot be opened after multiple attempts due to being used by another process.
        This method performs the following steps:
        1. Creates the directory for error log files if it does not exist.
        2. Reads the overview of faults for the specified machine.
        3. Constructs file paths for different error categories (star, plus, f, h).
        4. For each file path, attempts to open and read the file content, retrying if the file is locked.
        5. Parses the HTML content and finds the div element with id "logs".
        6. Clears the old content in the "logs" div and inserts new error messages from the machine_errors dictionary.
        7. Saves the updated HTML content back to the file.
        Note:
            The method assumes that the error messages are stored in a dictionary structure within the readFault attribute.
        """
        
        path = "./Resources/Logfiles_Errors/"
        os.makedirs(path, exist_ok=True)
        self.readFault.readOverview(machine)
        machine_errors = self.readFault.dictMachineErrors.get(machine, {})
        file_paths = {
            "star": f"{os.getenv("ERROR_REPORTER_PATH")}\\{machine.lower()}_{category}_star.html",
            "plus": f"{os.getenv("ERROR_REPORTER_PATH")}\\{machine.lower()}_{category}_plus.html",
            "f": f"{os.getenv("ERROR_REPORTER_PATH")}\\{machine.lower()}_{category}_f.html",
            "h": f"{os.getenv("ERROR_REPORTER_PATH")}\\{machine.lower()}_{category}_h.html",
        }

        def insert_new_content(file_path, error_key):
            """
            Inserts new content into an HTML file by replacing the content of a <div> element with id "logs".
            Args:
                file_path (str): The path to the HTML file.
                error_key (str): The key to retrieve error messages from the machine_errors dictionary.
            Raises:
                IOError: If the file cannot be opened after the maximum number of retries.
            Notes:
                - The function attempts to open the file up to 5 times if it is being used by another process.
                - The function parses the HTML content using BeautifulSoup.
                - The function clears the existing content of the <div> element with id "logs" and inserts new content.
                - The new content is retrieved from the machine_errors dictionary based on the provided error_key.
            """
            max_retries = 5
            retry_delay = 1  # Sekunden
            file_content = ""
            if not os.path.exists(file_path):
                print(f"{file_path} existiert nicht.")
                return

            for attempt in range(max_retries):
                try:
                    with open(file_path, "r") as file:
                        file_content = file.read()
                    break
                except IOError as e:
                    if "being used by another process" in str(e):
                        print(f"Datei {file_path} ist gesperrt, Versuch {attempt + 1} von {max_retries}. Warte {retry_delay} Sekunden...")
                        time.sleep(retry_delay)
                    else:
                        raise
            else:
                raise IOError(f"Konnte die Datei {file_path} nach {max_retries} Versuchen nicht öffnen.")

            # HTML parsen
            soup = BeautifulSoup(file_content, 'html.parser')
            
            # Div-Element mit id "logs" finden
            logs_div = soup.find("div", {"id": "logs"})
            if logs_div:
                # Alten Inhalt entfernen
                logs_div.clear()

                # Neuen Inhalt aus dem machine_errors Dictionary einfügen
                error_messages = machine_errors.get(category, {}).get(error_key, [])
                if error_messages:
                    cleaned_messages = [msg.replace("'", "").replace("[", "").replace("]", "") for msg in error_messages]
                    logs_div.append(BeautifulSoup("".join(cleaned_messages), 'html.parser'))
                # Änderungen speichern
                with open(file_path, "w") as file:
                    file.write(str(soup))

        # Dateien überschreiben
        insert_new_content(file_paths["star"], '.*.')
        insert_new_content(file_paths["plus"], '.+.')
        insert_new_content(file_paths["f"], '.F.')
        insert_new_content(file_paths["h"], '.H.')

        print("Files overridden")
                
                
    def modifyHTMLFile(self, machine, category, getCurrentTCNumber, tcNumberReadOut, new_progress=None, error=None):
        """
        Modifies an HTML file to update progress, error information, and other data visualizations for a given machine and category.
        Args:
            machine (str): The name of the machine for which the HTML file is being modified.
            category (str): The category of data being processed.
            getCurrentTCNumber (int): The current test case number.
            tcNumberReadOut (int): The total number of test cases read out.
            new_progress (float, optional): The new progress value to be updated in the HTML file. Defaults to None.
            error (str, optional): Error message to be displayed in the HTML file. Defaults to None.
        Returns:
            None
        """
        randomStringProgressbar = self.getRandomStringForCategory(category, "randomStringProgressbar")
        randomStringChartdiagram = self.getRandomStringForCategory(category, "randomStringChartdiagram")

        # Debugging-Ausgaben hinzufügen
        print(f"Modifying HTML file for machine: {machine}, category: {category}")
        print(f"Current TC Number: {getCurrentTCNumber}, TC Number Read Out: {tcNumberReadOut}")
        print(f"New Progress: {new_progress}, Error: {error}")

        # Auslesen der Übersicht
        self.readFault.readOverview(machine)
        
        modul = self.readFault.getCurrentVersionMachine(machine, modulOption=True)

        # Auslesen der Kategorien in je modul / qtp_test.ini
        self.readCategoriesQTP.getCategories(machine, modul)

        # Sammeln aller Fehler und absichern in self.dictOFMachines
        for pattern in self.readFault.errorList:
            self.readFault.getErrorsForPattern(machine, category, pattern)
            self.collectDataForHTML(machine, category)
            self.createHTMLErrorFiles(machine, category)

        data_dict = self.dictOfMachines.get(machine, {}).get(category, {})
        
        internal_stardata = data_dict.get(".*.", 0)
        internal_plusdata = data_dict.get(".+.", 0)
        internal_fdata = data_dict.get(".F.", 0)
        internal_hdata = data_dict.get(".H.", 0)

        # Öffne die Datei zum Lesen
        with open(f"{os.getenv("REPORTER_PATH")}" + "\\" + f"{machine + self.reporterHTML}", "r") as f:
            template_content = f.read()

        # Muster für die zu ersetzenden Zeilen
        patternProgress = re.compile(rf"{{id:'{re.escape(randomStringProgressbar)}',\s*progress:\s*\d+(\.\d+)?\s*}}")

        anchorPattern = rf"<!-- START DATA BLOCK FOR: {machine}_{category}-->\s*.*?\s*<!-- END DATA BLOCK FOR: {machine}_{category}-->"
        spanPattern = rf"<!-- START DATA SPAN CLASS: {machine}_{category}-->\s*.*?\s*<!-- END DATA SPAN CLASS: {machine}_{category}-->"
        infoLastChange = rf"<!-- Start infoLastChange -->s*.*?\s*<!-- End infoLastChange -->"

        dataAddRowsPattern = re.compile(anchorPattern, re.DOTALL)
        dataSpanRowsPattern = re.compile(spanPattern, re.DOTALL)
        dataInfoLastChangePattern = re.compile(infoLastChange, re.DOTALL)

        # Neue Zeilen, die eingefügt werden sollen
        newProgressbarLine = f"{{id:'{randomStringProgressbar}', progress: {new_progress}}}"
        
        colors = "['#FF0000', '#0000FF', '#DA70D6', '#32CD32']" if data_dict else "['#D3D3D3']"  # Grau wenn keine Daten
        
        now = dt.datetime.now()
        newInfoLastChange = (
            "<!-- Start infoLastChange -->\n"
            f"<p id = 'infoLastChange'>Letzte Änderung: {now.strftime('%d.%m.%y - %H:%M')} - {category}</p>\n"
            "<!-- End infoLastChange -->\n")

        newDataAddRows = (
            f"<!-- START DATA BLOCK FOR: {machine}_{category}-->\n"
            "//I WAS CHANGED\n"
            f"google.charts.setOnLoadCallback({self.getRandomStringForCategory(category, 'randomStringFunction')});\n"
            f"function {self.getRandomStringForCategory(category, 'randomStringFunction')}() {{\n"
            "var data = new google.visualization.DataTable();\n"
            "data.addColumn('string', 'Fehlercode');\n"
            "data.addColumn('number', 'Anzahl');\n"
            "data.addRows([\n"
            f"['.*.', {internal_stardata}],\n"
            f"['.+.', {internal_plusdata}],\n"
            f"['.F.', {internal_fdata}],\n"
            f"['.H.', {internal_hdata}],\n"
            "]);\n"
            "var settings = {\n"
            f"title: '{machine} - {category} Überblick',\n"
            f"colors: {colors},\n"
            "titleTextStyle: { fontSize: 18, bold: true },\n"
            "legend: { position: 'right', textStyle: { fontSize: 16, bold: true } },\n"
            "chartArea: { width: '80%', height: '70%' },\n"
            "pieSliceTextStyle: { fontSize: 14 },\n"
            "};\n"
            f"var chart = new google.visualization.PieChart(document.getElementById('{self.getRandomStringForCategory(category, 'randomStringChartdiagram')}'));\n"
            "chart.draw(data, settings);\n"
            "google.visualization.events.addListener(chart, 'select', function() {\n"
            "var selectedItem = chart.getSelection()[0];\n"
            "if (selectedItem) {\n"
            "var topping = data.getValue(selectedItem.row, 0);\n"
            "var url;\n"
            f"if (topping === '.*.') {{ url = './Logfiles_Errors/{machine}_{category}_star.html'; }}\n"
            f"else if (topping === '.+.') {{ url = './Logfiles_Errors/{machine}_{category}_plus.html'; }}\n"
            f"else if (topping === '.F.') {{ url = './Logfiles_Errors/{machine}_{category}_f.html'; }}\n"
            f"else if (topping === '.H.') {{ url = './Logfiles_Errors/{machine}_{category}_h.html'; }}\n"
            "window.open(url, '_blank');\n"
            "}\n"
            "});\n"
            "}\n"
            f"<!-- END DATA BLOCK FOR: {machine}_{category}-->\n"
        )
        
        newSpanAddRow = (
            f"<!-- START DATA SPAN CLASS: {machine}_{category}-->\n"
            "<td style='border: 1px solid #00772c;'>\n"
            f"<div id={randomStringChartdiagram} style='width: 400px; height: 300px;'></div>\n"
            "<div class='current-state'>\n"
            f"<span class='current-state-digit'>Testfall: {getCurrentTCNumber} von {tcNumberReadOut} </span>\n"
            "</div>\n"
            f"{self.getProgressBar(randomStringProgressbar)}</td>\n"
            f"<!-- END DATA SPAN CLASS: {machine}_{category}-->\n"
        )
        newError = (
            f"<!-- START DATA SPAN CLASS: {machine}_{category}-->\n"
            "<td style='border: 1px solid #00772c;'>\n"
            f"<div id={randomStringChartdiagram} style='width: 400px; height: 300px;'></div>\n"
            "<div class='current-state'>\n"
            f"<span class='current-state-digit'>{error}</span>\n"
            "</div>\n"
            f"{self.getProgressBar(randomStringProgressbar)}</td>\n"
            f"<!-- END DATA SPAN CLASS: {machine}_{category}-->\n"
        )

        # Führe die Ersetzungen durch
        modified_content = patternProgress.sub(newProgressbarLine, template_content)
        modified_content = dataAddRowsPattern.sub(newDataAddRows, modified_content)
        modified_content = dataSpanRowsPattern.sub(newSpanAddRow, modified_content)
        modified_content = dataInfoLastChangePattern.sub(newInfoLastChange, modified_content)

        if error != None:
            modified_content = dataSpanRowsPattern.sub(newError,modified_content)
        # Schreibe den geänderten Inhalt zurück zur Datei
        with open(f"{os.getenv("REPORTER_PATH")}" + "\\" + f"{machine + self.reporterHTML}", "w") as f:
            f.write(modified_content)


    def overrideFiles(self, masch, category, overviewPath, tcNumberReadOut):
        """
        Override files and update HTML based on the current and read-out test case numbers.
        Args:
            masch (str): The machine identifier.
            category (str): The category of the test.
            overviewPath (str): The path to the overview file.
            tcNumberReadOut (int): The read-out test case number.
        Returns:
            None
        """
        print(f"Override files for machine: {masch}, category: {category},\noverviewPath: {overviewPath}, tcNumberReadOut: {tcNumberReadOut}")

        getCurrentTCNumber = self.readCountedTestcase.extractLastTestcaseNumber(overviewPath, masch,tcNumberReadOut)
        if getCurrentTCNumber == None:
            while True:
                getCurrentTCNumber = self.readCountedTestcase.extractLastTestcaseNumber(overviewPath, masch, tcNumberReadOut)
                if getCurrentTCNumber != None:
                    break


        if tcNumberReadOut != 0 and getCurrentTCNumber != 0:
            difference = getCurrentTCNumber / tcNumberReadOut * 100
            rounded_difference = round(difference)
            self.modifyHTMLFile(masch, category, getCurrentTCNumber, tcNumberReadOut,new_progress=rounded_difference)

        elif tcNumberReadOut != 0 and getCurrentTCNumber == 0:
            difference = "Noch nicht gestartet"
            progress = 0
            self.modifyHTMLFile(masch, category, getCurrentTCNumber, tcNumberReadOut,new_progress=progress, error=difference)
            self.overwriteHTMLErrorFiles(masch, category)
            return

        elif tcNumberReadOut == 0 and getCurrentTCNumber == 0:
            difference = "Fehler beim lesen der Datenbank/QTP_Test.ini"
            self.modifyHTMLFile(masch, category, getCurrentTCNumber, tcNumberReadOut,error=difference)
            self.overwriteHTMLErrorFiles(masch, category)
            return
        else:
            difference = "Irgendwas ist schief gelaufen"
            self.modifyHTMLFile(masch, category, getCurrentTCNumber, tcNumberReadOut,error=difference)
            self.overwriteHTMLErrorFiles(masch, category)
            return

        self.modifyHTMLFile(masch, category, getCurrentTCNumber, tcNumberReadOut,new_progress=rounded_difference)
        self.overwriteHTMLErrorFiles(masch, category)


    def getRandom(self, N):
        """
        Generate a random string of specified length.

        This method generates a random string consisting of uppercase ASCII letters
        and digits. The length of the generated string is determined by the input parameter N.

        Args:
            N (int): The length of the random string to generate.

        Returns:
            str: A random string of length N containing uppercase ASCII letters and digits.
        """
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))




    ##################################################################
    # Monitoring each category in a separate thread, which is choice #
    ##################################################################
    def monitorSystemLog(self, masch):
        """
        Monitors the system log for a given machine.
        This method retrieves the current version of the machine module and its categories,
        then starts a separate thread to continuously monitor the system log.
        Args:
            masch (str): The identifier for the machine to monitor.
        """
        try:
            modul = self.readFault.getCurrentVersionMachine(masch, modulOption=True)
            categories = self.readCategoriesQTP.categories[masch][modul]


            # Start the loop in a separate thread
            monitor_thread = threading.Thread(target=self.monitorLoop, args=(masch, modul, categories), daemon=True)
            monitor_thread.start()
        except Exception as e:
            print(f"Error monitoring system log for machine {masch}: {e}")

    def monitorLoop(self, masch, modul, categories):
        """
        Monitors the status of a machine and processes test cases for given categories.
        Args:
            masch (str): The machine identifier.
            modul (str): The module identifier.
            categories (list): A list of categories to process.
        Description:
            This method continuously checks the status of the specified machine (`masch`). 
            For each category in the `categories` list, it performs the following steps:
            - If the machine is free, it overrides files for the current category.
            - It retrieves the test case number for the given module and category.
            - It overrides the necessary files.
            - It checks if all test cases for the current category are completed.
            - If all test cases are completed, it breaks out of the loop for the current category.
            - If not, it waits for a short period before checking again.
            - If the machine is not free, it waits for a longer period before checking again.
        Note:
            The method relies on several instance methods and attributes:
            - `self.stop_event.is_set()`: Checks if the stop event is set.
            - `self.readTimeControll.getCurrentStatus(masch)`: Checks the current status of the machine.
            - `self.readFault.getVersionPath(masch)`: Retrieves the version path for the machine.
            - `self.tcAnalyzer.getTestCaseNumberCategory(modul, category)`: Retrieves the test case number for the module and category.
            - `self.overrideFiles(masch, category, overview_path, tcNumberReadOut)`: Overrides the necessary files.
            - `self.readCountedTestcase.allTestCasesCompleted(masch, overview_path, tcNumberReadOut)`: Checks if all test cases are completed.
        """
        for category in categories:
            while not self.stop_event.is_set():
                if self.readTimeControll.getCurrentStatus(masch):
                    print(f"{masch} is free. Overriding files for category: {category}...")
                    overview_path = os.path.join(self.readFault.getVersionPath(masch), category, "uebersicht.txt")
                    tcNumberReadOut = self.tcAnalyzer.getTestCaseNumberCategory(modul, category)
                    self.overrideFiles(masch, category, overview_path, tcNumberReadOut)

                    # Check if all test cases are completed
                    if self.readCountedTestcase.allTestCasesCompleted(masch, overview_path, tcNumberReadOut):
                        break  # Exit the loop once all test cases for the current category are completed
                    else:
                        time.sleep(2)  # Wait for 5 seconds before checking again
                else:
                    print(f"{masch} is not free. Waiting...")
                    time.sleep(5)  # Wait for 2 second before checking again

    def setupInitialWatcher(self, masch, modul, categories):
        """
        Start the initial watcher for the first category that is found in the log.

        Args:
            masch (str): The machine identifier.
            modul (str): The module identifier.
            categories (list): A list of categories to check in the log.

        Returns:
            None
        """
        for category in categories:
            if self.doesLogContainCategory(masch, category):
                self.startNewWatch(masch, modul, category)
                self.current_category = category
                break


    def doesLogContainCategory(self, masch, category):
        """
        Checks if the system log file on a remote machine contains a specific category.
        Args:
            masch (str): The name or IP address of the remote machine.
            category (str): The category to search for in the system log.
        Returns:
            bool: True if the category is found in the system log, False otherwise.
        Raises:
            Exception: If there is an error accessing or reading the system log file.
        Notes:
            - This method uses `self.networkShare.openFileVMUser` to open the file on the remote machine.
        """
        systemlogPath = os.getenv("MACHINE_SYSTEMLOG_PATH")
        if not os.path.isfile(systemlogPath):
            print(f"System log file {systemlogPath} does not exist.")
            return False
        try:
            with self.networkShare.openFileVMUser(systemlogPath,masch,"r") as file:
                for line in file:
                    if category in line:
                        print(f"Found category {category} in system log.")
                        return True
            return False

        except Exception as e:
            print(f"Error: {e}")


    def startNewWatch(self, masch, modul, category):
        """
        Starts a new file watcher for the given machine, module, and category.
        If a watcher for the specified category already exists, it stops the existing watcher
        before starting a new one. It then retrieves the test case number for the given module
        and category, and checks if the overview file exists. If the overview file does not exist,
        it modifies the HTML file accordingly. Finally, it creates and starts a new file watcher
        for the overview file.
        Args:
            masch (str): The machine identifier.
            modul (str): The module identifier.
            category (str): The category for which the file watcher is to be started.
        Raises:
            Any exceptions raised by the underlying methods such as `getTestCaseNumberCategory`,
            `getVersionPath`, `modifyHTMLFile`, or the `FileWatcher` class.
        """
        if category in self.file_watchers:
            self.file_watchers[category].stop()

        print(f"Starting watch for category: {category}")
        tcNumberReadOut = self.tcAnalyzer.getTestCaseNumberCategory(modul, category)
        overview_path = os.path.join(self.readFault.getVersionPath(masch), category, "uebersicht.txt")

        if not os.path.isfile(overview_path):
            self.modifyHTMLFile(masch, category, 0, 0, tcNumberReadOut)

        if os.path.isfile(overview_path):
            file_watcher = FileWatcher(
                overview_path,
                self.overrideFiles,
                masch,
                category,
                overview_path,
                tcNumberReadOut
            )
            self.file_watchers[category] = file_watcher
            file_watcher.start()

    def continuousMonitor(self, masch, modul, categories):
        """
        Continuously monitors the log for new categories and starts a new watch if a new category is found.

        Args:
            masch (str): The machine identifier.
            modul (str): The module identifier.
            categories (list): A list of categories to monitor.

        Returns:
            None
        """
        while True:
            for category in categories:
                if category not in self.found_categories and self.doesLogContainCategory(masch, category):
                    self.startNewWatch(masch, modul, category)
                    self.found_categories.add(category)  # Add category to found_categories
            time.sleep(30)  # Check every 30 seconds for new categories

    def openHTMLDataWithWatchdog(self, machine):
        """
        Generates HTML files for the specified machine, opens the HTML report in a web browser,
        and monitors the system log for the machine.

        Args:
            machine (str): The identifier for the machine for which the HTML report is generated.

        Returns:
            None
        """
        self.generateHTMLFilesforMachine(machine)
        cwd = os.path.dirname(os.path.abspath(sys.argv[0]))
        drivePath = f"{os.getenv("REPORTER_PATH")}" + "\\" + f"{machine + self.reporterHTML}"
        webbrowser.open(f"{os.getenv("REPORTER_PATH")}" + "\\" + f"{machine + self.reporterHTML}")
        self.monitorSystemLog(machine)


    def close(self):
        """
        Closes the current file watcher if it is active.

        This method stops the file watcher associated with the current instance,
        if it exists, and prints a message indicating that the monitoring has stopped.
        """
        if self.current_file_watcher:
            self.current_file_watcher.stop()
        print("Überwachung gestoppt.")